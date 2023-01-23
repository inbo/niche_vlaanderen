import os

import numpy as np
import geopandas as gpd
import pandas as pd
import pytest

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.validation import NicheValidation, NicheValidationException


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
    assert np.isclose(no.summary["score_opt"][6], 78.383459)
    assert np.isclose(no.summary["score_opt"][28], 3.813559)

    # repr
    assert "map: tests/data/bwk/bkw_brasschaat_part1.shp" in str(no)
    assert "niche object: brasschaat" in str(no)

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

def test_validation_invalid_niche():
    nv = 6
    with pytest.raises(ValueError):
        NicheValidation(niche=nv, map="tests/data/bwk/bwk_selection.shp")

def test_validation_warning_overlap():
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")
    with pytest.warns(UserWarning):
        NicheValidation(niche=nv, map="tests/data/bwk/bwk_selection.shp", upscale=1)

def test_validation_write(tmpdir):
    nv = Niche()
    nv.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")
    validation = NicheValidation(niche=nv, map="tests/data/bwk/bwk_selection.shp")
    validation.write(tmpdir)
    files_written = os.listdir(tmpdir)
    expected_files = {'area_nonpot_optimistic.csv', 'area_pot_perc.csv', 'potential_presence.csv', 'area_pot.csv', 'overlay.gpkg', 'area_effective.csv', 'summary.csv', 'veg_present.csv', 'area_pot_perc_optimistic.csv', 'area_nonpot.csv'}
    assert set(files_written)== expected_files

    # should raise because the dir eists and is not empty
    with pytest.raises(NicheValidationException):
        validation.write(tmpdir)

    # raises because the path exists and is not a folder
    with pytest.raises(NicheValidationException):
        validation.write(tmpdir/"overlay.gpkg")

    # should not raise
    validation.write(tmpdir, overwrite=True)

def test_validation_write_customid(tmpdir):
    """Test writing using a custom id"""
    nv = Niche()
    nv.run_config_file("tests/data/bwk_tiny/tiny.yaml")

    map = gpd.read_file("tests/data/bwk_tiny/bwk_clip.shp")
    map["new_id"] = [6, 7, 8, 9, 10]
    map.to_file(str(tmpdir / "sel_id.shp"))

    validation = NicheValidation(niche=nv, map=str(tmpdir / "sel_id.shp"), id="new_id")
    validation.write(tmpdir / "validation")
    files_written = os.listdir(tmpdir / "validation")
    expected_files = {'area_nonpot_optimistic.csv', 'area_pot_perc.csv', 'potential_presence.csv', 'area_pot.csv', 'overlay.gpkg', 'area_effective.csv', 'summary.csv', 'veg_present.csv', 'area_pot_perc_optimistic.csv', 'area_nonpot.csv'}
    assert set(files_written)== expected_files

    overlay = gpd.read_file(str(tmpdir /"validation"/ "overlay.gpkg"))
    area = pd.read_csv(tmpdir / "validation" /"area_pot_perc.csv")

    assert "new_id" in overlay.columns
    assert "new_id" in area.columns


def test_validation_multiple_veg():
    """Test that multiple mappings are used when converting to niche

    cfr issue #314
    """
    simplebr = Niche()
    simplebr.run_config_file("tests/data/bwk/niche_brasschaat/simple.yaml")

    no_simplebr_fkok = NicheValidation(niche=simplebr, map= "tests/data/bwk_fake/bwk_fake_extentok.shp") # see zip attached
    no_simplebr_fkok.overlay()

    assert pytest.approx(no_simplebr_fkok.area_effective.iloc[6][28]) == 6.776321

def test_validation_hablegend(tmpdir):
    """Test that fields starting with hab but not hab1-9 are skipped

    cfr issue #313
    """
    nv = Niche()
    nv.run_config_file("tests/data/bwk_tiny/tiny.yaml")

    map = gpd.read_file("tests/data/bwk_tiny/bwk_clip.shp")
    map["HAB_legend"] = "little text"
    map.to_file(str(tmpdir / "hablegend.shp"))
    validation = NicheValidation(niche=nv, map=str(tmpdir / "hablegend.shp"))
