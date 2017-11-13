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
                                 "testcase/grote_nete/input/soil_code.asc")

    def create_grote_nete_niche(self):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/grote_nete/input/soil_code.asc")
        myniche.set_input("mhw", "testcase/grote_nete/input/mhw.asc")
        myniche.set_input("mlw", "testcase/grote_nete/input/mlw.asc")
        myniche.set_input("msw", "testcase/grote_nete/input/msw.asc")
        myniche.set_input("conductivity",
                          "testcase/grote_nete/input/conductivity.asc")
        myniche.set_input("nitrogen_atmospheric",
                          "testcase/grote_nete/input/nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal",
                          "testcase/grote_nete/input/nitrogen_animal.asc")
        myniche.set_input("nitrogen_fertilizer",
                          "testcase/grote_nete/input/nullgrid.asc")
        myniche.set_input("management",
                          "testcase/grote_nete/input/management.asc")
        myniche.set_input("inundation_nutrient",
                          "testcase/grote_nete/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_acidity",
                          "testcase/grote_nete/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_vegetation",
                          "testcase/grote_nete/input/inundation_vegetation.asc")
        myniche.set_input("seepage", "testcase/grote_nete/input/seepage.asc")
        myniche.set_input("rainwater",
                          "testcase/grote_nete/input/nullgrid.asc")
        return myniche

    def test_grote_nete(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!

        """

        myniche = self.create_grote_nete_niche()

        myniche.run()

        o1 = myniche.occurrence
        o1 = pd.DataFrame(o1, index=[0])

        myniche.set_input("management_vegetation",
                          "testcase/grote_nete/input/management.asc")
        myniche.run()
        o2 = myniche.occurrence
        o2 = pd.DataFrame(o2, index=[0])

        myniche.set_input("inundation_vegetation",
                          "testcase/grote_nete/input/inundation_vegetation.asc")
        myniche.run()
        o3 = myniche.occurrence
        o3 = pd.DataFrame(o3, index=[0])

        self.assertTrue(np.all(o1>=o2))
        self.assertTrue(np.all(o3>=o2))

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

    def test_grote_nete_constant_values(self):
        myniche = self.create_grote_nete_niche()
        myniche.set_input("rainwater", 0)
        self.assertFalse("rainwater" in myniche._inputfiles)
        myniche.set_input("nitrogen_fertilizer", 0)

        myniche.run()
        myniche2 = self.create_grote_nete_niche()
        myniche2.run()
        self.assertEqual(myniche.occurrence, myniche2.occurrence)

    def test_testcase_simple(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!

        """

        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/grote_nete/input/soil_code.asc")
        myniche.set_input("mhw", "testcase/grote_nete/input/mhw.asc")
        myniche.set_input("mlw", "testcase/grote_nete/input/mlw.asc")
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

    def create_grobbendonk_niche(self):
        myniche = niche_vlaanderen.Niche()
        input = "testcase/grobbendonk/input/"
        myniche.set_input("soil_code",
                          input + "soil_code.asc")
        myniche.set_input("mhw", input + "mhw_correct2.asc")
        myniche.set_input("mlw", input + "mlw.asc")
        myniche.set_input("msw", input + "msw_correct.asc")
        myniche.set_input("conductivity",
                          input + "conductivity.asc")
        myniche.set_input("nitrogen_atmospheric",
                          input + "nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal",
                          input + "nitrogen_animal.asc")
        myniche.set_input("nitrogen_fertilizer",
                          "testcase/grobbendonk/input/nullgrid.asc")
        myniche.set_input("management",
                          input + "management.asc")
        myniche.set_input("inundation_nutrient",
                          input + "inundation_nutrient.asc")
        myniche.set_input("inundation_acidity",
                          input + "inundation_nutrient.asc")
        myniche.set_input("seepage", input + "seepage.asc")
        myniche.set_input("rainwater", input + "nullgrid.asc")
        return myniche

    def create_grobbendonk_small(self):
        # note we add one small grid here, so the spatial extent is small
        # and the test much faster
        myniche = self.create_grobbendonk_niche()
        myniche.set_input("msw", "tests/data/msw_small.asc")

        return myniche

    def test_grobbendonk(self):
        """
        This tests runs the data from the testcase/grobbendonk.

        The influence of adding management and inundation is checked

        """

        myniche = self.create_grobbendonk_niche()
        myniche.run()
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        # check tempdir contains the vegation and the abiotic files
        expected_files = ["nutrient_level.tif", "acidity.tif",
             'V1.tif', 'V2.tif', 'V3.tif', 'V4.tif', 'V5.tif', 'V6.tif',
             'V7.tif', 'V8.tif', 'V9.tif', 'V10.tif', 'V11.tif', 'V12.tif',
             'V13.tif', 'V14.tif', 'V15.tif', 'V16.tif', 'V17.tif', 'V18.tif',
             'V19.tif', 'V20.tif', 'V21.tif', 'V22.tif', 'V23.tif', 'V24.tif',
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif','log.txt']

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)

    @pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")

    def test_grobbendonk_validate(self):
        myniche = self.create_grobbendonk_niche()
        myniche.run()
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)

        info = subprocess.check_output(
            ["gdalinfo",
             "-stats",
            os.path.join(tmpdir, 'V1.tif')]
        ).decode('utf-8')
        assert ("Origin = (164937.500000000000000,216162.500000000000000)" in
                info)
        assert ("STATISTICS_MAXIMUM=1" in info)
        assert ("STATISTICS_MINIMUM=0" in info)

        shutil.rmtree(tmpdir)

    def test_deviation(self):
        n = self.create_grobbendonk_niche()
        n.run(deviation=True)
        # check dict exists and contains enough nan values
        self.assertEqual(276072, np.isnan(n._deviation["mhw_04"]).sum())

    @pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")

    def test_write_deviation(self):
        n = self.create_grobbendonk_niche()
        n.run(deviation=True)

        tmpdir = tempfile.mkdtemp()
        n.write(tmpdir)
        info = subprocess.check_output(
            ["gdalinfo",
             "-stats",
            os.path.join(tmpdir, 'mhw_04.tif')]
        ).decode('utf-8')
        self.assertTrue(
            "Origin = (164937.500000000000000,216162.500000000000000)" in
                info)
        self.assertTrue ("STATISTICS_MAXIMUM=1051" in info)
        self.assertTrue ("STATISTICS_MINIMUM=-100" in info)
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
        myniche = self.create_grobbendonk_small()
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

    def rereadoutput(self):
        """
        This tests checks if the output written by the model is a valid input
        for a new run
        """
        config = 'tests/small_simple.yaml'
        myniche = niche_vlaanderen.Niche()
        myniche.run(config)
        myniche = niche_vlaanderen.Niche()
        config = '_output/log.txt'
        myniche.run(config)

