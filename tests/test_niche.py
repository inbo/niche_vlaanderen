from unittest import TestCase
import pytest

import niche_vlaanderen
import numpy as np
import pandas as pd

import tempfile
import shutil
import os
import sys

import distutils.spawn
import subprocess

class testNiche(TestCase):

    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        result = n.set_input("msw", "nonexistingfile")
        self.assertEqual(False, result)

        result = n.set_input("msw", "tests/data/invalid.asc")
        self.assertEqual(False, result)


    def create_grote_nete_niche(self):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/grote_nete/input/soil_codes.asc",
                          set_spatial_context=True)
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
        myniche.set_input("management", "testcase/grote_nete/input/management.asc")
        myniche.set_input("inundation_nutrient",
                          "testcase/grote_nete/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_acidity",
                          "testcase/grote_nete/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_vegetation",
                          "testcase/grote_nete/input/inundation_vegetation.asc")
        myniche.set_input("seepage", "testcase/grote_nete/input/seepage.asc")
        myniche.set_input("rainwater", "testcase/grote_nete/input/nullgrid.asc")
        return myniche

    def test_grote_nete(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!

        """

        myniche = self.create_grote_nete_niche()

        myniche.run()

        o1 = myniche.occurence
        o1 = pd.DataFrame(o1, index=[0])

        myniche.set_input("management_vegetation",
                          "testcase/grote_nete/input/management.asc")
        myniche.run()
        o2 = myniche.occurence
        o2 = pd.DataFrame(o2, index=[0])

        myniche.set_input("inundation_vegetation",
                          "testcase/grote_nete/input/inundation_vegetation.asc")
        myniche.run()
        o3 = myniche.occurence
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
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif']

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)

    def test_testcase_simple(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!
  
        """

        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/grote_nete/input/soil_codes.asc",
                          set_spatial_context=True)
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
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif']

        dir = os.listdir(tmpdir)

        if sys.version_info < (3, 2):
            self.assertItemsEqual(expected_files, dir)
        else:
            self.assertCountEqual(expected_files, dir)

        shutil.rmtree(tmpdir)
        
    def create_grobbendonk_niche(self):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code",
                          "testcase/grobbendonk/input/soil_codes.asc",
                          set_spatial_context=True)
        myniche.set_input("mhw", "testcase/grobbendonk/input/mhw_correct2.asc")
        myniche.set_input("mlw", "testcase/grobbendonk/input/mlw.asc")
        myniche.set_input("msw", "testcase/grobbendonk/input/msw_correct.asc")
        myniche.set_input("conductivity",
                          "testcase/grobbendonk/input/conductivity.asc")
        myniche.set_input("nitrogen_atmospheric",
                          "testcase/grobbendonk/input/nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal",
                          "testcase/grobbendonk/input/nitrogen_animal.asc")
        myniche.set_input("nitrogen_fertilizer",
                          "testcase/grobbendonk/input/nullgrid.asc")
        myniche.set_input("management",
                          "testcase/grobbendonk/input/management.asc")
        myniche.set_input("inundation_nutrient",
                          "testcase/grobbendonk/input/inundation_nutrient.asc")
        myniche.set_input("inundation_acidity",
                          "testcase/grobbendonk/input/inundation_nutrient.asc")
        myniche.set_input("seepage",
                          "testcase/grobbendonk/input/seepage.asc")
        myniche.set_input("rainwater",
                          "testcase/grobbendonk/input/nullgrid.asc")
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
             'V25.tif', 'V26.tif', 'V27.tif', 'V28.tif']

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

    def test_difference(self):
        n = self.create_grobbendonk_niche()
        n.calculate_difference()
        # check dict exists and contains enough nan values
        self.assertEqual(276072, np.isnan(n._difference["mhw_04"]).sum())

    @pytest.mark.skipif(
        distutils.spawn.find_executable("gdalinfo") is None,
        reason="gdalinfo not available in the environment.")

    def test_write_difference(self):
        n = self.create_grobbendonk_niche()
        n.calculate_difference()

        tmpdir = tempfile.mkdtemp()
        n.write_difference(tmpdir)
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
