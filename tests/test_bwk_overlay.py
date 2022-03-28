import numpy as np

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.bwk_overlay import NicheOverlay


def test_overlay():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")

    no = NicheOverlay(niche=nv, map="tests/data/bwk/bkw_brasschaat_part1.shp")
    no.overlay()

    # get the index of a record we know should have a nich_1_1 value
    test_index = (
        no.map.reset_index().set_index("OBJECTID_1").loc[[2662]]["index"].values[0]
    )
    assert test_index == 48
    item = no.map.iloc[test_index]
    assert item["NICH_1_1"] == 6
    assert item["NICH_1_2"] == 6

    # calibration score
    assert np.isclose(no.score[6], 77.872340)


def test_overlay_artificial():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")
    no = NicheOverlay(niche=nv, map="tests/data/bwk/bwk_selection.shp")
    no.overlay()
