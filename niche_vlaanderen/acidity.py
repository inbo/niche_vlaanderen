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
            "niche_vlaanderen", "../SystemTables/soil_codes.csv"),
            lnk_acidity=resource_filename(
            "niche_vlaanderen", "../SystemTables/lnk_acidity.csv"),
            ct_seepage=resource_filename(
            "niche_vlaanderen", "../SystemTables/seepage.csv")):

        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_soil_mlw = pd.read_csv(ct_soil_mlw_class)
        self._ct_soil_codes = pd.read_csv(ct_soil_codes).set_index("soil_code")
        self._lnk_acidity = pd.read_csv(lnk_acidity)
        self._ct_seepage = pd.read_csv(ct_seepage)

    def _get_soil_mlw(self, soil_code, mlw):
        # determine soil_group for soil_code
        orig_shape = mlw.shape
        soil_code = soil_code.flatten()
        mlw = mlw.flatten()

        soil_group = self._ct_soil_codes.soil_group[soil_code]\
            .values.astype("int8")
        # the function above gives 0 for no data
        soil_group[soil_group == 0] = -99

        result = np.full(soil_code.shape, -99)
        for sel_group, subtable in self._ct_soil_mlw.groupby(["soil_group"]):

            subtable = subtable.copy().reset_index(drop=True)
            index = np.digitize(mlw, subtable.mlw_max, right=True)
            selection = (soil_group == sel_group)

            result[selection] = subtable.soil_mlw_class[index][selection]

        result = result.reshape(orig_shape)
        return result

    def _get_mineral_richness_class(self, conductivity):
        # conductivity may contain np.nan values - we ignore the numpy warnings
        # about the fact that these can not be compared.
        with np.errstate(invalid='ignore'):
            reclass = (conductivity >= 500).astype("int8") + 1
        reclass[np.isnan(conductivity)] = -99
        return reclass

    def _get_acidity(self, rainwater, mineral_richness, inundation, seepage,
                     soil_mlw_class):

        orig_shape = inundation.shape
        rainwater = rainwater.flatten()
        mineral_richness = mineral_richness.flatten()
        inundation = inundation.flatten()
        seepage = seepage.flatten()
        soil_mlw_class = soil_mlw_class.flatten()

        result = np.full(soil_mlw_class.shape, -99, dtype="int16")
        for labels, subtable in self._lnk_acidity.groupby(
                ["rainwater", "mineral_richness", "inundation", "seepage",
                 "soil_mlw_class"]):
            sel_rainwater, sel_mr, sel_inundation, \
                sel_seepage, sel_soil_mlw_class = labels
            subtable = subtable.copy().reset_index(drop=True)

            # TODO: 1 is added to rainwater and inundation because a different
            # convention is used between the code table and the actual grid
            # we should sort this out.
            # https://github.com/inbo/niche_vlaanderen/issues/13
            selection = ((rainwater + 1 == sel_rainwater)
                         & (mineral_richness == sel_mr)
                         & (inundation + 1 == sel_inundation)
                         & (seepage == sel_seepage)
                         & (soil_mlw_class == sel_soil_mlw_class))
            result[(selection)] = subtable.acidity[0]
        result = result.reshape(orig_shape)
        return result

    def _get_seepage_code(self, seepage):
        orig_shape = seepage.shape
        seepage = seepage.flatten()
        index = np.digitize(seepage, self._ct_seepage.seepage_max, right=True)
        seepage_code = self._ct_seepage.seepage_code[index]
        return seepage_code.values.reshape(orig_shape)

    def calculate(self, soil_class, mlw, inundation, seepage, conductivity,
                  rainwater):
        soil_mlw = self._get_soil_mlw(soil_class, mlw)
        mineral_richness = self._get_mineral_richness_class(conductivity)
        seepage_code = self._get_seepage_code(seepage)
        acidity = self._get_acidity(rainwater, mineral_richness, inundation,
                                    seepage_code, soil_mlw)
        return acidity
