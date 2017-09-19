
from unittest import TestCase

import numpy as np


import niche_vlaanderen

class testAcidity(TestCase):

    def test_get_soil_mlw(self):
        mlw = np.array([50,66])
        soil_codes = np.array([140000, 40000])
        a = niche_vlaanderen.Acidity()
        result = a._get_soil_mlw(soil_codes, mlw)

        np.testing.assert_equal(np.array([1, 9]), result)
