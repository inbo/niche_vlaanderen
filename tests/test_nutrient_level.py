from unittest import TestCase

import numpy as np

import niche_vlaanderen

class testNutrientLevel(TestCase):
    def test_nitrogen_mineralisation(self):
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get_mineralisation(140000,33)
        self.assertEqual(75, result)
    
    def test_nitrogen_mineralisation_array_oneelement(self):
        soil_codes = np.array(140000)
        msw = np.array(33)
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get_mineralisation_array(soil_codes, msw)
        np.testing.assert_equal(np.array(75), result)

    def test__get(self):
        '''
           This test case is the same as the documentation
        '''
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._get(2,140000,445,1)

        self.assertEqual(5, result)

    def test_get(self):
        nl = niche_vlaanderen.NutrientLevel()
        result = nl.get(140000,33,20,445,350,2,1)
        
        self.assertEqual(5, result)
