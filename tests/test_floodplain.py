from unittest import TestCase
import niche_vlaanderen as nv
import numpy as np
import rasterio
from niche_vlaanderen.floodplain import FloodPlainException
import pytest
import os
import tempfile
import shutil
import sys


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

    def test_calculate_arcgis(self):
        # note this tests uses an arcgis raster with only 8bit unsigned values
        fp = nv.FloodPlain()
        fp.calculate("tests/data/ff_bt_t10_h", "T10",
                     period="winter", duration=1)
        with rasterio.open(
                "testcase/floodplains/result/F25-T10-P1-winter.asc") as dst:
            expected = dst.read(1)
        np.testing.assert_equal(expected, fp._veg[25])

    def test_calculate_withnodata(self):
        fp = nv.FloodPlain()
        fp.calculate("tests/data/depths_with_nodata.asc", "T10",
                     period="winter", duration=1)
        unique = []
        for i in fp._veg:
            unique.append(np.unique(fp._veg[i]))
        unique = np.unique(np.hstack(unique))
        expected = np.array([-99, 0, 1, 2, 3, 4])
        np.testing.assert_equal(expected, unique)

    def test_table(self):
        fp = nv.FloodPlain()
        with pytest.raises(FloodPlainException):
            fp.table

        fp.calculate(depth_file="testcase/floodplains/ff_bt_t10_h.asc",
                     frequency="T10", period="winter", duration=1)
        df = fp.table
        sel = df[((df.vegetation == 1)
                  & (df.presence == "goed combineerbaar"))]
        assert np.all(178.64 == np.round(sel["area_ha"], 2))

    def test_plot(self):
        import matplotlib as mpl
        mpl.use('agg')

        import matplotlib.pyplot as plt
        plt.show = lambda: None

        fp = nv.FloodPlain()
        fp.calculate("testcase/floodplains/ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)
        fp.plot(7)

        with pytest.raises(FloodPlainException):
            fp.plot(2000)

    def test_write(self):
        fp = nv.FloodPlain()
        tempdir = tempfile.mkdtemp() + "/newdir"
        with pytest.raises(FloodPlainException):
            # Should fail - model not yet run
            fp.write(tempdir)

        fp.calculate("testcase/floodplains/ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)

        fp.write(tempdir)

        expected_files = [
            'F01-T10-P1-winter.tif', 'F07-T10-P1-winter.tif',
            'F16-T10-P1-winter.tif', 'F22-T10-P1-winter.tif',
            'F02-T10-P1-winter.tif', 'F08-T10-P1-winter.tif',
            'F17-T10-P1-winter.tif', 'F23-T10-P1-winter.tif',
            'F03-T10-P1-winter.tif', 'F09-T10-P1-winter.tif',
            'F18-T10-P1-winter.tif', 'F24-T10-P1-winter.tif',
            'F04-T10-P1-winter.tif', 'F12-T10-P1-winter.tif',
            'F19-T10-P1-winter.tif', 'F25-T10-P1-winter.tif',
            'F05-T10-P1-winter.tif', 'F14-T10-P1-winter.tif',
            'F20-T10-P1-winter.tif', 'F27-T10-P1-winter.tif',
            'F06-T10-P1-winter.tif', 'F15-T10-P1-winter.tif',
            'F21-T10-P1-winter.tif', 'F28-T10-P1-winter.tif'
        ]

        dir = os.listdir(tempdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tempdir)

    def test_combine(self):
        fp = nv.FloodPlain()

        myniche = nv.Niche()
        input = "testcase/dijle/"
        myniche.set_input("soil_code", input + "bodemv.asc")
        myniche.set_input("msw", input + "gvg_0_cm.asc")
        myniche.set_input("mlw", input + "glg_0_cm.asc")
        myniche.set_input("mhw", input + "ghg_0_cm.asc")
        myniche.set_input("seepage", input + "kwel_mm_dag.asc")

        myniche.set_input("management", input + "beheer_int.asc")

        myniche.set_input("nitrogen_atmospheric", input + "depositie_def.asc")
        myniche.set_input("nitrogen_animal", input + "bemest_dier.asc")

        myniche.set_input("nitrogen_fertilizer", input + "bemest_kunst.asc")

        myniche.set_input("inundation_vegetation", input + "overstr_veg.asc")
        myniche.set_input("inundation_acidity", input + "ovrstr_t10_50.asc")
        myniche.set_input("inundation_nutrient", input + "ovrstr_t10_50.asc")

        myniche.set_input("minerality", input + "minerality.asc")

        myniche.set_input("rainwater", input + "nulgrid.asc")

        with pytest.raises(FloodPlainException):
            # niche model not yet run
            fp.combine(myniche)

        myniche.run()
        with pytest.raises(FloodPlainException):
            # floodplain model not yet run
            fp.combine(myniche)

        fp.calculate("testcase/floodplains/ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)

        small = nv.Niche()
        small.run_config_file("tests/small.yaml")

        with pytest.raises(FloodPlainException):
            # floodplain has different spatial extent than niche
            fp.combine(small)

        result = fp.combine(myniche)

        # get unique values for every vegtype
        unique = []
        for i in result._veg:
            unique.append(np.unique(result._veg[i]))
        unique = np.unique(np.hstack(unique))
        expected = np.array([-99, 0, 1, 2, 3])
        np.testing.assert_equal(expected, unique)
