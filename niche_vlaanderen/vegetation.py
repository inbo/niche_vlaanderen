from pkg_resources import resource_filename

import numpy as np
import pandas as pd


class Vegetation(object):
    '''
    '''
    def __init__(self, ct_vegetation=resource_filename(
                    "niche_vlaanderen",
                    "../SystemTables/niche_vegetation.csv")):
        self._ct_vegetation = pd.read_csv(ct_vegetation)

    def get_vegetation(self, soil_code, nutrient_level, acidity, mhw, mlw,
                       management=None, inundation=None):

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
