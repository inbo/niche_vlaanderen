import pytest

import niche_vlaanderen

@pytest.fixture
def zwarte_beek_niche():
    myniche = niche_vlaanderen.Niche()
    myniche.name="zwarte beek"
    input_dir = "testcase/zwarte_beek/input/"
    myniche.set_input("soil_code", input_dir + "soil_code.asc")
    myniche.set_input("mhw", input_dir + "mhw.asc")
    myniche.set_input("mlw", input_dir + "mlw.asc")
    myniche.set_input("msw", input_dir + "msw.asc")
    myniche.set_input("minerality", input_dir + "minerality.asc")
    myniche.set_input(
        "nitrogen_atmospheric", input_dir + "nitrogen_atmospheric.asc"
    )
    myniche.set_input("nitrogen_animal", 0)
    myniche.set_input("nitrogen_fertilizer", 0)
    myniche.set_input("management", input_dir + "management.asc")
    myniche.set_input("inundation_nutrient", input_dir + "inundation.asc")
    myniche.set_input("inundation_acidity", input_dir + "inundation.asc")
    myniche.set_input("seepage", input_dir + "seepage.asc")
    myniche.set_input("rainwater", input_dir + "rainwater.asc")
    return myniche