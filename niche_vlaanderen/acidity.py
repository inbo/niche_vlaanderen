import numpy as np
import pandas as pd

from niche_vlaanderen.codetables import package_resource
from niche_vlaanderen.codetables import validate_tables_acidity, check_codes_used


class Acidity(object):
    """Calculate the Acidity

    The used codetables can be overwritten by using the corresponding ct_*
    arguments.
    """

    nodata = 255  # unsigned 8 bit integer for acidity

    def __init__(
        self,
        ct_acidity=None,
        ct_soil_mlw_class=None,
        ct_soil_code=None,
        lnk_acidity=None,
        ct_seepage=None,
    ):
        """Create an acidity calculator

        Parameters
        ----------
        ct_acidity : str, Optional
            Path to the acidity system table to overwrite the default.
        ct_soil_mlw_class : str, Optional
            Path to the soil_mlw_class system table to overwrite the default.
        ct_soil_code : str, Optional
            Path to the soil_code system table to overwrite the default.
        lnk_acidity : str, Optional
            Path to the lnk_acidity system table to overwrite the default.
        ct_seepage : str, Optional
            Path to the seepage system table to overwrite the default.
        """

        if ct_acidity is None:
            ct_acidity = package_resource(
                ["system_tables"], "acidity.csv")
        if ct_soil_mlw_class is None:
            ct_soil_mlw_class = package_resource(
                ["system_tables"], "soil_mlw_class.csv")
        if ct_soil_code is None:
            ct_soil_code = package_resource(
                ["system_tables"], "soil_codes.csv")
        if lnk_acidity is None:
            lnk_acidity = package_resource(
                ["system_tables"], "lnk_acidity.csv")
        if ct_seepage is None:
            ct_seepage = package_resource(
                ["system_tables"], "seepage.csv")

        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_soil_mlw = pd.read_csv(ct_soil_mlw_class)
        self._ct_soil_codes = pd.read_csv(ct_soil_code)
        self._lnk_acidity = pd.read_csv(lnk_acidity)
        self._ct_seepage = pd.read_csv(ct_seepage)

        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])

        validate_tables_acidity(
            ct_acidity=self._ct_acidity,
            ct_soil_mlw_class=self._ct_soil_mlw,
            ct_soil_codes=self._ct_soil_codes,
            lnk_acidity=self._lnk_acidity,
            ct_seepage=self._ct_seepage,
            inner=inner,
        )

        self._ct_soil_codes = self._ct_soil_codes.set_index("soil_code")

    def _calculate_soil_mlw(self, soil_code, mlw):
        """Calculate the soild mlw classes

        Parameters
        ----------
        soil_code : numpy.ma.MaskedArray
            Array containing the soil codes. Values must be present
            in the soil_code system table.
        mlw : numpy.ma.MaskedArray
            Array containing the mean low waterlevel.

        Returns
        -------
        numpy.ma.MaskedArray, uint8
            Array containing the soil_mlw class values.
        """
        check_codes_used("soil_code", soil_code, self._ct_soil_codes.index)

        # determine soil_group for soil_code
        orig_shape = mlw.shape
        soil_code = soil_code.flatten()
        mlw = mlw.flatten()

        self._ct_soil_codes.loc[self.nodata, "soil_group"] = self.nodata
        # use filled to represent no-data values correctly
        soil_group = self._ct_soil_codes.soil_group[
            soil_code.filled(fill_value=self.nodata)].values.astype("uint8")

        result = np.ma.empty_like(soil_code)
        for sel_group, subtable in self._ct_soil_mlw.groupby("soil_group"):
            subtable = subtable.copy().reset_index(drop=True)
            index = np.digitize(mlw, subtable.mlw_max, right=False)
            index = np.ma.array(index, mask=mlw.mask,
                                fill_value=self.nodata).filled()
            selection = soil_group == sel_group
            subtable.loc[self.nodata, "soil_mlw_class"] = self.nodata
            result[selection] = subtable.soil_mlw_class[index].iloc[selection].values
        result = result.reshape(orig_shape)
        # Set mask values to default no-data value
        result = np.ma.masked_array(result.filled(self.nodata), mask=mlw.mask,
                                    fill_value=self.nodata, dtype="uint8")
        return result

    def _get_acidity(self, rainwater, minerality, inundation, seepage, soil_mlw_class):
        """Calculate the acidity

        Parameters
        ----------
        rainwater : numpy.ma.MaskedArray
            Array denoting whether rainwater lenses occur.
        minerality : numpy.ma.MaskedArray
            Array noting whether the groundwater is rich(1) or poor in minerals
        inundation : numpy.ma.MaskedArray
            Array containing rate of inundation.
        seepage : numpy.ma.MaskedArray
            Array containing the flux of groundwater at the location.
        soil_mlw_class : numpy.ma.MaskedArray
            Array containing the soil mlw classes from helper function.

        Returns
        -------
        numpy.ma.MaskedArray, uint8
            Array containing the acidity values.
        """
        orig_shape = inundation.shape

        check_codes_used("rainwater", rainwater, {0, 1})
        check_codes_used(
            "minerality", minerality, self._lnk_acidity["mineral_richness"]
        )
        check_codes_used("inundation", inundation, self._lnk_acidity["inundation"])
        check_codes_used("seepage", seepage, self._ct_seepage["seepage"])

        rainwater = rainwater.flatten()
        minerality = minerality.flatten()
        inundation = inundation.flatten()
        seepage = seepage.flatten()
        soil_mlw_class = soil_mlw_class.flatten()

        result = np.empty_like(soil_mlw_class)

        for labels, subtable in self._lnk_acidity.groupby(
            ["rainwater", "mineral_richness", "inundation", "seepage", "soil_mlw_class"]
        ):
            (
                sel_rainwater,
                sel_mr,
                sel_inundation,
                sel_seepage,
                sel_soil_mlw_class,
            ) = labels
            subtable = subtable.copy().reset_index(drop=True)

            selection = (
                (rainwater == sel_rainwater)
                & (minerality == sel_mr)
                & (inundation == sel_inundation)
                & (seepage == sel_seepage)
                & (soil_mlw_class == sel_soil_mlw_class)
            )
            result[selection] = subtable.acidity[0]

        result = result.reshape(orig_shape)
        # Set mask values to default no-data value
        result = np.ma.masked_array(result.filled(self.nodata),
                                    mask=soil_mlw_class.mask,
                                    fill_value=self.nodata,
                                    dtype="uint8")
        return result

    def _get_seepage(self, seepage):
        """Classify seepage values into seepage classes

        Parameters
        ----------
        seepage : numpy.ma.MaskedArray
            Seepage array

        Returns
        -------
        numpy.ma.MaskedArray, uint8
            Seepage class array
        """
        orig_shape = seepage.shape
        seepage = seepage.flatten()

        index = np.digitize(seepage, self._ct_seepage.seepage_max, right=True)
        index = np.ma.array(index, mask=seepage.mask, fill_value=self.nodata).filled()

        self._ct_seepage.loc[self.nodata, "seepage"] = self.nodata
        seepage_class = self._ct_seepage["seepage"][index]
        seepage_class = seepage_class.values.reshape(orig_shape)
        return np.ma.masked_array(seepage_class,
                                  mask=seepage.mask,
                                  fill_value=self.nodata,
                                  dtype="uint8")

    def calculate(self, soil_class, mlw, inundation, seepage, minerality, rainwater):
        """Calculate the Acidity

        Parameters
        ----------
        soil_class: numpy.ma.MaskedArray
            Array containing the soil codes. Values must be present
            in the soil_code table. -99 is used as no data value.
        mlw: numpy.array
            Array containing the mean lowest waterlevel.
        inundation:  numpy.ma.MaskedArray
            Array containing rate of inundation.
            https://inbo.github.io/niche_vlaanderen/invoer.html#overstroming-trofie-inundation-nutrient
        seepage:  numpy.ma.MaskedArray
            Array containing the flux of groundwater at the location
            https://inbo.github.io/niche_vlaanderen/invoer.html#overstroming-trofie-inundation-nutrient
        minerality: numpy.ma.MaskedArray
            Array noting whether the groundwater is rich(1) or poor in minerals
            https://inbo.github.io/niche_vlaanderen/invoer.html#mineraalrijkdom-minerality
        rainwater: numpy.ma.MaskedArray
            Array denoting whether rainwater lenses occur.
            https://inbo.github.io/niche_vlaanderen/invoer.html#regenlens-rainwater

        Returns
        -------
        numpy.ma.MaskedArray, uint8
            acidity
        """
        soil_mlw = self._calculate_soil_mlw(soil_class, mlw)
        seepage = self._get_seepage(seepage)
        acidity = self._get_acidity(
            rainwater, minerality, inundation, seepage, soil_mlw
        )
        return acidity
