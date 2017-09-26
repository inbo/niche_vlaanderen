from unittest import TestCase


import niche_vlaanderen

import tempfile
import shutil


import pytest

class testNiche(TestCase):

    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        result = n.set_input("msw", "nonexistingfile")
        self.assertEqual(False, result)

    def test_testcase(self):
        """
        This tests runs the data from the testcase. Note no validation is done on the output - we just check nothing
        goes wrong for now.

        """

        myniche = niche_vlaanderen.Niche()
        myniche.set_input("soil_code", "testcase/input/soil_codes.asc", set_spatial_context=True)
        myniche.set_input("mhw", "testcase/input/mhw.asc")
        myniche.set_input("mlw", "testcase/input/mlw.asc")
        myniche.set_input("msw", "testcase/input/msw.asc")
        myniche.set_input("msw", "testcase/input/msw.asc")
        myniche.set_input("conductivity", "testcase/input/conductivity.asc")
        myniche.set_input("nitrogen_atmospheric", "testcase/input/nitrogen_atmospheric.asc")
        myniche.set_input("nitrogen_animal", "testcase/input/nitrogen_animal.asc")
        myniche.set_input("nitrogen_fertilizer", "testcase/input/nullgrid.asc")
        myniche.set_input("management", "testcase/input/management.asc")
        myniche.set_input("inundation_nutrient", "testcase/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_acidity", "testcase/input/inundation_nutrient_level.asc")
        myniche.set_input("inundation_vegetation", "testcase/input/inundation_vegetation.asc")
        myniche.set_input("seepage", "testcase/input/seepage.asc")
        myniche.set_input("rainwater", "testcase/input/nullgrid.asc")
        myniche.run()
        tmpdir = tempfile.mkdtemp()
        myniche.write(tmpdir)
        shutil.rmtree(tmpdir)