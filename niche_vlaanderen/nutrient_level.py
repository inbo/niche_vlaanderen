from pkg_resources import resource_filename

import numpy as np
import pandas as pd

class NitrogenMineralisation(object):
    ''' class to calculate mineralisation
    '''
    def __init__(self, code_table = resource_filename("niche_vlaanderen","../SystemTables/nitrogen_mineralisation.csv")):
        self.table = pd.read_csv(code_table)
        
        # convert the mineralisation columns to float so we can use np.nan for nodata
        self.table.nitrogen_mineralisation = self.table.nitrogen_mineralisation.astype("float64")
        
    def get(self,soil_code, msw):
        result= self.table.nitrogen_mineralisation[
                ((self.table.soil_code == soil_code) 
                & (self.table.msw_min <= msw )
                & (self.table.msw_max >msw))].values
        return result[0] if result.size >0 else np.nan
        
    def get_array(self, soil_code_array, msw_array):
        # logic: use digitize per unique code
        orig_shape = soil_code_array.shape
        soil_code_array = soil_code_array.flatten()
        msw_array = msw_array.flatten()
        result = np.empty(soil_code_array.shape)
        result[:]= np.nan
        
        for code in self.table.soil_code.unique():
            # we must reset the index because digitize will give indexes compared to the new table.
            table_sel = self.table[self.table.soil_code == code].copy(deep=True).reset_index(drop=True)
            soil_code_sel = (soil_code_array == code)
            index = np.digitize(msw_array[soil_code_sel], table_sel.msw_max)
          
            result[soil_code_sel] = table_sel.nitrogen_mineralisation[index]
            
        result = result.reshape(orig_shape
                                      )
        return result

class NutrientLevel(object):
    '''
     Class to calculate the coded NutrientLevel
    '''
    def __init__(self, 
            code_table_nutrient_level = resource_filename("niche_vlaanderen", "../SystemTables/lnk_soil_nutrient_level.csv"),
            code_table_management = resource_filename("niche_vlaanderen", "../SystemTables/management.csv")):
        self.table_nutrient_level = pd.read_csv(code_table_nutrient_level)
        self.table_management = pd.read_csv(code_table_management)

    def get(self, management, soil_code, nitrogen, inundation_nutrient_level):
       management_influence = self.table_management[self.table_management.code == management].influence.values[0]
       selection = ((self.table_nutrient_level.management_influence == management_influence)
                   & (self.table_nutrient_level.soil_code == soil_code)
                   & (self.table_nutrient_level.total_nitrogen_min <= nitrogen)
                   & (self.table_nutrient_level.total_nitrogen_max > nitrogen))
       result = self.table_nutrient_level[(selection)].nutrient_level.values
       
       nutrient_level = result[0] if result.size>0 else np.nan

       # influence inundation

       # TODO: return nan or error if inundation is not in 0,1 ?

       nutrient_level = min(nutrient_level + inundation_nutrient_level, 5) if inundation_nutrient_level in [0,1] else np.nan
       return nutrient_level


