from unittest import TestCase

import numpy as np
import rasterio

import niche_vlaanderen


class TestNutrientLevel:

    def test_nitrogen_mineralisation(self):
        soil_code = np.array([14])
        msw = np.array([-33])
        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate_mineralisation(soil_code, msw)
        np.testing.assert_equal(np.array([75]), result)

    def test_borders(self):
        soil_code = np.array([7, 7, 7, 7, 7])
        msw = np.array([-4, -5, -7, -10, -11])
        nl = niche_vlaanderen.NutrientLevel()
        result_nm = nl._calculate_mineralisation(soil_code, msw)
        expected_nm = np.array([50, 50, 55, 55, 76])
        np.testing.assert_equal(expected_nm, result_nm)
        nuls = np.array([0, 0, 0, 0, 0])
        # we want to check the boundaries ]156, 293]
        nitrogen_sum = np.array([155, 156, 200, 293, 294])
        # so we substract the nitrogen_sum from the expected mineralisation
        nitrogen_animal = nitrogen_sum - expected_nm
        management = np.array([2, 2, 2, 2, 2])
        result = nl.calculate(soil_code=soil_code,
                              msw=msw,
                              management=management,
                              nitrogen_animal=nitrogen_animal,
                              nitrogen_atmospheric=nuls,
                              nitrogen_fertilizer=nuls,
                              inundation=nuls)
        expected = np.array([2, 2, 3, 3, 4])
        np.testing.assert_equal(expected, result)

    def test__get(self):

        management = np.array([2])
        soil_code = np.array([14])
        nitrogen = np.array([445])
        inundation = np.array([1])

        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate(management, soil_code, nitrogen, inundation)
        np.testing.assert_equal(np.array(5), result)

    def test_calculate(self):
        nl = niche_vlaanderen.NutrientLevel()
        management = np.array([2])
        soil_code = np.array([14])
        msw = np.array([-33])
        nitrogen_deposition = np.array([20])
        nitrogen_animal = np.array([350])
        nitrogen_fertilizer = np.array([0])
        inundation = np.array([1])
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation)

        np.testing.assert_equal(np.array([5]), result)

    def test_nutrient_level_testcase(self, path_testcase):
        n = niche_vlaanderen.Niche()

        input_folder_path = path_testcase / "zwarte_beek" / "input"

        # Set all inputs required for the nutrient-level calculation
        soil_code_file_path = input_folder_path / "soil_code.asc"
        n.set_input("soil_code", soil_code_file_path)
        soil_code = n.read_rasterio_to_grid(soil_code_file_path,
                                            variable_name="soil_code")

        msw_file_path = input_folder_path / "msw.asc"
        n.set_input("msw", msw_file_path)
        msw = n.read_rasterio_to_grid(msw_file_path, variable_name="msw")

        na_file_path = input_folder_path / "nitrogen_atmospheric.asc"
        n.set_input("nitrogen_atmospheric", na_file_path)
        nitrogen_deposition = n.read_rasterio_to_grid(na_file_path,
                                                      variable_name="nitrogen_atmospheric")

        nanimal_file_path = input_folder_path / "nullgrid.asc"
        n.set_input("nitrogen_animal", nanimal_file_path)
        nitrogen_animal = n.read_rasterio_to_grid(nanimal_file_path,
                                                  variable_name="nitrogen_animal")

        nfertil_file_path = input_folder_path / "nullgrid.asc"
        n.set_input("nitrogen_fertilizer", nfertil_file_path)
        nitrogen_fertilizer = n.read_rasterio_to_grid(nfertil_file_path,
                                                      variable_name="nitrogen_fertilizer")

        in_file_path = input_folder_path / "inundation.asc"
        n.set_input("inundation_nutrient", in_file_path)
        inundation_nutrient = n.read_rasterio_to_grid(in_file_path,
                                                      variable_name="inundation_nutrient")

        management_file_path = input_folder_path / "management.asc"
        n.set_input("management", management_file_path)
        management = n.read_rasterio_to_grid(management_file_path, variable_name="management")

        nl = niche_vlaanderen.NutrientLevel()

        # Read the expected nutrient-level result
        nutrient_file_path = path_testcase / "zwarte_beek" / "abiotic" / "nutrient_level.asc"
        n.set_input("nutrient_level", nutrient_file_path)
        nutrient_level = n.read_rasterio_to_grid(nutrient_file_path, variable_name="nutrient_level")

        # Compare calculated result with expected result
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation_nutrient)

        np.testing.assert_equal(nutrient_level, result)
