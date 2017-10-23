from __future__ import division
from pkg_resources import resource_filename

import numpy as np
import pandas as pd

from .nutrient_level import NutrientLevel
from .acidity import Acidity


class Vegetation(object):
    """Helper class to calculate vegetation based on input arrays

    This class helps predicting vegetation based on a number of input arrays.
    On initialization the input codetables are parsed (and validated).

    Note that to use grid inputs (eg raster files) it is recommended to use
    the Niche Class
    """

    nodata = 255 # uint8

    def __init__(self, ct_vegetation=resource_filename(
                    "niche_vlaanderen",
                    "../SystemTables/niche_vegetation.csv")):
        """ Initializes the Vegetation helper class

        This class initializes the Vegetation helper class. By default it uses
        the codetables supplied by the niche_vlaanderen package. It is possible
        to overwrite this by supplying the niche_vlaanderen parameter

        Parameters
        ----------
        ct_vegetation: filename, .csv
            optional alternative classification table
            Must contain the columns mentioned in the documentation:
            https://inbo.github.io/niche_vlaanderen/codetables.html#niche_vlaanderen
        """
        self._ct_vegetation = pd.read_csv(ct_vegetation)

    def calculate(self, soil_code, mhw, mlw, nutrient_level=None, acidity=None,
                  management=None, inundation=None, return_all=True,
                  full_model=True):
        """ Calculate vegetation types based on input arrays

        Returns
        -------
        veg: dict
            A dictionary containing the different output arrays per
            veg_code value.
            -99 is used for nodata values
        veg_occurence: dict
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

        veg_bands = dict()
        occurence = dict()

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
            vegi[nodata] = self.nodata

            if return_all or np.any(vegi):
                veg_bands[veg_code] = vegi

            if np.any(vegi == 1):
                occurence[veg_code] = (np.sum(vegi == 1)
                                       / (vegi.size - np.sum(nodata)))
        return veg_bands, occurence

    def calculate_difference(self, soil_code, mhw, mlw):
        """ Calculates the difference between the mhw/mlw and the reference

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
                                   "mhw_max", "mlw_min","mlw_max"]];

        veg = veg.drop_duplicates()

        for veg_code, subtable in veg.groupby(["veg_code"]):
            subtable = subtable.reset_index()

            mhw_diff = np.zeros(soil_code.shape)
            mlw_diff = np.zeros(soil_code.shape)

            for row in subtable.itertuples():
                # mhw smaller than maximum
                sel = (row.soil_code == soil_code) & (row.mhw_max > mhw)
                mhw_diff[sel] = (mhw - row.mhw_max)[sel]

                # mhw larger than minimum
                sel = (row.soil_code == soil_code) & (row.mhw_min < mhw)
                mhw_diff[sel] = (mhw - row.mhw_min)[sel]
                
                # mlw smaller than maximum
                sel = (row.soil_code == soil_code) & (row.mlw_max > mlw)
                mlw_diff[sel] = (mlw - row.mlw_max)[sel]

                # mlw larger than minimum
                sel = (row.soil_code == soil_code) & (row.mlw_min < mlw)
                mlw_diff[sel] = (mlw - row.mlw_min)[sel]

            mhw_diff[nodata] = np.NaN
            mlw_diff[nodata] = np.NaN

            difference["mhw_%02d" % veg_code] = mhw_diff
            difference["mlw_%02d" % veg_code] = mlw_diff

        return difference


