from pkg_resources import resource_filename

import numpy as np
import pandas as pd


class Vegetation(object):
    '''
    '''
    def __init__(self,
            ct_vegetation=resource_filename(
                "niche_vlaanderen", "../SystemTables/niche_vegetation.csv")):
        self._ct_vegetation = pd.read_csv(ct_vegetation)

    def get_vegetation(self, soil_code, nutrient_level, acidity, mhw, mlw,
            management, inundation):

        veg = list()
        for veg_code, subtable in self._ct_vegetation.groupby(["veg_code"]):
            subtable = subtable.reset_index()
            veg[veg_code] = np.zero(soil_code.shape)
            for row in subtable.iterrows():
                veg[veg_code] = (veg[veg_code]
                    | ((row.soil_code == soil_code) & (row.acidity == acidity)
                        & (row.mhw_min < mhw) & (row.mhw_max > mhw)
                        & (row.mlw_min < mlw) & (row.mlw_max > mlw)
                        & (nutrient_level == row.nutrient_level)
                        & (inundation == row.inundation)
                        & (management == row.management)))

        # set cells to no data if any of the inputs has no data
        sel = ((soil_code ==-99) | (nutrient_level == -99) | (acidity == -99)
                | np.isnan(mhw_min) | np.isnan(mhw_max)
                | np.isnan(mlw_min) | np.isnan(mlw_max)
                | (management == -99) | (inundation == -99)
                )
        for vi in veg:
            vi[sel] = -99
        return veg

