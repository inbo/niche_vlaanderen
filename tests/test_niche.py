from __future__ import division
from unittest import TestCase
import pytest

import niche_vlaanderen
from niche_vlaanderen.exception import NicheException
from rasterio.errors import RasterioIOError
import numpy as np
import pandas as pd

import tempfile
import shutil
import os
import sys

import distutils.spawn
import subprocess


class TestNiche(TestCase):

    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        with pytest.raises(RasterioIOError):
            n.set_input("msw", "nonexistingfile")

    def test_invalid_input_type(self):
        n = niche_vlaanderen.Niche()
        with pytest.raises(NicheException):
            n.set_input("bla", "testcase/zwarte_beek/input/soil_code.asc")

    @staticmethod
    def create_zwarte_beek_niche():
        myniche = niche_vlaanderen.Niche()
        input_dir = "testcase/zwarte_beek/input/"
        myniche.set_input("soil_code", input_dir + "soil_code.asc")
        myniche.set_input("mhw", input_dir + "mhw.asc")
        myniche.set_input("mlw", input_dir + "mlw.asc")
        myniche.set_input("msw", input_dir + "msw.asc")
        myniche.set_input("minerality",
                          input_dir + "minerality.asc")
        myniche.set_input("nitrogen_atmospheric",
                          input_dir + "nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal",
                          0)
        myniche.set_input("nitrogen_fertilizer",
                          0)
        myniche.set_input("management",
                          input_dir + "management.asc")
        myniche.set_input("inundation_nutrient",
                          input_dir + "inundation.asc")
        myniche.set_input("inundation_acidity",
                          input_dir + "inundation.asc")
        myniche.set_input("seepage", input_dir + "seepage.asc")
        myniche.set_input("rainwater",
                          input_dir + "rainwater.asc")
        return myniche

    def test_zwarte_beek(self):
        """
        This tests runs the data from the testcase/zwarte_beek.
        TODO no actual validation is done!

        """

        myniche = self.create_zwarte_beek_niche()

        myniche.run()

        o1 = myniche.occurrence
        o1 = pd.DataFrame(o1, index=[0])

        input_dir = "testcase/zwarte_beek/input/"

        myniche.set_input("management_vegetation",
                          input_dir + "management.asc")
        myniche.run()
        o2 = myniche.occurrence
        o2 = pd.DataFrame(o2, index=[0])

        myniche.set_input("inundation_vegetation",
                          input_dir + "inundation.asc")
        myniche.run()
        o3 = myniche.occurrence
        o3 = pd.DataFrame(o3, index=[0])

        self.assertTrue(np.all(o1 >= o2))
        self.assertTrue(np.all(o2 >= o3))

        tmpdir = tempfile.mkdtemp()
        # if a subdir does not exist - it should be created
        tmpdir = tmpdir + '/subdir'
        myniche.write(tmpdir)
        # check tempdir contains the vegetation and the abiotic files
        expected_files = [
            "nutrient_level.tif", "acidity.tif",
            'V01.tif', 'V02.tif', 'V03.tif', 'V04.tif', 'V05.tif', 'V06.tif',
            'V07.tif', 'V08.tif', 'V09.tif', 'V10.tif', 'V11.tif', 'V12.tif',
            'V13.tif', 'V14.tif', 'V15.tif', 'V16.tif', 'V17.tif', 'V18.tif',
            'V19.tif', 'V20.tif', 'V21.tif', 'V22.tif', 'V23.tif', 'V24.tif',
            'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif', 'log.txt',
            'summary.csv']

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)

    def test_zwarte_beek_constant_values(self):
        myniche = self.create_zwarte_beek_niche()
        myniche.set_input("rainwater", 0)
        self.assertFalse("rainwater" in myniche._inputfiles)
        myniche.set_input("nitrogen_fertilizer", 0)

        myniche.run()
        myniche2 = self.create_zwarte_beek_niche()
        myniche2.run()
        self.assertEqual(myniche.occurrence, myniche2.occurrence)

    def test_testcase_simple(self):
        """
        This tests runs the data from the testcase/zwarte_beek.
        Note: validation is done in the vegetation tests - not here.

        """

        myniche = niche_vlaanderen.Niche()
        input_dir = "testcase/zwarte_beek/input/"

        myniche.set_input("soil_code",
                          input_dir + "soil_code.asc")
        myniche.set_input("mhw", input_dir + "mhw.asc")
        myniche.set_input("mlw", input_dir + "mlw.asc")
        myniche.name = "simple"
        myniche.run(full_model=False)
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        # check tempdir contains the vegation and the abiotic files
        expected_files = [
             'V01.tif', 'V02.tif', 'V03.tif', 'V04.tif', 'V05.tif', 'V06.tif',
             'V07.tif', 'V08.tif', 'V09.tif', 'V10.tif', 'V11.tif', 'V12.tif',
             'V13.tif', 'V14.tif', 'V15.tif', 'V16.tif', 'V17.tif', 'V18.tif',
             'V19.tif', 'V20.tif', 'V21.tif', 'V22.tif', 'V23.tif', 'V24.tif',
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif', 'log.txt',
             'summary.csv']

        expected_files = ["simple_" + i for i in expected_files]

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)

    @staticmethod
    def create_small():
        myniche = niche_vlaanderen.Niche()
        myniche.read_config_file("tests/small.yaml")
        return myniche

    @pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")
    def test_zwarte_beek_validate(self):
        myniche = self.create_zwarte_beek_niche()
        myniche.run()
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)

        info = subprocess.check_output(
            ["gdalinfo",
             "-stats",
             os.path.join(tmpdir, 'V01.tif')]
        ).decode('utf-8')
        print(info)
        assert ("(216580.000000000000000,198580.000000000000000)" in
                info)
        assert ("STATISTICS_MAXIMUM=1" in info)
        assert ("STATISTICS_MINIMUM=0" in info)

        shutil.rmtree(tmpdir)

    def test_windowed_read(self):
        # tests whether the spatial context is adjusted to the smaller grid
        myniche = self.create_zwarte_beek_niche()
        myniche.set_input("mlw", "tests/data/part_zwarte_beek_mlw.asc")
        myniche.run(full_model=True)
        self.assertEqual(37, myniche._context.width)
        self.assertEqual(37, myniche._context.height)

    def test_deviation(self):
        n = self.create_zwarte_beek_niche()
        n.run(deviation=True)
        # check dict exists and contains enough nan values
        self.assertEqual(14400, np.isnan(n._deviation["mhw_04"]).sum())

    @pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")
    def test_write_deviation(self):
        n = self.create_small()
        n.run(deviation=True, full_model=False)

        tmpdir = tempfile.mkdtemp()
        n.write(tmpdir)
        info = subprocess.check_output(
            ["gdalinfo",
             "-stats",
             os.path.join(tmpdir, 'mhw_04.tif')]
        ).decode('utf-8')
        print(info)
        self.assertTrue(
            "Origin = (172762.500000000000000,210637.500000000000000)" in
            info)
        self.assertTrue("STATISTICS_MAXIMUM=9" in info)
        self.assertTrue("STATISTICS_MINIMUM=0" in info)
        shutil.rmtree(tmpdir)

    def test_read_configuration(self):
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.read_config_file(config)
        myniche.run(full_model=False)

    def test_run_configuration(self):
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def test_run_configuration_numeric(self):
        config = 'tests/small_ct.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def test_incomplete_model(self):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("mhw", "tests/data/small/msw.asc")
        with pytest.raises(NicheException):
            myniche.run()  # incomplete, keys are missing
        with pytest.raises(NicheException):
            myniche.write("_temp")  # should raise, no calculation done

    def test_mxw_validation(self):
        myniche = self.create_small()
        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 0)

        with pytest.raises(NicheException):
            myniche.run(full_model=False)

        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 10)
        myniche.set_input("msw", 3)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

        myniche.set_input("mhw", 3)
        myniche.set_input("mlw", 5)
        myniche.set_input("msw", 10)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

        myniche.set_input("mhw", 3)
        myniche.set_input("mlw", 5)
        myniche.set_input("msw", 10)
        myniche.run(full_model=True, strict_checks=False)
        # should not raise

    def test_mxw_validation_yml(self):
        myniche = niche_vlaanderen.Niche()
        # should not raise
        myniche.run_config_file("tests/small_nostrict.yml")

        n2 = niche_vlaanderen.Niche()
        n2.read_config_file("tests/small_nostrict.yml")
        with pytest.raises(NicheException):
            n2.run()

    def test_nitrogen_validation(self):
        myniche = self.create_small()
        myniche.set_input("nitrogen_animal", 10001)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

    def test_run_configuration_abiotic(self):
        config = 'tests/small_abiotic.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def test_run_abiotic_error(self):
        myniche = self.create_small()
        with pytest.raises(NicheException):
            myniche.run(abiotic=True)

        myniche.set_input("nutrient_level", 1)
        myniche.set_input("acidity", 1)

        with pytest.raises(NicheException):
            myniche.run(abiotic=True, full_model=False)

        myniche.run(abiotic=True)

    def test_rereadoutput(self):
        """
        This tests checks if the output written by the model is a valid input
        for a new run
        """
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)
        myniche = niche_vlaanderen.Niche()

        shutil.copy('_output/log.txt', 'log.txt')

        config = 'log.txt'
        myniche2 = niche_vlaanderen.Niche()
        myniche2.run_config_file(config)

    def test_overwrite_code_table(self):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation="tests/data/bad_ct/one_vegetation.csv")

        myniche.set_input("mhw", "tests/data/small/mhw.asc")
        myniche.set_input("mlw", "tests/data/small/mlw.asc")
        myniche.set_input("soil_code", "tests/data/small/soil_code.asc")
        myniche.run(full_model=False)

        # we expect only one vegetation type, as the codetable has only one
        self.assertEqual(1, len(myniche.occurrence))

        # we try to overwrite using a non existing key
        with pytest.raises(NicheException):
            myniche._set_ct("bla", "tests/data/bad_ct/one_vegetation.csv")

        # we try to overwrite using a non existing codetable
        with pytest.raises(NicheException):
            myniche._set_ct("ct_vegetation", "nonexisting")

    def test_repr(self):
        myniche = self.create_small()
        str = myniche.__repr__()
        assert "# No model run completed." in str
        myniche.run()
        str = myniche.__repr__()
        self.assertFalse("# No model run completed." in str)

    def test_plot(self):
        """
        Tests the plot method. Note that this only tests whether a plot is
        constructed. The actual content is not tested.
        """
        import matplotlib as mpl
        mpl.use('agg')

        import matplotlib.pyplot as plt
        plt.show = lambda: None

        myniche = self.create_small()

        # try plotting before running
        myniche.plot("mhw")
        myniche.run(deviation=True)
        myniche.plot("mhw")
        myniche.plot(1)
        myniche.name = "name"
        myniche.plot(1)
        myniche.plot("mhw_01")
        myniche.plot("nutrient_level")
        with pytest.raises(NicheException):
            myniche.plot("sinterklaas")

    def test_table(self):
        myniche = self.create_small()

        with pytest.raises(NicheException):
            myniche.table

        myniche.run(full_model=False)
        print(myniche)
        res = myniche.table
        print(res)
        self.assertEqual((36, 3), res.shape)

        area_expected = 7 * 6 * 25 * 25 * 28 / 10000
        area = np.sum(res["area_ha"])

        assert area == area_expected

    def test_zonal_stats(self):
        myniche = self.create_zwarte_beek_niche()
        myniche.run(full_model=False)
        vector = "testcase/zwarte_beek/input/study_area_l72.geojson"

        # there is only one polygon
        stats = myniche.zonal_stats(vector, outside=False)

        # we expect no data to be absent as the shape is a mask
        np.testing.assert_equal(np.all(stats.presence == "no data"), False)

        # which also means that present /not present should be equal to the
        # normal table
        table = myniche.table
        sum = np.sum(stats.area_ha[(stats.presence == "present")])
        table_sum = np.sum(table.area_ha[(table.presence == "present")])
        assert table_sum == sum

        stats = myniche.zonal_stats(vector)
        # we should have nodata areas now
        assert np.any(stats.presence == "no data")

        # these should have shapeid -1 and have area approx 15.16 ha
        subset = ((stats.presence == "no data") & (stats.vegetation == 7)
                  & (stats.shape_id == -1))
        result = np.sum(stats[(subset)]["area_ha"])
        result = np.round(result, 2)
        assert 15.16 == result

    def test_uint(self):
        myniche = niche_vlaanderen.Niche()

        myniche.set_input("mhw", "tests/data/small/mhw.asc")
        myniche.set_input("mlw", "tests/data/small/mlw.asc")
        myniche.set_input("soil_code", "tests/data/tif/soil_code.tif")
        myniche.run(full_model=False)

        # this dataset should contain one nodata cell
        df = myniche.table
        assert np.all(df[df.presence == "no data"]["area_ha"] == 0.0625)

    def test_overwrite_file(self):
        myniche = self.create_small()
        myniche.run()
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        # should raise: file already exists
        with pytest.raises(NicheException):
            myniche.write(tmpdir)
        shutil.rmtree(tmpdir)

    def test_overwrite_codetable_nonexisting(self):
        # assume error - file does not exist
        with pytest.raises(NicheException):
            niche_vlaanderen.Niche(ct_vegetation="nonexisting file")

    def test_overwrite_codetable(self):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation="tests/data/bad_ct/one_vegetation_limited.csv",
            ct_acidity="tests/data/bad_ct/acidity_limited.csv",
            lnk_acidity="tests/data/bad_ct/lnk_acidity_limited.csv",
            ct_nutrient_level="tests/data/bad_ct/nutrient_level.csv")
        myniche.read_config_file("tests/small.yaml")
        myniche.run()

    def test_overwrite_codetable_nojoin(self):
        # test should generate a warning
        myniche = niche_vlaanderen.Niche(
            ct_vegetation="tests/data/bad_ct/vegetation_noinnerjoin.csv"
        )
        myniche.read_config_file("tests/small.yaml")
        with pytest.warns(UserWarning):
            myniche.run()


