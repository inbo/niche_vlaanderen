from unittest import TestCase
import niche_vlaanderen as nv
import numpy as np
import rasterio

class TestFloodPlain(TestCase):
    def test__calculate(self):
        fp = nv.FloodPlain()
        fp._calculate(depth=np.array([1, 2, 3]), frequency="T25",
                      period="winter", duration=1)
        np.testing.assert_equal(np.array([3, 3, 3]), fp._veg[1])

    def test_calculate(self):
        fp = nv.FloodPlain()
        fp.calculate("testcase/floodplains/ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)
        with rasterio.open(
                "testcase/floodplains/result/F25-T10-P1-winter.asc") as dst:
            expected = dst.read(1)
        np.testing.assert_equal(expected, fp._veg[25])

    def test_plot(self):
        import matplotlib as mpl
        mpl.use('agg')

        import matplotlib.pyplot as plt
        plt.show = lambda: None

        fp = nv.FloodPlain()
        fp.calculate("testcase/floodplains/ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)
        fp.plot(7)

    
