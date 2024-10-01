import numpy as np

import niche_vlaanderen


class TestNutrientLevel:

    def test_nitrogen_mineralisation(self):
        """Correct nitrogen mineralisation calculated from single-value
        grids with empty mask"""
        soil_code = np.ma.array([14], dtype="uint8")
        msw =np.ma.array([-33], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate_mineralisation(soil_code, msw)
        np.testing.assert_equal(np.ma.array([75]), result)
        assert result.dtype == np.float32

    def test_nitrogen_mineralisation_masked(self):
        """Correct nitrogen mineralisation calculated from fixed-value
        grids with non-empty mask"""
        soil_code = np.ma.array([14, 14, 255],
                                mask=[False, False, True], dtype="uint8")
        msw =np.ma.array([-33, -33, np.nan],
                         mask=[False, False, True], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate_mineralisation(soil_code, msw)
        np.testing.assert_equal(np.ma.array([75, 75, np.nan],
                                            mask=[False, False, True]), result)
        assert result.dtype == np.float32

    def test_borders(self):
        """Correct nutrient level calculated for border values"""
        soil_code = np.ma.array([7, 7, 7, 7, 7], dtype="uint8")
        msw = np.ma.array([-4, -5, -7, -10, -11], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result_nm = nl._calculate_mineralisation(soil_code, msw)
        expected_nm = np.ma.array([50, 50, 55, 55, 76])
        np.testing.assert_equal(expected_nm, result_nm)
        assert result_nm.dtype == np.float32

        nuls = np.ma.array([0, 0, 0, 0, 0])
        # we want to check the boundaries ]156, 293]
        nitrogen_sum = np.ma.array([155, 156, 200, 293, 294])
        # so we substract the nitrogen_sum from the expected mineralisation
        nitrogen_animal = nitrogen_sum - expected_nm
        management = np.ma.array([2, 2, 2, 2, 2])
        result = nl.calculate(soil_code=soil_code.astype("uint8"),
                              msw=msw.astype("float32"),
                              management=management.astype("uint8"),
                              nitrogen_animal=nitrogen_animal.astype("float32"),
                              nitrogen_atmospheric=nuls.astype("float32"),
                              nitrogen_fertilizer=nuls.astype("float32"),
                              inundation=nuls.astype("uint8"))
        expected = np.ma.array([2, 2, 3, 3, 4])
        np.testing.assert_equal(expected, result)
        assert result.dtype == np.uint8

    def test_support_calculate(self):
        """Correct nutrient level based on nitrogen mineralisation calculated
        from single-value grids with empty mask"""
        management = np.ma.array([2], dtype="uint8")
        soil_code = np.ma.array([14], dtype="uint8")
        nitrogen = np.ma.array([445], dtype="float32")
        inundation = np.ma.array([1], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate(management, soil_code, nitrogen, inundation)
        np.testing.assert_equal(np.ma.array(5), result)
        assert result.dtype == np.uint8

    def test_support_calculate_masked(self):
        """Correct nutrient level based on nitrogen mineralisation calculated
        from single-value grids with non-empty mask"""
        management = np.ma.array([2, 2, 255],
                                 mask=[False, False, True], dtype="uint8")
        soil_code = np.ma.array([14, 14, 14],
                                mask=[False, False, True], dtype="uint8")
        nitrogen = np.ma.array([445, 445, 445],
                               mask=[False, False, True], dtype="float32")
        inundation = np.ma.array([1, 1, 1],
                                 mask=[False, False, True], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl._calculate(management, soil_code, nitrogen, inundation)
        np.testing.assert_equal(np.ma.array([5, 5, 5],
                                            mask=[False, False, True]), result)
        assert result.dtype == np.uint8

    def test_calculate(self):
        """Correct nutrient level calculated from fixed-value grids with empty mask"""
        management = np.ma.array([2], dtype="uint8")
        soil_code = np.ma.array([14], dtype="uint8")
        msw = np.ma.array([-33], dtype="float32")
        nitrogen_deposition = np.ma.array([20], dtype="float32")
        nitrogen_animal = np.ma.array([350], dtype="float32")
        nitrogen_fertilizer = np.ma.array([0], dtype="float32")
        inundation = np.ma.array([1], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation)

        np.testing.assert_equal(np.array([5]), result)
        assert result.dtype == np.uint8

    def test_calculate_masked(self):
        """Correct nutrient level calculated from fixed-value grids with
        non-empty mask"""
        management = np.ma.array([2, 2, 255],
                                 mask=[False, False, True], dtype="uint8")
        soil_code = np.ma.array([14, 14, 255],
                                mask=[False, False, True], dtype="uint8")
        msw = np.ma.array([-33, -33, np.nan],
                          mask=[False, False, True], dtype="float32")
        nitrogen_deposition = np.ma.array([20, 20, np.nan],
                                          mask=[False, False, True], dtype="float32")
        nitrogen_animal = np.ma.array([350, 350, np.nan],
                                      mask=[False, False, True], dtype="float32")
        nitrogen_fertilizer = np.ma.array([0, 0, np.nan],
                                          mask=[False, False, True], dtype="float32")
        inundation = np.ma.array([1, 1, np.nan],
                                 mask=[False, False, True], dtype="float32")

        nl = niche_vlaanderen.NutrientLevel()
        result = nl.calculate(soil_code, msw, nitrogen_deposition,
                              nitrogen_animal, nitrogen_fertilizer, management,
                              inundation)

        np.testing.assert_equal(np.ma.array([5, 5, 255],
                                            mask=[False, False, True]), result)
        assert result.dtype == np.uint8

    def test_nutrient_level_testcase(self, path_testcase):
        """Correct nutrient level calculated for test case of the zwarte beek"""
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
