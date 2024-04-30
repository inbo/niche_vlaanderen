import os
from pathlib import Path

import pytest

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
        myniche.set_input("mhw", input_dir / "mhw_inv.asc")
        myniche.set_input("mlw", input_dir / "mlw_inv.asc")
        myniche.set_input("msw", input_dir / "msw_inv.asc")
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
def small_niche(path_tests):
    """Create dummy testcase small"""
    myniche = niche_vlaanderen.Niche()
    myniche.read_config_file(path_tests / "small.yaml")
    return myniche