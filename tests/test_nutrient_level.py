from unittest import TestCase

import numpy as np
import gdal
import osr

import niche_vlaanderen

def raster_to_numpy(filename):
    '''Read a GDAL grid as numpy array
    
    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    '''
    # Read the raster file with GDAL
    ds = gdal.Open(filename)

    #  Extract the data, transformation and projection information
    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    raster_wkt = ds.GetProjection()
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(raster_wkt)
    proj = spatial_ref.ExportToProj4()
    
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float32':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = -99
    
    # destroy the gdal object
    del ds
    return data

class testNutrientLevel(TestCase):
    
    def test_nitrogen_mineralisation_array_oneelement(self):
        soil_codes = np.array([140000])
        msw = np.array([33])
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get_mineralisation_array(soil_codes, msw)
        np.testing.assert_equal(np.array([75]), result)

    def test__get_array(self):
        '''
         Array version of the documentation test
        '''
        management = np.array([2])
        soil_code = np.array([140000])
        nitrogen = np.array([445])
        inundation = np.array([1])
        
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get_array(management, soil_code, nitrogen, inundation)
        np.testing.assert_equal(np.array(5), result)


    def test_get_array(self):
        nl = niche_vlaanderen.NutrientLevel()
        management = np.array([2])
        soil_code = np.array([140000])
        msw = np.array([33])
        nitrogen_deposition = np.array([20])
        nitrogen_animal = np.array([445])
        nitrogen_fertilizer = np.array([350])
        inundation = np.array([1])
        result = nl.get_array(soil_code, msw, nitrogen_deposition, nitrogen_animal,
                nitrogen_fertilizer, management, inundation)

        np.testing.assert_equal(np.array([5]), result)

    def test_nutrient_level_testcase(self):
        nl = niche_vlaanderen.NutrientLevel()
        soil_code = raster_to_numpy("testcase/input/soil_codes.asc")
        msw = raster_to_numpy("testcase/input/msw.asc")
        nitrogen_deposition = raster_to_numpy("testcase/input/nitrogen_atmospheric.asc")
        nitrogen_animal = raster_to_numpy("testcase/input/nitrogen_animal.asc")
        nitrogen_fertilizer = raster_to_numpy("testcase/input/nitrogen_fertilizer.asc")
        inundation = raster_to_numpy("testcase/input/inundation_nutrient_level.asc")
        management = raster_to_numpy("testcase/input/management.asc")

        nutrient_level = raster_to_numpy("testcase/intermediate/nutrient_level.asc")
        result = nl.get_array(soil_code, msw, nitrogen_deposition, nitrogen_animal,
                nitrogen_fertilizer, management, inundation)

        np.testing.assert_equal(nutrient_level, result)
