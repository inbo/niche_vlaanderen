from unittest import TestCase

import numpy as np
import rasterio

import niche_vlaanderen


def raster_to_numpy(filename):
    '''Read a GDAL grid as numpy array

    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    '''
    with rasterio.open(filename) as ds:
        data = ds.read(1)
        nodata = ds.nodatavals[0]

    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float32':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = -99

    return data


class testNutrientLevel(TestCase):

    def test_nitrogen_mineralisation(self):
        soil_codes = np.array([140000])
        msw = np.array([33])
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get_mineralisation(soil_codes, msw)
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
        result = nl._get(management, soil_code, nitrogen, inundation)
        np.testing.assert_equal(np.array(5), result)

    def test_calculate(self):
        nl = niche_vlaanderen.NutrientLevel()
        management = np.array([2])
        soil_code = np.array([140000])
        msw = np.array([33])
        nitrogen_deposition = np.array([20])
        nitrogen_animal = np.array([350])
        nitrogen_fertilizer = np.array([0])
        inundation = np.array([1])
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation)

        np.testing.assert_equal(np.array([5]), result)

    def test_nutrient_level_testcase(self):
        nl = niche_vlaanderen.NutrientLevel()
        soil_code = raster_to_numpy("testcase/input/soil_codes.asc")
        msw = raster_to_numpy("testcase/input/msw.asc")
        nitrogen_deposition = \
            raster_to_numpy("testcase/input/nitrogen_atmospheric.asc")
        nitrogen_animal = raster_to_numpy("testcase/input/nitrogen_animal.asc")
        nitrogen_fertilizer = raster_to_numpy("testcase/input/nullgrid.asc")
        inundation = \
            raster_to_numpy("testcase/input/inundation_nutrient_level.asc")
        management = raster_to_numpy("testcase/input/management.asc")

        nutrient_level = \
            raster_to_numpy("testcase/intermediate/nutrient_level.asc")
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation)

        np.testing.assert_equal(nutrient_level, result)
