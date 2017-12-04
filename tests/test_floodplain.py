from unittest import TestCase
import niche_vlaanderen as nv
import numpy as np


class TestFloodPlain(TestCase):
    def test__calculate(self):
        fp = nv.FloodPlain()
        fp._calculate(depth=np.array([1, 2, 3]), frequency="T10",
                      period="winter", duration=1)
        np.testing.assert_equal(np.array([3, 3, 3]), fp._veg[1])
