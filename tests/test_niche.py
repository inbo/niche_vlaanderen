from unittest import TestCase


import niche_vlaanderen

import tempfile
import shutil
import os
import sys


class testNiche(TestCase):

    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        result = n.set_input("msw", "nonexistingfile")
        self.assertEqual(False, result)

    def test_testcase(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!

        # on linux this could be done with gdalcompare.py

        """

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

    def test_testcase(self):
        """
        This tests runs the data from the testcase/grote_nete.
        TODO no actual validation is done!

        # on linux this could be done with gdalcompare.py

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