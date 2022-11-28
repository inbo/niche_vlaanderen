import numpy as np

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.validation import NicheValidation


def test_validation():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")

    no = NicheValidation(niche=nv, map="tests/data/bwk/bkw_brasschaat_part1.shp")
    no.overlay()

    # get the index of a record we know should have a nich_1_1 value
    test_index = (
        no.map.reset_index().set_index("OBJECTID_1").loc[[2662]]["index"].values[0]
    )
    assert test_index == 48
    item = no.map.iloc[test_index]
    assert item["NICH_1_1"] == 6
    assert np.isnan(item["NICH_1_2"])

    # calibration score
    print(no.summary)
    assert np.isclose(no.summary["score"][6], 78.383459)
    assert np.isclose(no.summary["score_opt"][6], 78.008985)

def test_validation_custom_vegetation():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")

    no = NicheValidation(niche=nv, map="tests/data/bwk/bkw_brasschaat_part1.shp", mapping_file="tests/data/hab_niche_test.csv")
    no.overlay()

    # three niche types for all 2 HAB types
    print(no.map.columns[no.map.columns.str.startswith("NICH")])
    assert np.all(no.map.columns[no.map.columns.str.startswith("NICH")] == ['NICH_1_1', 'NICH_1_2', 'NICH_1_3', 'NICH_2_1', 'NICH_2_2', 'NICH_2_3'])

def test_validation_artificial():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")
    no = NicheValidation(niche=nv, map="tests/data/bwk/bwk_selection.shp")
    no.overlay()
