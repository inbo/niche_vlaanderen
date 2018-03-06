from __future__ import division
from pkg_resources import resource_filename

import numpy as np
import pandas as pd

from .nutrient_level import NutrientLevel
from .acidity import Acidity
from .codetables import validate_tables_vegetation, check_codes_used
from .exception import NicheException


class Vegetation(object):
    """Helper class to calculate vegetation based on input arrays

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

    nodata_veg = 255  # uint8

    def __init__(self, ct_vegetation=None, ct_soil_code=None, ct_acidity=None,
                 ct_management=None, ct_nutrient_level=None,
                 ct_inundation=None):
        """ Initializes the Vegetation helper class

        This class initializes the Vegetation helper class. By default it uses
        the code tables supplied by the niche_vlaanderen package. It is
        possible to overwrite this by supplying the niche_vlaanderen parameter

        """

        if ct_vegetation is None:
            ct_vegetation = resource_filename(
                "niche_vlaanderen",
                "system_tables/niche_vegetation.csv")

        # Note that the next code tables are only used for validation, they are
        # not part of the logic of the vegetation class

        if ct_soil_code is None:
            ct_soil_code = resource_filename(
                "niche_vlaanderen", "system_tables/soil_codes.csv")

        if ct_acidity is None:
            ct_acidity = resource_filename(
                "niche_vlaanderen", "system_tables/acidity.csv")

        if ct_nutrient_level is None:
            ct_nutrient_level = resource_filename(
                "niche_vlaanderen", "system_tables/nutrient_level.csv")

        if ct_management is None:
            ct_management = resource_filename(
                "niche_vlaanderen", "system_tables/management.csv")

        if ct_inundation is None:
            ct_inundation = resource_filename(
                "niche_vlaanderen", "system_tables/inundation.csv")

        self._ct_vegetation = pd.read_csv(ct_vegetation)
        self._ct_soil_code = pd.read_csv(ct_soil_code)
        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_nutrient_level = pd.read_csv(ct_nutrient_level)
        self._ct_management = pd.read_csv(ct_management)
        self._ct_inundation = pd.read_csv(ct_inundation)

        # we check for inner joins if codetables are not overwritten
        # https://github.com/inbo/niche_vlaanderen/issues/106
        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])

        validate_tables_vegetation(ct_vegetation=self._ct_vegetation,
                                   ct_soil_code=self._ct_soil_code,
                                   ct_acidity=self._ct_acidity,
                                   ct_management=self._ct_management,
                                   ct_nutrient_level=self._ct_nutrient_level,
                                   ct_inundation=self._ct_inundation,
                                   inner=inner)

        # join soil_code to soil_name where needed
        self._ct_soil_code = self._ct_soil_code.set_index("soil_name")
        self._ct_vegetation["soil_code"] = \
            self._ct_soil_code.soil_code[self._ct_vegetation["soil_name"]]\
                .reset_index().soil_code

    def calculate(self, soil_code, mhw, mlw, nutrient_level=None, acidity=None,
                  management=None, inundation=None, return_all=True,
                  full_model=True):
        """ Calculate vegetation types based on input arrays

        Parameters
        ----------
        return_all: boolean
            A boolean (default=True) whether all grids should be returned or
            only grids containing data.

        Returns
        -------
        veg: dict
            A dictionary containing the different output arrays per
            veg_code value.
            -99 is used for nodata_veg values
        veg_occurrence: dict
            A dictionary containing the percentage of the area where the
            vegetation can occur.

        """

        nodata = ((soil_code == -99) | np.isnan(mhw) | np.isnan(mlw))

        if full_model:
            nodata = nodata | (nutrient_level == NutrientLevel.nodata) \
                     | (acidity == Acidity.nodata)

        if inundation is not None:
            nodata = nodata | (inundation == -99)

        if management is not None:
            nodata = nodata | (management == -99)

        if np.all(nodata):
            raise NicheException("only nodata values in prediction")

        if full_model:
            check_codes_used("acidity", acidity,
                             self._ct_acidity["acidity"])
            check_codes_used("nutrient_level", nutrient_level,
                             self._ct_nutrient_level["code"])

        if inundation is not None:
            check_codes_used("inundation", inundation,
                             self._ct_inundation["inundation"])
        if management is not None:
            check_codes_used("management", management,
                             self._ct_management["code"])

        veg_bands = dict()
        occurrence = dict()

        for veg_code, subtable in self._ct_vegetation.groupby(["veg_code"]):
            subtable = subtable.reset_index()
            # vegi is the prediction for the current veg_code
            # it is a logical or of the result of every row:
            # if a row is true for a pixel, that vegetation can occur
            vegi = np.zeros(soil_code.shape, dtype=bool)
            for row in subtable.itertuples():
                current_row = ((row.soil_code == soil_code)
                               & (row.mhw_min >= mhw) & (row.mhw_max <= mhw)
                               & (row.mlw_min >= mlw) & (row.mlw_max <= mlw))
                if full_model:
                    current_row = (current_row
                                   & (nutrient_level == row.nutrient_level)
                                   & (row.acidity == acidity))

                if inundation is not None:
                    current_row = current_row & (row.inundation == inundation)
                if management is not None:
                    current_row = current_row & (row.management == management)
                vegi = vegi | current_row
            vegi = vegi.astype("uint8")
            vegi[nodata] = self.nodata_veg

            if return_all or np.any(vegi):
                veg_bands[veg_code] = vegi

            occurrence[veg_code] = np.asscalar(
                (np.sum(vegi == 1) / (vegi.size - np.sum(nodata))))
        return veg_bands, occurrence

    def calculate_deviation(self, soil_code, mhw, mlw):
        """ Calculates the deviation between the mhw/mlw and the reference

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
        nodata = ((soil_code == -99) | np.isnan(mhw) | np.isnan(mlw))

        difference = dict()

        veg = self._ct_vegetation[["veg_code", "soil_code", "mhw_min",
                                   "mhw_max", "mlw_min", "mlw_max"]]

        veg = veg.drop_duplicates()

        for veg_code, subtable in veg.groupby(["veg_code"]):
            subtable = subtable.reset_index()

            mhw_diff = np.full(soil_code.shape, np.nan)
            mlw_diff = np.full(soil_code.shape, np.nan)

            for row in subtable.itertuples():
                # mhw smaller than maximum
                sel = (row.soil_code == soil_code) & (row.mhw_max > mhw)
                mhw_diff[sel] = (mhw - row.mhw_max)[sel]

                # mhw larger than minimum
                sel = (row.soil_code == soil_code) & (row.mhw_min < mhw)
                mhw_diff[sel] = (mhw - row.mhw_min)[sel]

                # mhw in range
                sel = ((row.soil_code == soil_code) & (row.mhw_min >= mhw)
                       & (row.mhw_max <= mhw))
                mhw_diff[sel] = (np.zeros(soil_code.shape))[sel]

                # mlw smaller than maximum
                sel = (row.soil_code == soil_code) & (row.mlw_max > mlw)
                mlw_diff[sel] = (mlw - row.mlw_max)[sel]

                # mlw larger than minimum
                sel = (row.soil_code == soil_code) & (row.mlw_min < mlw)
                mlw_diff[sel] = (mlw - row.mlw_min)[sel]

                # mlw in range
                sel = ((row.soil_code == soil_code) & (row.mlw_min >= mlw)
                       & (row.mlw_max <= mlw))
                mlw_diff[sel] = (np.zeros(soil_code.shape))[sel]

            mhw_diff[nodata] = np.NaN
            mlw_diff[nodata] = np.NaN

            difference["mhw_%02d" % veg_code] = mhw_diff
            difference["mlw_%02d" % veg_code] = mlw_diff

        return difference
