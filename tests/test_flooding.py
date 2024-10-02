from collections import Counter
import niche_vlaanderen as nv
import numpy as np
import rasterio
from niche_vlaanderen.flooding import FloodingException
import pytest
import os
import tempfile
import shutil
import sys


class TestFlooding:

    def test__calculate(self):
        """Flooding calculate support function returns correct flood potential
        classes"""
        fp = nv.Flooding()
        fp._calculate(depth=np.array([1, 2, 3], dtype="uint8"), frequency="T25",
                      period="winter", duration=1)
        np.testing.assert_equal(np.array([3, 3, 3]), fp._veg[1])
        assert fp._veg[1].dtype == np.int8

    def test__calculate_nodata(self):
        """Flooding calculate support function returns correct flood potential
        classes with no data values in depth input"""
        fp = nv.Flooding()
        fp._calculate(depth=np.array([1, 2, 3, 255], dtype="uint8"), frequency="T25",
                      period="winter", duration=1)
        np.testing.assert_equal(np.array([3, 3, 3, -99]), fp._veg[1])
        assert fp._veg[1].dtype == np.int8

    def test_calculate_asc(self, path_testcase):
        """Flooding calculate function returns correct flood potential
        classes from depth input grid"""
        fp = nv.Flooding()
        fp.calculate(path_testcase / "flooding" / "ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)
        with rasterio.open(
                path_testcase / "flooding" / "result" / "F25-T10-P1-winter.asc") as dst:
            expected = dst.read(1)
        np.testing.assert_equal(expected, fp._veg[25])
        assert fp._veg[25].dtype == np.int8

    @pytest.mark.xfail
    def test_calculate_arcgis(self, path_testcase, path_testdata):
        # note this tests uses an arcgis raster with only 8bit unsigned values
        fp = nv.Flooding()
        fp.calculate(path_testdata / "ff_bt_t10_h", "T10",
                     period="winter", duration=1)
        with rasterio.open(
                path_testcase / "flooding" / "result" / "F25-T10-P1-winter.asc") as dst:
            expected = dst.read(1)
        np.testing.assert_equal(expected, fp._veg[25])

    def test_calculate_nodata(self, path_testdata):
        fp = nv.Flooding()
        fp.calculate(path_testdata / "depths_with_nodata.asc", "T10",
                     period="winter", duration=1)
        unique = []
        for i in fp._veg:
            unique.append(np.unique(fp._veg[i]))
        unique = np.unique(np.hstack(unique))
        expected = np.array([-99, 0, 1, 2, 3, 4])
        np.testing.assert_equal(set(expected), set(unique))

    def test_table(self, path_testcase):
        fp = nv.Flooding()
        with pytest.raises(FloodingException):
            fp.table

        fp.calculate(depth_file_path=path_testcase / "flooding" / "ff_bt_t10_h.asc",
                     frequency="T10", period="winter", duration=1)
        df = fp.table
        sel = df[((df.vegetation == 1)
                  & (df.presence == "goed combineerbaar"))]
        assert np.all(178.64 == np.round(sel["area_ha"], 2))

    def test_plot(self, path_testcase):
        import matplotlib as mpl
        mpl.use('agg')

        import matplotlib.pyplot as plt
        plt.show = lambda: None

        fp = nv.Flooding()
        fp.calculate(path_testcase / "flooding" / "ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)
        fp.plot(7)

        with pytest.raises(FloodingException):
            fp.plot(2000)

    def test_write(self, path_testcase, tmp_path, caplog):
        fp = nv.Flooding()
        with pytest.raises(FloodingException):
            # Should fail - model not yet run
            fp.write(str(tmp_path))

        fp.calculate(depth_file_path=path_testcase / "flooding" / "ff_bt_t10_h.asc",
                     frequency="T10", period="winter", duration=1)

        fp.write(str(tmp_path))

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
            'F21-T10-P1-winter.tif', 'F28-T10-P1-winter.tif',
            'summary.csv'
        ]

        dir = os.listdir(tmp_path)

        assert Counter(list(expected_files)) == Counter(list(dir))

        # try writing again, should raise as files already exist
        with pytest.raises(FloodingException):
            fp.write(str(tmp_path))

        fp.write(str(tmp_path), overwrite_files=True)
        assert "already exists" in caplog.text


    def test_combine(self, path_testcase, path_tests):
        fp = nv.Flooding()

        myniche = nv.Niche()
        input_path = path_testcase / "dijle"
        myniche.set_input("soil_code", input_path / "bodemv.asc")
        myniche.set_input("msw", input_path / "gvg_0_cm.asc")
        myniche.set_input("mlw", input_path / "glg_0_cm.asc")
        myniche.set_input("mhw", input_path / "ghg_0_cm.asc")
        myniche.set_input("seepage", input_path / "kwel_mm_dag.asc")

        myniche.set_input("management", input_path / "beheer_int.asc")

        myniche.set_input("nitrogen_atmospheric",input_path / "depositie_def.asc")
        myniche.set_input("nitrogen_animal", input_path / "bemest_dier.asc")

        myniche.set_input("nitrogen_fertilizer", input_path / "bemest_kunst.asc")

        myniche.set_input("inundation_vegetation", input_path / "overstr_veg.asc")
        myniche.set_input("inundation_acidity", input_path / "ovrstr_t10_50.asc")
        myniche.set_input("inundation_nutrient", input_path / "ovrstr_t10_50.asc")

        myniche.set_input("minerality", input_path / "minerality.asc")

        myniche.set_input("rainwater", input_path / "nulgrid.asc")

        with pytest.raises(FloodingException):
            # niche model not yet run
            fp.combine(myniche)

        myniche.run()
        with pytest.raises(FloodingException):
            # floodplain model not yet run
            fp.combine(myniche)

        fp.calculate(path_testcase / "flooding" / "ff_bt_t10_h.asc", "T10",
                     period="winter", duration=1)

        small = nv.Niche()
        small.run_config_file(path_tests / "small.yaml")
        with pytest.raises(FloodingException):
            # floodplain has different spatial extent than niche
            fp.combine(small)

        result = fp.combine(myniche)

        # get unique values for every vegtype
        unique = []
        for i in result._veg:
            unique.append(np.unique(result._veg[i]))
        unique = np.unique(np.hstack(unique))
        expected = np.array([-1, 1, 2, 3, -99])
        np.testing.assert_equal(set(expected), set(unique))
