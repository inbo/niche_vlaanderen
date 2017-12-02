from unittest import TestCase
import pytest

import niche_vlaanderen
from niche_vlaanderen.niche import NicheException, TypeException
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

    @pytest.mark.skipif(sys.platform == "win32",
                        reason="fails on win32 - fixed in recent rasterio")
    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        with pytest.raises(RasterioIOError):
            result = n.set_input("msw", "nonexistingfile")

    def test_invalid_input_type(self):
        n = niche_vlaanderen.Niche()
        with pytest.raises(TypeException):
            result = n.set_input("bla",
                                 "testcase/zwarte_beek/input/soil_code.asc")

    def create_zwarte_beek_niche(self):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/zwarte_beek/input/soil_code.asc")
        myniche.set_input("mhw", "testcase/zwarte_beek/input/mhw.asc")
        myniche.set_input("mlw", "testcase/zwarte_beek/input/mlw.asc")
        myniche.set_input("msw", "testcase/zwarte_beek/input/msw.asc")
        myniche.set_input("conductivity",
                          "testcase/zwarte_beek/input/conductivity.asc")
        myniche.set_input("nitrogen_atmospheric",
                          "testcase/zwarte_beek/input/nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal",
                          0)
        myniche.set_input("nitrogen_fertilizer",
                          0)
        myniche.set_input("management",
                          "testcase/zwarte_beek/input/management.asc")
        myniche.set_input("inundation_nutrient",
                          "testcase/zwarte_beek/input/inundation.asc")
        myniche.set_input("inundation_acidity",
                          "testcase/zwarte_beek/input/inundation.asc")
        myniche.set_input("seepage", "testcase/zwarte_beek/input/seepage.asc")
        myniche.set_input("rainwater",
                          "testcase/zwarte_beek/input/rainwater.asc")
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

        myniche.set_input("management_vegetation",
                          "testcase/zwarte_beek/input/management.asc")
        myniche.run()
        o2 = myniche.occurrence
        o2 = pd.DataFrame(o2, index=[0])

        myniche.set_input("inundation_vegetation",
                          "testcase/zwarte_beek/input/inundation.asc")
        myniche.run()
        o3 = myniche.occurrence
        o3 = pd.DataFrame(o3, index=[0])

        self.assertTrue(np.all(o1>=o2))
        self.assertTrue(np.all(o2>=o3))

        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        # check tempdir contains the vegation and the abiotic files
        expected_files = ["nutrient_level.tif", "acidity.tif",
             'V1.tif', 'V2.tif', 'V3.tif', 'V4.tif', 'V5.tif', 'V6.tif',
             'V7.tif', 'V8.tif', 'V9.tif', 'V10.tif', 'V11.tif', 'V12.tif',
             'V13.tif', 'V14.tif', 'V15.tif', 'V16.tif', 'V17.tif', 'V18.tif',
             'V19.tif', 'V20.tif', 'V21.tif', 'V22.tif', 'V23.tif', 'V24.tif',
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif', 'log.txt']

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
        TODO no actual validation is done!

        """

        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/zwarte_beek/input/soil_code.asc")
        myniche.set_input("mhw", "testcase/zwarte_beek/input/mhw.asc")
        myniche.set_input("mlw", "testcase/zwarte_beek/input/mlw.asc")
        myniche.run(full_model=False)
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        # check tempdir contains the vegation and the abiotic files
        expected_files = [
             'V1.tif', 'V2.tif', 'V3.tif', 'V4.tif', 'V5.tif', 'V6.tif',
             'V7.tif', 'V8.tif', 'V9.tif', 'V10.tif', 'V11.tif', 'V12.tif',
             'V13.tif', 'V14.tif', 'V15.tif', 'V16.tif', 'V17.tif', 'V18.tif',
             'V19.tif', 'V20.tif', 'V21.tif', 'V22.tif', 'V23.tif', 'V24.tif',
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif', 'log.txt']

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)

    def create_small(self):
        myniche = niche_vlaanderen.Niche()

        input_dir = "tests/data/"
        myniche.set_input("mhw", input_dir + "mhw_small.asc")
        myniche.set_input("mlw", input_dir + "mlw_small.asc")
        myniche.set_input("msw", "tests/data/msw_small.asc")
        myniche.set_input("soil_code", input_dir + "soil_code_small.asc")

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
            os.path.join(tmpdir, 'V1.tif')]
        ).decode('utf-8')
        print(info)
        assert ("(216580.000000000000000,198580.000000000000000)" in
                info)
        assert ("STATISTICS_MAXIMUM=1" in info)
        assert ("STATISTICS_MINIMUM=0" in info)

        shutil.rmtree(tmpdir)

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
        self.assertTrue ("STATISTICS_MAXIMUM=9" in info)
        self.assertTrue ("STATISTICS_MINIMUM=0" in info)
        shutil.rmtree(tmpdir)

    def test_read_configuration(self):
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.read_config_input(config)
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
        myniche.set_input("mhw", "tests/data/msw_small.asc")
        with pytest.raises(NicheException):
            myniche.run()  # incomplete, keys are missing
        with pytest.raises(NicheException):
            myniche.write("_temp")  # should raise, no calculation done

    def test_mxw_validation(self):
        myniche = self.create_small()
        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 0)
        with pytest.raises(NicheException):
            myniche.run()

        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 10)
        myniche.set_input("msw", 3)
        with pytest.raises(NicheException):
            myniche.run()

        myniche.set_input("mhw", 3)
        myniche.set_input("mlw", 5)
        myniche.set_input("msw", 10)
        with pytest.raises(NicheException):
            myniche.run()

    def test_run_configuration_abiotic(self):
        config = 'tests/small_abiotic.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def overwrite_codetable(self):
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.read_config_input(config)
        myniche.set_input('ct_acidity', 'system_tables/acidity.asc')
        myniche.run()

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


class TestNicheDelta(TestCase):
    def test_simplevsfull(self):
        config = 'tests/small_simple.yaml'
        simple = niche_vlaanderen.Niche()
        simple.run_config_file(config)

        config_full = "tests/small.yaml"
        full = niche_vlaanderen.Niche()
        full.run_config_file(config_full)

        delta = niche_vlaanderen.NicheDelta(simple, full)

        self.assertEqual(0, delta.table["only in model 2"].sum())


