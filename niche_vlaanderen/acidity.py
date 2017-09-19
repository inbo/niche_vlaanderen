from pkg_resources import resource_filename

import numpy as np
import pandas as pd


class Acidity(object):
    '''
    '''
    def __init__(self, ct_acidity=resource_filename(
            "niche_vlaanderen", "../SystemTables/acidity.csv"),
            ct_soil_mlw_class=resource_filename(
            "niche_vlaanderen", "../SystemTables/soil_mlw_class.csv"),
            ct_soil_codes=resource_filename(
            "niche_vlaanderen", "../SystemTables/soil_codes.csv")):

        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_soil_mlw = pd.read_csv(ct_soil_mlw_class)
        self._ct_soil_codes = pd.read_csv(ct_soil_codes).set_index("soil_code")

    def _get_soil_mlw(self, soil_code, mlw):
        # determine soil_group for soil_code
        orig_shape = mlw.shape
        soil_code = soil_code.flatten()
        mlw = mlw.flatten()

        soil_group = np.array(self._ct_soil_codes.soil_group[soil_code])

        result = np.full(soil_code.shape, -99)
        for sel_soil_group, table in self._ct_soil_mlw.groupby(["soil_group"]):
            table_sel = table.copy().reset_index(drop=True)
            index = np.digitize(mlw, table_sel.mlw_max, right=True)
            selection = (soil_group == sel_soil_group)
            result[selection] = table_sel.soil_mlw_class[index][selection]

        result.reshape(orig_shape)
        return result

    def _get_mineral_richness_class(self, conductivity):
        reclass = (conductivity >= 500).astype("int8")
        reclass[np.isnan(conductivity)] = -99
        return reclass
