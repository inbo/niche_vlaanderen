from pkg_resources import resource_filename

import numpy as np
import pandas as pd

from .codetables import validate_tables_acidity

class Acidity(object):
    '''
    '''

    nodata = 255  # uint8 data type

    def __init__(self, ct_acidity=None,
                 ct_soil_mlw_class=None,
                 ct_soil_codes=None,
                 lnk_acidity=None,
                 ct_seepage=None):

        if ct_acidity is None:
            ct_acidity = resource_filename(
             "niche_vlaanderen", "system_tables/acidity.csv")
        if ct_soil_mlw_class is None:
            ct_soil_mlw_class = resource_filename(
             "niche_vlaanderen", "system_tables/soil_mlw_class.csv")
        if ct_soil_codes is None:
            ct_soil_codes = resource_filename(
             "niche_vlaanderen", "system_tables/soil_codes.csv")
        if lnk_acidity is None:
            lnk_acidity = resource_filename(
             "niche_vlaanderen", "system_tables/lnk_acidity.csv")
        if ct_seepage is None:
            ct_seepage = resource_filename(
             "niche_vlaanderen", "system_tables/seepage.csv")

        self._ct_acidity = pd.read_csv(ct_acidity)
        self._ct_soil_mlw = pd.read_csv(ct_soil_mlw_class)
        self._ct_soil_codes = pd.read_csv(ct_soil_codes)
        self._lnk_acidity = pd.read_csv(lnk_acidity)
        self._ct_seepage = pd.read_csv(ct_seepage)

        validate_tables_acidity(ct_acidity=self._ct_acidity,
                                ct_soil_mlw_class=self._ct_soil_mlw,
                                ct_soil_codes=self._ct_soil_codes,
                                lnk_acidity=self._lnk_acidity,
                                ct_seepage=self._ct_seepage)

        self._ct_soil_codes = self._ct_soil_codes.set_index("soil_code")

    def _calculate_soil_mlw(self, soil_code, mlw):
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

    def _calculate_mineral_richness_class(self, conductivity):
        # conductivity may contain np.nan values - we ignore the numpy warnings
        # about the fact that these can not be compared.
        with np.errstate(invalid='ignore'):
            reclass = (conductivity >= 500).astype("int8")
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

        result = np.full(soil_mlw_class.shape, self.nodata, dtype="uint8")
        for labels, subtable in self._lnk_acidity.groupby(
                ["rainwater", "mineral_richness", "inundation", "seepage",
                 "soil_mlw_class"]):
            sel_rainwater, sel_mr, sel_inundation, \
                sel_seepage, sel_soil_mlw_class = labels
            subtable = subtable.copy().reset_index(drop=True)

            selection = ((rainwater == sel_rainwater)
                         & (mineral_richness == sel_mr)
                         & (inundation == sel_inundation)
                         & (seepage == sel_seepage)
                         & (soil_mlw_class == sel_soil_mlw_class))
            result[(selection)] = subtable.acidity[0]
        result = result.reshape(orig_shape)
        return result

    def _get_seepage(self, seepage):
        orig_shape = seepage.shape
        seepage = seepage.flatten()
        index = np.digitize(seepage, self._ct_seepage.seepage_max, right=True)
        seepage = self._ct_seepage.seepage[index]
        return seepage.values.reshape(orig_shape)

    def calculate(self, soil_class, mlw, inundation, seepage, conductivity,
                  rainwater):
        soil_mlw = self._calculate_soil_mlw(soil_class, mlw)
        mineral_richness = self._calculate_mineral_richness_class(conductivity)
        seepage = self._get_seepage(seepage)
        acidity = self._get_acidity(rainwater, mineral_richness, inundation,
                                    seepage, soil_mlw)
        return acidity
