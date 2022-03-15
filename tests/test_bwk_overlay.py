from niche_vlaanderen.niche import Niche
from niche_vlaanderen.bwk_overlay import NicheOverlay


def test_overlay():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")


    # get the index of a record we know should have a nich_1_1 value
    test_index = no.map.reset_index().set_index("OBJECTID_1").loc[[2662]]['index'].values[0]
    assert test_index == 48
    item = no.map.iloc[test_index]
    assert item['NICH_1_1'] == 6
    assert item['NICH_1_2'] == 6

    # this should also have a potential presence
    no.potential_presence.loc[test_index].loc[6].loc['present']

    assert False


def test_overlay2():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")
