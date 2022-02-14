from niche_vlaanderen.niche import Niche
from niche_vlaanderen.bwk_overlay import NicheOverlay


def test_overlay():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")

    no = NicheOverlay(niche=nv, map="tests/data/bwk/BWK_edit_20190207.shp")
    no.overlay()