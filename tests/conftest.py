import os
from pathlib import Path

import pytest
import numpy as np

import niche_vlaanderen

CURRENT_DIR = Path(os.path.dirname(__file__))


@pytest.fixture
def path_tests():
    """Main folder path to the test cases directory."""
    return CURRENT_DIR


@pytest.fixture
def path_testcase():
    """Main folder path to the test cases directory."""
    return CURRENT_DIR / ".." / "testcase"


@pytest.fixture
def path_testdata():
    """Folder path to test data."""
    return CURRENT_DIR / "data"


@pytest.fixture
def path_system_tables():
    """Main folder path to the system tables shipped with the package."""
    return CURRENT_DIR / ".." / "niche_vlaanderen" / "system_tables"


@pytest.fixture
def zwarte_beek_niche(path_testcase):
    """Create testcase Zwarte Beek"""

    def _create_zwarte_beek():
        myniche = niche_vlaanderen.Niche()
        input_dir = path_testcase / "zwarte_beek" / "input"
        myniche.set_input("soil_code", input_dir / "soil_code.asc")
        myniche.set_input("mhw", input_dir / "mhw.asc")
        myniche.set_input("mlw", input_dir / "mlw.asc")
        myniche.set_input("msw", input_dir / "msw.asc")
        myniche.set_input("minerality", input_dir / "minerality.asc")
        myniche.set_input(
            "nitrogen_atmospheric", input_dir / "nitrogen_atmospheric.asc"
        )
        myniche.set_input("nitrogen_animal", 0)
        myniche.set_input("nitrogen_fertilizer", 0)
        myniche.set_input("management", input_dir / "management.asc")
        myniche.set_input("inundation_nutrient", input_dir / "inundation.asc")
        myniche.set_input("inundation_acidity", input_dir / "inundation.asc")
        myniche.set_input("seepage", input_dir / "seepage.asc")
        myniche.set_input("rainwater", input_dir / "rainwater.asc")
        return myniche
    return _create_zwarte_beek


@pytest.fixture
def zwarte_beek_data(path_testcase):
    """Provide masked arrays loaded from disk for the Zwarte Beek testcase"""
    n = niche_vlaanderen.Niche()
    input_folder_path = path_testcase / "zwarte_beek" / "input"

    soil_code_file_path = input_folder_path / "soil_code.asc"
    n.set_input("soil_code", soil_code_file_path)
    soil_code = n.read_rasterio_to_grid(soil_code_file_path,
                                        variable_name="soil_code")

    msw_file_path = input_folder_path / "msw.asc"
    n.set_input("msw", msw_file_path)
    msw = n.read_rasterio_to_grid(msw_file_path, variable_name="msw")

    mhw_file_path = input_folder_path / "mhw.asc"
    n.set_input("mhw", mhw_file_path)
    mhw = n.read_rasterio_to_grid(mhw_file_path, variable_name="mhw")

    mlw_file_path = input_folder_path / "mlw.asc"
    n.set_input("mlw", mlw_file_path)
    mlw = n.read_rasterio_to_grid(mlw_file_path, variable_name="mlw")

    in_file_path = input_folder_path / "inundation.asc"
    n.set_input("inundation_nutrient", in_file_path)
    inundation = n.read_rasterio_to_grid(in_file_path,
                                         variable_name="inundation_nutrient")
    rainwater_file_path = input_folder_path / "nullgrid.asc"
    n.set_input("rainwater", rainwater_file_path)
    rainwater = n.read_rasterio_to_grid(rainwater_file_path,
                                        variable_name="rainwater")
    seepage_file_path = input_folder_path / "seepage.asc"
    n.set_input("seepage", seepage_file_path)
    seepage = n.read_rasterio_to_grid(seepage_file_path,
                                      variable_name="seepage")

    minerality_file_path = input_folder_path / "minerality.asc"
    n.set_input("minerality", minerality_file_path)
    minerality = n.read_rasterio_to_grid(minerality_file_path,
                                         variable_name="minerality")

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

    management_file_path = input_folder_path / "management.asc"
    n.set_input("management", management_file_path)
    management = n.read_rasterio_to_grid(management_file_path,
                                         variable_name="management")
    return n, (soil_code, msw, mhw, mlw, inundation, rainwater, seepage, minerality,
            nitrogen_deposition, nitrogen_animal, nitrogen_fertilizer, management)


@pytest.fixture
def single_value_input_arrays():
    """Provide set of fixed single value grids"""
    nutrient_level = np.array([4], dtype="uint8")
    acidity = np.array([3], dtype="uint8")
    mlw = np.array([-50], dtype="float32")
    mhw = np.array([-10], dtype="float32")
    soil_code = np.array([14], dtype="uint8")
    inundation = np.array([1], dtype="uint8")
    return nutrient_level, acidity, mlw, mhw, soil_code, inundation

@pytest.fixture
def single_value_input_arrays_nodata():
    """Provide set of fixed single value grids with a mask"""

    nutrient_level = np.array([4, 4, 255], dtype="uint8")
    acidity = np.array([3, 3, 255], dtype="uint8")
    mlw = np.array([-50, -50, np.nan], dtype="float32")
    mhw = np.array([-10, -10, np.nan], dtype="float32")
    soil_code = np.array([14, 14, 255], dtype="uint8")
    inundation = np.array([1, 1, 255], dtype="uint8")

    return nutrient_level, acidity, mlw, mhw, soil_code, inundation


@pytest.fixture
def small_niche(path_tests):
    """Create dummy testcase small"""
    myniche = niche_vlaanderen.Niche()
    myniche.read_config_file(path_tests / "small.yaml")
    return myniche