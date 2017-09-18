from pkg_resources import resource_filename

import numpy as np
import pandas as pd

class NutrientLevel(object):
    '''
     Class to calculate the NutrientLevel
    '''
    def __init__(self, 
            code_table_nutrient_level = resource_filename("niche_vlaanderen", "../SystemTables/lnk_soil_nutrient_level.csv"),
            code_table_management = resource_filename("niche_vlaanderen", "../SystemTables/management.csv"),
            code_table_mineralisation = resource_filename("niche_vlaanderen","../SystemTables/nitrogen_mineralisation.csv")
            ):
        
        self._ct_nutrient_level = pd.read_csv(code_table_nutrient_level)
        self._ct_management = pd.read_csv(code_table_management)
        self._ct_mineralisation = pd.read_csv(code_table_mineralisation)

        # convert the mineralisation columns to float so we can use np.nan for nodata
        self._ct_mineralisation = self._ct_mineralisation.astype("float64")

    def _get_mineralisation(self,soil_code, msw):
        """
        get nitrogen mineralisation for single values
        """
        result= self._ct_mineralisation[
                ((self._ct_mineralisation.soil_code == soil_code) 
                & (self._ct_mineralisation.msw_min <= msw )
                & (self._ct_mineralisation.msw_max >msw))].nitrogen_mineralisation.values
        return result[0] if result.size >0 else np.nan
        
    def _get_mineralisation_array(self, soil_code_array, msw_array):
        """
        get nitrogen mineralisation for numpy arrays
        """
        orig_shape = soil_code_array.shape
        soil_code_array = soil_code_array.flatten()
        msw_array = msw_array.flatten()
        result = np.empty(soil_code_array.shape)
        result[:]= np.nan
        
        for code in self._ct_mineralisation.soil_code.unique():
            # we must reset the index because digitize will give indexes compared to the new table.
            table_sel = self._ct_mineralisation[self._ct_mineralisation.soil_code == code].copy(deep=True).reset_index(drop=True)
            soil_code_sel = (soil_code_array == code)
            index = np.digitize(msw_array[soil_code_sel], table_sel.msw_max)
          
            result[soil_code_sel] = table_sel.nitrogen_mineralisation[index]
            
        result = result.reshape(orig_shape
                                      )
        return result

    def _get(self, management, soil_code, nitrogen, inundation):
        """
        Calculates the nutrient level based on management, total nitrogen and inundation
        """
        management_influence = self._ct_management[self._ct_management.code == management].influence.values[0]
        selection = ( (self._ct_nutrient_level.management_influence == management_influence)
                    & (self._ct_nutrient_level.soil_code == soil_code)
                    & (self._ct_nutrient_level.total_nitrogen_min <= nitrogen)
                    & (self._ct_nutrient_level.total_nitrogen_max > nitrogen))
        result = self._ct_nutrient_level[(selection)].nutrient_level.values
        
        nutrient_level = result[0] if result.size>0 else np.nan

        # influence inundation
        # TODO: return nan or throw error if inundation is not in 0,1 ?

        nutrient_level = min(nutrient_level + inundation, 5) if inundation in [0,1] else np.nan
        return nutrient_level

    def _get_array(self, management, soil_code, nitrogen, inundation):

        # calculate management influence
        influence = np.full(management.shape, -99) # -99 used as no data value
        for i in self._ct_management.code.unique():
            influence[management == i] = self._ct_management[self._ct_management.code == i].influence.values[0] 
       
        # flatten all input layers (necessary for next step)
        orig_shape = soil_code.shape
        soil_code = soil_code.flatten()
        nitrogen = nitrogen.flatten()
        inundation = inundation.flatten()
        influence = influence.flatten()

        # search for classification values in nutrient level codetable
        result = np.full(influence.shape, -99)
        for name, group in self._ct_nutrient_level.groupby(["soil_code","management_influence"]):
            soil_selected, influence_selected = name
            table_sel = group.copy(deep=True).reset_index(drop=True)
            index = np.digitize(nitrogen, table_sel.total_nitrogen_max)
            selection = (soil_code == soil_selected) & (influence == influence_selected)
            result[selection] = table_sel.nutrient_level[index][selection]
        result = result.reshape(orig_shape)
        return result

    def get(self, soil_code, msw, nitrogen_atmospheric, nitrogen_animal, nitrogen_fertilizer, management, inundation):
        """
        Calculates the Nutrient level based on single values
        """
        # First step: get the nitrogen mineralisation
        nitrogen_mineralisation = self._get_mineralisation(soil_code, msw)
        total_nitrogen = nitrogen_mineralisation + nitrogen_atmospheric\
                + nitrogen_animal + nitrogen_fertilizer
        nutrient_level = self._get(management, soil_code, total_nitrogen, inundation)
        return nutrient_level

    def get_array(self, soil_code, msw, nitrogen_atmospheric, nitrogen_animal, nitrogen_fertilizer, management, inundation):
        """
        Calculates the Nutrient level based on numpy arrays
        """

        nitrogen_mineralisation = self._get_mineralisation_array(soil_code, msw)
        total_nitrogen = nitrogen_mineralisation + nitrogen_atmospheric\
                + nitrogen_animal + nitrogen_fertilizer
        nutrient_level = self._get_array(management, soil_code, total_nitrogen, inundation)
        return nutrient_level
