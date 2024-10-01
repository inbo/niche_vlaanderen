from __future__ import division
from enum import IntEnum
import warnings

import numpy as np
import pandas as pd

from niche_vlaanderen.nutrient_level import NutrientLevel
from niche_vlaanderen.acidity import Acidity
from niche_vlaanderen.codetables import (validate_tables_vegetation,
                                         check_codes_used, package_resource)
from niche_vlaanderen.exception import NicheException


class VegSuitable(IntEnum):
    SOIL = 1
    MXW = 2
    NUTRIENT = 4
    ACIDITY = 8
    MANAGEMENT = 16
    FLOODING = 32

    @staticmethod
    def possible():
        """Possible legend items

        Due to the way niche works, only certain combinations are possible,
        eg soil is checked first, so it is impossible to have suitable management
        and unsuitable soil conditions.
        """

        return [0, 1, 3, 7, 11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63]

    @staticmethod
    def legend():
        """Returns a dict with key number + text = legend text"""
        legend = {}
        for i in range(64):
            legend_items = []
            for j in list(map(int, VegSuitable)):
                if i & j == j:
                    legend_items += [VegSuitable(i & j).name.lower()]
            legend[i] = "+".join(legend_items) + " suitable"
        legend[0] = "soil unsuitable"

        # only select possible combinations for legend
        sel = VegSuitable.possible()
        return {i: legend[i] for i in sel}