class TestNicheDelta(TestCase):
    def test_simplevsfull_plot(self):
        config = 'tests/small_simple.yaml'
        simple = niche_vlaanderen.Niche()
        simple.run_config_file(config)

        config_full = "tests/small.yaml"
        full = niche_vlaanderen.Niche()
        full.run_config_file(config_full)

        delta = niche_vlaanderen.NicheDelta(simple, full)

        # as the full model always contains less than the simple model,
        # we can use this in a test
        df = delta.table
        self.assertEqual(0, df[df.presence == "only in model 2"].area_ha.sum())

        import matplotlib as mpl
        mpl.use('agg')

        import matplotlib.pyplot as plt
        plt.show = lambda: None

        delta.plot(5)
        delta.name = "vergelijking"
        delta.plot(5)

    def test_simplevsfull_write(self):
        config = 'tests/small_simple.yaml'
        simple = niche_vlaanderen.Niche()
        simple.run_config_file(config)

        config_full = "tests/small.yaml"
        full = niche_vlaanderen.Niche()
        full.run_config_file(config_full)

        delta = niche_vlaanderen.NicheDelta(simple, full)

        tmpdir = tempfile.mkdtemp()
        tmpsubdir = tmpdir + "/new"
        delta.write(tmpsubdir)
        # check tempdir contains the vegetation and the abiotic files
        expected_files = [
             'D1.tif', 'D2.tif', 'D3.tif', 'D4.tif', 'D5.tif', 'D6.tif',
             'D7.tif', 'D8.tif', 'D9.tif', 'D10.tif', 'D11.tif', 'D12.tif',
             'D13.tif', 'D14.tif', 'D15.tif', 'D16.tif', 'D17.tif', 'D18.tif',
             'D19.tif', 'D20.tif', 'D21.tif', 'D22.tif', 'D23.tif', 'D24.tif',
             'D25.tif', 'D26.tif', 'D27.tif', 'D28.tif', 'legend_delta.csv',
             'delta_summary.csv']

        dir = os.listdir(tmpsubdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        delta.name = "vgl"
        delta.write(tmpsubdir)

        dir = os.listdir(tmpsubdir)
        assert 60 == len(dir)
        assert 30 == sum(f.startswith("vgl_") for f in dir)
        shutil.rmtree(tmpdir)

    def test_differentvegsize(self):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation="tests/data/bad_ct/one_vegetation.csv")

        myniche.set_input("mhw", "tests/data/small/mhw.asc")
        myniche.set_input("mlw", "tests/data/small/mlw.asc")
        myniche.set_input("soil_code", "tests/data/small/soil_code.asc")
        myniche.run(full_model=False)

        small = niche_vlaanderen.Niche()
        small.run_config_file("tests/small.yaml")

        # we try to compare but both elements have different vegetations
        with pytest.raises(NicheException):
            niche_vlaanderen.NicheDelta(small, myniche)

    def testinvalidDelta(self):
        small = niche_vlaanderen.Niche()
        with pytest.raises(NicheException):
            # should fail as there is no extent yet
            niche_vlaanderen.NicheDelta(small, small)

        small.read_config_file("tests/small_simple.yaml")
        with pytest.raises(NicheException):
            # should fail as the model has not yet been run
            niche_vlaanderen.NicheDelta(small, small)

        zwb = TestNiche.create_zwarte_beek_niche()
        zwb.run()
        small.run(full_model=False)
        # should fail due to different extent
        with pytest.raises(NicheException):
            niche_vlaanderen.NicheDelta(zwb, small)

    def test_overwrite_file(self):
        myniche = TestNiche.create_small()
        myniche.run(full_model=False)
        delta = niche_vlaanderen.NicheDelta(myniche, myniche)
        tmpdir = tempfile.mkdtemp()
        delta.write(tmpdir)
        # should raise: file already exists
        with pytest.raises(NicheException):
            delta.write(tmpdir)
        # should just warn
        delta.write(tmpdir, overwrite_files=True)
        shutil.rmtree(tmpdir)


@pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")
def test_conductivity2minerality():
    tmpdir = tempfile.mkdtemp()
    niche_vlaanderen.conductivity2minerality(
        "tests/data/small/conductivity.asc", tmpdir + "/minerality.tif")

    info = subprocess.check_output(
        ["gdalinfo", "-stats", tmpdir + "/minerality.tif"]
    ).decode('utf-8')

    assert ("STATISTICS_MAXIMUM=1" in info)
    assert ("STATISTICS_MINIMUM=0" in info)
    assert ("STATISTICS_STDDEV=0.5")
    assert ("STATISTICS_MEAN=0.5")

    shutil.rmtree(tmpdir)
