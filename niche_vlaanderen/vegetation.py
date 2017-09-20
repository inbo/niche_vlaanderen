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
                       management, inundation):

        nodata = ((soil_code == -99) | (nutrient_level == -99)
                  | (acidity == -99) | np.isnan(mhw) | np.isnan(mlw)
                  | (management == -99) | (inundation == -99)
                  )

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
                         # currently vegetation and management are not taken
                         # into account like the testcase
                         # & (inundation == row.inundation)
                         # & (management == row.management))
                         )
                      )
            vi = vi.astype("int8")
            vi[nodata] = -99
            veg[veg_code] = vi
        return veg
