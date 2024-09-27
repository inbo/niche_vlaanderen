import numpy as np
import pandas as pd

from niche_vlaanderen.codetables import (validate_tables_nutrient_level,
                                         check_codes_used, package_resource)


class NutrientLevel(object):
    """
    Class to calculate the NutrientLevel

    The used codetables can be overwritten by using the corresponding ct_*
    arguments.
    """

    nodata = 255  # unsigned 8 bit type is used

    def __init__(
        self,
        ct_lnk_soil_nutrient_level=None,
        ct_management=None,
        ct_mineralisation=None,
        ct_soil_code=None,
        ct_nutrient_level=None,
    ):
        if ct_lnk_soil_nutrient_level is None:
            ct_lnk_soil_nutrient_level = package_resource(
                ["system_tables"], "lnk_soil_nutrient_level.csv")
        if ct_management is None:
            ct_management = package_resource(
                ["system_tables"], "management.csv")
        if ct_mineralisation is None:
            ct_mineralisation = package_resource(
                ["system_tables"], "nitrogen_mineralisation.csv")
        if ct_soil_code is None:
            ct_soil_code = package_resource(
                ["system_tables"], "soil_codes.csv")
        if ct_nutrient_level is None:
            ct_nutrient_level = package_resource(
                ["system_tables"], "nutrient_level.csv")

        self.ct_lnk_soil_nutrient_level = pd.read_csv(ct_lnk_soil_nutrient_level)
        self._ct_management = pd.read_csv(ct_management)
        self._ct_mineralisation = pd.read_csv(ct_mineralisation)
        self._ct_nutrient_level = pd.read_csv(ct_nutrient_level)
        self._ct_soil_code = pd.read_csv(ct_soil_code)

        # convert the mineralisation system table to float to use np.nan for nodata
        self._ct_mineralisation["nitrogen_mineralisation"] = self._ct_mineralisation[
            "nitrogen_mineralisation"
        ].astype("float64")

        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])
        validate_tables_nutrient_level(
            self.ct_lnk_soil_nutrient_level,
            self._ct_management,
            self._ct_mineralisation,
            self._ct_soil_code,
            self._ct_nutrient_level,
            inner=inner,
        )

        # join soil_code to soil_name where needed
        self._ct_soil_code = pd.read_csv(ct_soil_code).set_index("soil_name")
        self._ct_mineralisation["soil_code"] = (
            self._ct_soil_code.soil_code[self._ct_mineralisation["soil_name"]]
            .reset_index()
            .soil_code
        )
        self.ct_lnk_soil_nutrient_level["soil_code"] = (
            self._ct_soil_code.soil_code[self.ct_lnk_soil_nutrient_level["soil_name"]]
            .reset_index()
            .soil_code
        )

    def _calculate_mineralisation(self, soil_code_array, msw_array):
        """
        Get nitrogen mineralisation for numpy arrays
        """
        orig_shape = soil_code_array.shape
        soil_code_array = soil_code_array.flatten()
        msw_array = msw_array.flatten()
        result = np.empty(soil_code_array.shape, dtype="float32")
        result[:] = np.nan

        for code in self._ct_mineralisation.soil_code.unique():
            # We must reset the index because digitize will give indexes
            # compared to the new table.
            select = self._ct_mineralisation.soil_code == code
            table_sel = self._ct_mineralisation[select].copy()
            table_sel = table_sel.reset_index(drop=True)
            soil_sel = soil_code_array == code
            ix = np.digitize(msw_array[soil_sel], table_sel.msw_max, right=False)
            result[soil_sel] = table_sel["nitrogen_mineralisation"].reindex(ix)

        result = result.reshape(orig_shape)
        # Reuse the mask of the msw_array
        result = np.ma.array(result, mask=msw_array.mask, fill_value=np.nan)
        return result

    def _calculate(self, management, soil_code, nitrogen, inundation):
        """
        Calculates the nutrient level using previously calculated nitrogen
        """
        check_codes_used("management", management, self._ct_management["management"])
        check_codes_used("soil_code", soil_code, self._ct_soil_code["soil_code"])

        # calculate management influence
        influence = np.ma.empty_like(management)
        for i in self._ct_management.management.unique():
            sel_grid = management == i
            sel_ct = self._ct_management.management == i
            influence[sel_grid] = self._ct_management[sel_ct].influence.values[0]

        # flatten all input layers (necessary for digitize)
        orig_shape = soil_code.shape
        soil_code = soil_code.flatten()
        nitrogen = nitrogen.flatten()

        inundation = inundation.flatten()
        influence = influence.flatten()

        result = influence
        # search for classification values in nutrient level codetable
        for name, subtable in self.ct_lnk_soil_nutrient_level.groupby(
            ["soil_code", "influence"]
        ):

            soil_selected, influence_selected = name
            table_sel = subtable.copy(deep=True).reset_index(drop=True)

            index = np.digitize(nitrogen, table_sel.total_nitrogen_max, right=True)
            index = np.ma.array(index, mask=nitrogen.mask, fill_value=self.nodata).filled()
            selection = (soil_code == soil_selected) & (influence == influence_selected)
            # Add the no-data value to the mapping
            table_sel.loc[self.nodata, "nutrient_level"] = self.nodata
            result[selection] = table_sel.nutrient_level[index].iloc[selection].values

        # np.nan values are not ignored in np.digitize
        #result[np.isnan(nitrogen)] = self.nodata
        result = np.ma.array(result, mask=nitrogen.mask, fill_value=self.nodata)

        # Note that niche_vlaanderen is different from the original (Dutch)
        # model here:
        # only if nutrient_level < 4 the inundation rule is applied.
        result[result < 4] = (result + (inundation > 0))[result < 4]
        result = result.reshape(orig_shape)
        return result

    def calculate(
        self,
        soil_code,
        msw,
        nitrogen_atmospheric,
        nitrogen_animal,
        nitrogen_fertilizer,
        management,
        inundation,
    ):
        """Calculates the nutrient level based on the input arrays provided

        Parameters
        ----------
        soil_code : numpy.ma.MaskedArray
            Array containing the soil codes. Values must be present
            in the soil_code table.
        msw : numpy.ma.MaskedArray
            Array containing the mean spring waterlevel.
        nitrogen_atmospheric : numpy.ma.MaskedArray
            Array containing the atmospheric deposition of Nitrogen.
        nitrogen_animal : numpy.ma.MaskedArray
            Array containing the animal contribution of Nitrogen.
        nitrogen_fertilizer : numpy.ma.MaskedArray
            Array containing the fertilizer contribution of Nitrogen.
        management : numpy.ma.MaskedArray
            Array containing the management.
        inundation : numpy.ma.MaskedArray
            Array containing the inundation values.

        """

        nitrogen_mineralisation = self._calculate_mineralisation(soil_code, msw)
        total_nitrogen = (
            nitrogen_mineralisation
            + nitrogen_atmospheric
            + nitrogen_animal
            + nitrogen_fertilizer
        )
        nutrient_level = self._calculate(
            management, soil_code, total_nitrogen, inundation
        )
        return nutrient_level
