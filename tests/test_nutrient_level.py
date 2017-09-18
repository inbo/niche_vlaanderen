from unittest import TestCase

import niche_vlaanderen

class testNitrogenMineralisation(TestCase):
    def test_simple_get(self):
        '''
           This test case is the same as the documentation
        '''
        nm = niche_vlaanderen.NitrogenMineralisation()
        result = nm.get(140000,33)

        self.assertEqual(75, result)

class testNutrientLevel(TestCase):
    def test_simple_get(self):
        '''
           This test case is the same as the documentation
        '''
        nl = niche_vlaanderen.NutrientLevel()
        result = nl.get(2,140000,445,1)

        self.assertEqual(5, result)
