from pkg_resources import resource_filename

import numpy as np
import pandas as pd


class Vegetation(object):
    '''Helper class to calculate vegetation based on input arrays

    This class helps predicting vegetation based on a number of input arrays.
    On initialization the input codetables are parsed (and validated).

    Note that to use grid inputs (eg raster files) it is recommended to use
    the Niche Class
    '''
    def __init__(self, ct_vegetation=resource_filename(
                    "niche_vlaanderen",
                    "../SystemTables/niche_vegetation.csv")):
        """ Initializes the Vegetation helper class

        This class initializes the Vegetation helper class. By default it uses
        the codetables supplied by the niche_vlaanderen package. It is possible
        to overwrite this by supplying the niche_vlaanderen parameter

        Parameter
        ---------
        ct_vegetation: optional alternative classification table. Must contain
        the columns mentioned in the documentation:
         https://inbo.github.io/niche_vlaanderen/codetables.html#niche_vlaanderen
        """
        self._ct_vegetation = pd.read_csv(ct_vegetation)

    def get_vegetation(self, soil_code, nutrient_level, acidity, mhw, mlw,
                       management=None, inundation=None):
        """ Calculate vegetation types based on input arrays

        Returns
        -------
        veg: dict
            A dictionary containing the different output arrays per
            veg_code value.

        """
        nodata = ((soil_code == -99) | (nutrient_level == -99)
                  | (acidity == -99) | np.isnan(mhw) | np.isnan(mlw))

        if inundation is not None:
            nodata = nodata | (inundation == -99)
        if management is not None:
            nodata = nodata | (management == -99)

        veg = dict()
        for veg_code, subtable in self._ct_vegetation.groupby(["veg_code"]):
            subtable = subtable.reset_index()
            vi = np.zeros(soil_code.shape, dtype=bool)
            for row in subtable.itertuples():
                vi = (vi
                      | ((row.soil_code == soil_code)
                         & (row.acidity == acidity)
                         & (row.mhw_min >= mhw) & (row.mhw_max <= mhw)
                         & (row.mlw_min >= mlw) & (row.mlw_max <= mlw)
                         & (nutrient_level == row.nutrient_level)
                         )
                      )
                if inundation is not None:
                    vi = vi & (inundation == row.inundation)
                if management is not None:
                    vi = vi & (management == row.management)
            vi = vi.astype("int8")
            vi[nodata] = -99
            veg[veg_code] = vi
        return veg