class Vegetation(object):
    """Calculate vegetation based on input arrays

    This class helps predicting vegetation based on a number of input arrays.
    On initialization the input codetables are parsed (and validated).

    Note that to use grid inputs (eg raster files) it is recommended to use
    the Niche Class

    Parameters
    ----------
    ct_vegetation: filename, .csv
        optional alternative classification table
        Must contain the columns mentioned in the documentation:
        https://inbo.github.io/niche_vlaanderen/codetables.html
    """

    nodata_veg = 255  # unsigned 8 bit integer for vegetation

    def __init__(
        self,
        ct_vegetation=None,
        ct_soil_code=None,
        ct_acidity=None,
        ct_management=None,
        ct_nutrient_level=None,
        ct_inundation=None,
    ):
        """Create a Vegetation helper class

        This class initializes the Vegetation helper class. By default it uses
        the code tables supplied by the niche_vlaanderen package. It is
        possible to overwrite this by supplying the niche_vlaanderen parameter
        """

        if ct_vegetation is None:
            ct_vegetation = package_resource(["system_tables"],
                                             "niche_vegetation.csv")

        # Note that the next code tables are only used for validation, they are
        # not part of the logic of the vegetation class
        if ct_soil_code is None:
            ct_soil_code = package_resource(["system_tables"],
                                             "soil_codes.csv")
        if ct_acidity is None:
            ct_acidity = package_resource(["system_tables"],
                                             "acidity.csv")
        if ct_nutrient_level is None:
            ct_nutrient_level = package_resource(["system_tables"],
                                                 "nutrient_level.csv")
        if ct_management is None:
            ct_management = package_resource(["system_tables"],
                                                 "management.csv")
        if ct_inundation is None:
            ct_inundation = package_resource(["system_tables"],
                                             "inundation.csv")

        self._ct_vegetation = pd.read_csv(ct_vegetation)
        self._ct_soil_code = pd.read_csv(ct_soil_code)
        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_nutrient_level = pd.read_csv(ct_nutrient_level)
        self._ct_management = pd.read_csv(ct_management)
        self._ct_inundation = pd.read_csv(ct_inundation)

        # we check for inner joins if codetables are not overwritten
        # https://github.com/inbo/niche_vlaanderen/issues/106
        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])

        validate_tables_vegetation(
            ct_vegetation=self._ct_vegetation,
            ct_soil_code=self._ct_soil_code,
            ct_acidity=self._ct_acidity,
            ct_management=self._ct_management,
            ct_nutrient_level=self._ct_nutrient_level,
            ct_inundation=self._ct_inundation,
            inner=inner,
        )

        # join soil_code to soil_name where needed
        self._ct_soil_code = self._ct_soil_code.set_index("soil_name")
        self._ct_vegetation["soil_code"] = (
            self._ct_soil_code.soil_code[self._ct_vegetation["soil_name"]]
            .reset_index()
            .soil_code
        )

    def calculate(
        self,
        soil_code,
        mhw,
        mlw,
        nutrient_level=None,
        acidity=None,
        management=None,
        inundation=None,
        return_all=True,
        full_model=True,
    ):
        """Calculate vegetation types based on input arrays

        Parameters
        ----------
        soil_code : numpy.ma.MaskedArray
            Array containing the soil codes. Values must be present
            in the soil_code system table.
        mhw : numpy.ma.MaskedArray
            Array containing the mean high waterlevel.
        mlw : numpy.ma.MaskedArray
            Array containing the mean low waterlevel.
        nutrient_level : numpy.ma.MaskedArray, optional
            Array containing the nutrient levels. Values must be present
            in the nutrient_level system table.
        acidity : numpy.ma.MaskedArray, optional
            Array containing the acidity levels. Values must be present
            in the acidity system table.
        management : numpy.ma.MaskedArray
            Array containing the management codes. Values must be present
            in the management system table.
        inundation : numpy.ma.MaskedArray
            Array containing the inundation values.
        return_all: boolean
            A boolean (default=True) whether all grids should be returned or
            only grids containing data.
        full_model : bool
            If True, the full niche model is applied

        Returns
        -------
        veg: dict
            A dictionary containing the different output arrays per veg_code value.
        expected: int
            Expected code in veg arrays if all conditions are met
        veg_occurrence: dict
            A dictionary containing the percentage of the area where the
            vegetation can occur.
        """
        # Create combined mask from all input arrays
        nodata_mask = soil_code.mask | mhw.mask | mlw.mask
        if full_model:
            nodata_mask = nodata_mask | nutrient_level.mask | acidity.mask
        if inundation is not None:
            nodata_mask = nodata_mask | inundation.mask
        if management is not None:
            nodata_mask = nodata_mask | management.mask

        if np.all(nodata_mask):
            raise NicheException("Only nodata values in prediction")

        if full_model:
            check_codes_used("acidity", acidity, self._ct_acidity["acidity"])
            check_codes_used(
                "nutrient_level", nutrient_level, self._ct_nutrient_level["nutrient_level"]
            )

        if inundation is not None:
            check_codes_used(
                "inundation", inundation, self._ct_inundation["inundation"]
            )
        if management is not None:
            check_codes_used("management", management, self._ct_management["management"])

        veg_bands = dict()
        veg_detail = dict()
        occurrence = dict()

        for veg_code, subtable in self._ct_vegetation.groupby("veg_code"):

            subtable = subtable.reset_index()
            # vegi is the prediction for the current veg_code
            # it is a logical or of the result of every row:
            # if a row is 0 for a pixel, that vegetation can occur

            vegi = np.zeros(soil_code.shape, dtype="int64")

            # expected code if all conditions are met
            expected = VegSuitable.SOIL + VegSuitable.MXW
            if full_model:
                expected += (
                    VegSuitable.NUTRIENT
                    + VegSuitable.ACIDITY
                    + (inundation is not None) * VegSuitable.FLOODING
                    + (management is not None) * VegSuitable.MANAGEMENT
                )

            # filter for GxG
            for row in subtable.itertuples():
                warnings.simplefilter(action="ignore", category=RuntimeWarning)
                row_soil = row.soil_code == soil_code
                vegi |= row_soil * VegSuitable.SOIL

                current_row = (
                        row_soil
                        & (row.mhw_min <= mhw)
                        & (row.mhw_max >= mhw)
                        & (row.mlw_min <= mlw)
                        & (row.mlw_max >= mlw)
                )

                vegi |= current_row * VegSuitable.MXW
                warnings.simplefilter("default")
                if full_model:
                    vegi |= (
                        current_row & (nutrient_level == row.nutrient_level)
                    ) * VegSuitable.NUTRIENT
                    vegi |= (
                        current_row & (acidity == row.acidity)
                    ) * VegSuitable.ACIDITY

                if inundation is not None:
                    vegi |= (
                        current_row & (row.inundation == inundation)
                    ) * VegSuitable.FLOODING
                if management is not None:
                    vegi |= (
                        current_row & (row.management == management)
                    ) * VegSuitable.MANAGEMENT

            vegi = np.ma.array(vegi, mask=nodata_mask,
                               fill_value=255, dtype="uint8")
            vegi_summary = vegi == expected
            vegi_summary = np.ma.array(vegi_summary, mask=nodata_mask,
                                       fill_value=255, dtype="uint8")

            if return_all or np.any(vegi):
                veg_bands[veg_code] = vegi_summary

            veg_detail[veg_code] = vegi

            occi = np.sum(vegi_summary == 1) / vegi_summary.compressed().size
            occurrence[veg_code] = occi.item()
        return veg_bands, occurrence, veg_detail

    def calculate_deviation(self, soil_code, mhw, mlw):
        """Calculates the deviation between the mhw/mlw and the reference

        This function calculates the difference between the mhw and mlw and
        the reference values for each vegetation type.

        Positive values indicate too dry values, negative values indicate too
        wet values.

        Values of zero indicate that the vegetation type can occur based on
        soil type and the value under consideration (mhw or mlw)

        Returns
        -------
        difference: dict
            A dictionary containing the difference between the vegetation
            value an the actual value.
            Keys are eg mhw_01 for mhw and vegetation type 01
        """
        nodata_mask = soil_code.mask | mhw.mask | mlw.mask

        difference = dict()

        veg = self._ct_vegetation[
            ["veg_code", "soil_code", "mhw_min", "mhw_max", "mlw_min", "mlw_max"]
        ]

        veg = veg.drop_duplicates()

        warnings.simplefilter(action="ignore", category=RuntimeWarning)
        for veg_code, subtable in veg.groupby("veg_code"):
            subtable = subtable.reset_index()

            mhw_diff = np.ma.array(np.ma.empty_like(mhw), mask=nodata_mask) * np.nan
            mlw_diff = np.ma.array(np.ma.empty_like(mlw), mask=nodata_mask) * np.nan

            for row in subtable.itertuples():
                # mhw smaller than maximum
                selection = (row.soil_code == soil_code) & (row.mhw_max < mhw)
                mhw_diff[selection] = -(mhw - row.mhw_max)[selection]

                # mhw larger than minimum
                selection = (row.soil_code == soil_code) & (row.mhw_min > mhw)
                mhw_diff[selection] = -(mhw - row.mhw_min)[selection]

                # mhw in range
                selection = (
                    (row.soil_code == soil_code)
                    & (row.mhw_min <= mhw)
                    & (row.mhw_max >= mhw)
                )
                zero_arr = np.ma.array(np.ma.zeros(soil_code.shape), mask=nodata_mask)
                mhw_diff[selection] = zero_arr[selection]

                # mlw smaller than maximum
                selection = (row.soil_code == soil_code) & (row.mlw_max < mlw)
                mlw_diff[selection] = -(mlw - row.mlw_max)[selection]

                # mlw larger than minimum
                selection = (row.soil_code == soil_code) & (row.mlw_min > mlw)
                mlw_diff[selection] = -(mlw - row.mlw_min)[selection]

                # mlw in range
                selection = (
                    (row.soil_code == soil_code)
                    & (row.mlw_min <= mlw)
                    & (row.mlw_max >= mlw)
                )
                zero_arr = np.ma.array(np.ma.zeros(soil_code.shape), mask=nodata_mask)
                mlw_diff[selection] = zero_arr[selection]

            mhw_diff = np.ma.array(mhw_diff, mask=nodata_mask,
                                   fill_value=np.nan, dtype="float32")
            mlw_diff = np.ma.array(mlw_diff, mask=nodata_mask,
                                   fill_value=np.nan, dtype="float32")

            difference["mhw_%02d" % veg_code] = mhw_diff
            difference["mlw_%02d" % veg_code] = mlw_diff

        warnings.simplefilter("default")  # Reset to default warning level
        return difference
