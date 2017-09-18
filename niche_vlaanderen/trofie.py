import numpy as np
import pandas as pd

class NitrogenMineralisation(object):
    ''' class to calculate mineralisation
    '''
    def __init__(self, code_table = "../SystemTables/nitrogen_mineralisation.csv"):
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

class TrofieCode(object):
    '''
     Class to calculate the coded Trofie
    '''
    def __init__(self, code_table_trofie = "../SystemTables/lnk_soil_trofie.csv",
            code_table_management = "../SystemTables/management.csv"):
        self.table_trofie = pd.read_csv(code_table_trofie)
        self.table_management = pd.read_csv(code_table_management)

    def get(self, management, soil_code, nitrogen, inundation_trofie):
       management_influence = self.table_management[self.table_management.code == management].influence.values[0]
       selection = ((self.table_trofie.management_influence == management_influence)
                   & (self.table_trofie.soil_code == soil_code)
                   & (self.table_trofie.total_nitrogen_min <= nitrogen)
                   & (self.table_trofie.total_nitrogen_max > nitrogen))
       result = self.table_trofie[(selection)].trofie_code.values
       
       trofie = result[0] if result.size>0 else np.nan

       # influence inundation

       # check inundation is 0 or 1 - else fail - do it here or somewhere else?

       trofie = min(trofie + inundation_trofie, 5)
       return trofie


