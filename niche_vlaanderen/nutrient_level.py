from pkg_resources import resource_filename

import numpy as np
import pandas as pd
from .codetables import validate_tables_nutrient_level

class NutrientLevel(object):
    '''
     Class to calculate the NutrientLevel
    '''

    nodata = 255  # unsigned 8 bit type is used

    def __init__(self, ct_lnk_soil_nutrient_level=None, ct_management=None,
                 ct_mineralisation=None, ct_soil_code= None, ct_nutrient = None):
        if ct_lnk_soil_nutrient_level is None:
            ct_lnk_soil_nutrient_level = resource_filename(
                "niche_vlaanderen",
                "system_tables/lnk_soil_nutrient_level.csv")
        if ct_management is None:
            ct_management = resource_filename(
                "niche_vlaanderen", "system_tables/management.csv")
        if ct_mineralisation is None:
            ct_mineralisation = resource_filename(
                "niche_vlaanderen",
                "system_tables/nitrogen_mineralisation.csv")
        if ct_soil_code is None:
            ct_soil_code = resource_filename(
                "niche_vlaanderen", "system_tables/soil_codes.csv")

        if ct_nutrient is None:
            ct_nutrient_level = resource_filename(
                "niche_vlaanderen", "system_tables/nutrient_level.csv")

        self.ct_lnk_soil_nutrient_level = pd.read_csv(ct_lnk_soil_nutrient_level)
        self._ct_management = pd.read_csv(ct_management).set_index("management")
        self._ct_mineralisation = pd.read_csv(ct_mineralisation)
        self._ct_nutrient_level = pd.read_csv(ct_nutrient_level)
        self._ct_soil_code = pd.read_csv(ct_soil_code)

        # convert the mineralisation to float so we can use np.nan for nodata
        self._ct_mineralisation["nitrogen_mineralisation"] = \
            self._ct_mineralisation["nitrogen_mineralisation"].astype("float64")

        validate_tables_nutrient_level(self.ct_lnk_soil_nutrient_level,
                                       self._ct_management,
                                       self._ct_mineralisation,
                                       self._ct_soil_code,
                                       self._ct_nutrient_level)

        # join soil_code to soil_name where needed
        self._ct_soil_code = pd.read_csv(ct_soil_code).set_index("soil_name")
        self._ct_mineralisation["soil_code"] = \
            self._ct_soil_code.soil_code[self._ct_mineralisation["soil_name"]]\
                .reset_index().soil_code
        self.ct_lnk_soil_nutrient_level["soil_code"] = \
            self._ct_soil_code.soil_code[
                self.ct_lnk_soil_nutrient_level["soil_name"]]\
                .reset_index().soil_code


    def _calculate_mineralisation(self, soil_code_array, msw_array):
        """
        get nitrogen mineralisation for numpy arrays
        """
        orig_shape = soil_code_array.shape
        soil_code_array = soil_code_array.flatten()
        msw_array = msw_array.flatten()
        result = np.empty(soil_code_array.shape)
        result[:] = np.nan

        for code in self._ct_mineralisation.soil_code.unique():
            # We must reset the index because digitize will give indexes
            # compared to the new table.
            select = self._ct_mineralisation.soil_code == code
            table_sel = self._ct_mineralisation[select].copy()
            table_sel = table_sel.reset_index(drop=True)
            soil_sel = (soil_code_array == code)
            index = np.digitize(msw_array[soil_sel], table_sel.msw_max,
                                right=True)

            result[soil_sel] = table_sel["nitrogen_mineralisation"][index]

        result = result.reshape(orig_shape)
        return result

    def _calculate(self, management, soil_code, nitrogen, inundation):

        # calculate management influence
        influence = np.full(management.shape, -99)  # -99 used as no data value
        for i in self._ct_management.code.unique():
            sel_grid = (management == i)
            sel_ct = (self._ct_management.code == i)
            influence[sel_grid] = \
                self._ct_management[sel_ct].influence.values[0]

        # flatten all input layers (necessary for digitize)
        orig_shape = soil_code.shape
        soil_code = soil_code.flatten()
        nitrogen = nitrogen.flatten()
        inundation = inundation.flatten()
        influence = influence.flatten()

        # search for classification values in nutrient level codetable
        result = np.full(influence.shape, self.nodata, dtype='uint8')

        for name, subtable in self.ct_lnk_soil_nutrient_level.groupby(
                ["soil_code", "management_influence"]):

            soil_selected, influence_selected = name
            table_sel = subtable.copy(deep=True).reset_index(drop=True)

            index = np.digitize(nitrogen, table_sel.total_nitrogen_max,
                                right=True)
            selection = ((soil_code == soil_selected) &
                         (influence == influence_selected))

            result[selection] = table_sel.nutrient_level[index][selection]

        # Note that niche_vlaanderen is different from the original model here:
        # only if nutrient_level <4 the inundation rule is applied.
        selection = ((result < 4) & (result != self.nodata))
        result[selection] = (result + (inundation > 0))[selection]
        result = result.reshape(orig_shape)
        return result

    def calculate(self, soil_code, msw, nitrogen_atmospheric, nitrogen_animal,
                  nitrogen_fertilizer, management, inundation):
        """
        Calculates the Nutrient level based on numpy arrays
        """

        nitrogen_mineralisation = self._calculate_mineralisation(soil_code,
                                                                 msw)
        total_nitrogen = (nitrogen_mineralisation + nitrogen_atmospheric
                          + nitrogen_animal + nitrogen_fertilizer)
        nutrient_level = self._calculate(management, soil_code, total_nitrogen,
                                         inundation)
        return nutrient_level
