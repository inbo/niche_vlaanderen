import os

import numpy as np
import geopandas as gpd
import pandas as pd
import pytest

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.validation import NicheValidation, NicheValidationException


def test_validation(zwarte_beek_niche):
    zwarte_beek_niche.run()

    no = NicheValidation(
        niche=zwarte_beek_niche,
        map="tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp",
    )

    # get the index of a record we know should have a nich_1_1 value
    test_index = no.map.reset_index().set_index("OBJECTID").loc[[37]]["index"].values[0]
    assert test_index == 4
    item = no.map.iloc[test_index]
    print(item)
    assert item["NICH_1_1"] == 14
    assert item["NICH_2_1"] == 14
    assert item["NICH_3_1"] == 18

    # calibration score
    print(no.summary)
    assert np.isclose(no.summary["score"][2], 63.75896700)
    assert np.isclose(no.summary["score_opt"][14], 60.970486)
    assert np.isclose(no.summary["score_opt"][18], 100)

    # repr
    assert "map: tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp" in str(no)
    assert "niche object: zwarte beek" in str(no)


def test_validation_custom_vegetation(zwarte_beek_niche):
    zwarte_beek_niche.run()

    no = NicheValidation(
        niche=zwarte_beek_niche,
        map="tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp",
        mapping_file="tests/data/hab_niche_test.csv",
    )

    # 5 hab columns * 3 potential values
    # three niche types for all 2 HAB types
    assert len(no.map.columns[no.map.columns.str.startswith("NICH")]) == 15


def test_validation_multiple_mapping(tmpdir, zwarte_beek_niche):
    """
    Test that area's are correct if multiple vegetation types map to the same niche type
    """
    zwarte_beek_niche.run()
    mapping = pd.read_csv("tests/data/hab_niche_test.csv")
    mapping["NICHE"] = 4
    mapping.drop_duplicates(inplace=True, ignore_index=True)
    print(mapping)
    mapping.to_csv(tmpdir / "mapping.csv")
    no = NicheValidation(
        niche=zwarte_beek_niche,
        map="tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp",
        mapping_file=tmpdir / "mapping.csv",
    )

    np.testing.assert_almost_equal(
        no.potential_presence.sum()["area_ha"].to_numpy(),
        (no.area_pot.sum() + no.area_nonpot.sum()).to_numpy(),
    )


def test_validation_invalid_niche():
    nv = 6
    with pytest.raises(ValueError):
        NicheValidation(niche=nv, map="tests/data/bwk_fake/bwk_fake_extentok.shp")


def test_validation_warning_overlap(zwarte_beek_niche):
    zwarte_beek_niche.run()
    with pytest.warns(UserWarning):
        NicheValidation(
            niche=zwarte_beek_niche,
            map="tests/data/bwk/BWK_2020_clip_ZwarteBeek.shp",
            upscale=1,
        )


def test_validation_write(tmpdir, zwarte_beek_niche):
    zwarte_beek_niche.run()
    validation = NicheValidation(
        niche=zwarte_beek_niche,
        map="tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp",
    )
    validation.write(tmpdir)
    files_written = os.listdir(tmpdir)
<<<<<<< HEAD
    expected_files = {'area_nonpot_optimistic.csv', 'area_pot_perc.csv', 'potential_presence.csv', 'area_pot.csv', 'validation.gpkg', 'area_effective.csv', 'summary.csv', 'veg_present.csv', 'area_pot_perc_optimistic.csv', 'area_nonpot.csv'}
=======
    expected_files = {
        "area_nonpot_optimistic.csv",
        "area_pot_perc.csv",
        "potential_presence.csv",
        "area_pot.csv",
        "overlay.gpkg",
        "area_effective.csv",
        "summary.csv",
        "veg_present.csv",
        "area_pot_perc_optimistic.csv",
        "area_nonpot.csv",
    }
    assert set(files_written) == expected_files

    # should raise because the dir exists and is not empty
    with pytest.raises(NicheValidationException):
        validation.write(tmpdir)

    # raises because the path exists and is not a folder
    with pytest.raises(NicheValidationException):
        validation.write(tmpdir/"validation.gpkg")

    # should not raise
    validation.write(tmpdir, overwrite_files=True)


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
    expected_files = {'area_nonpot_optimistic.csv', 'area_pot_perc.csv', 'potential_presence.csv', 'area_pot.csv', 'validation.gpkg', 'area_effective.csv', 'summary.csv', 'veg_present.csv', 'area_pot_perc_optimistic.csv', 'area_nonpot.csv'}
    assert set(files_written) == expected_files

    overlay = gpd.read_file(str(tmpdir /"validation"/ "validation.gpkg"))
    area = pd.read_csv(tmpdir / "validation" /"area_pot_perc.csv")

    assert "new_id" in overlay.columns
    assert "new_id" in area.columns


def test_validation_multiple_veg(zwarte_beek_niche):
    """Test that multiple mappings are used when converting to niche

    cfr issue #314
    """
    zwarte_beek_niche.run()

    no_simplebr_fkok = NicheValidation(
        niche=zwarte_beek_niche,
        map="tests/data/bwk/BWK_2020_clip_ZwarteBeek_simplified.shp",
        id="OBJECTID",
    )  # see zip attached
    print(no_simplebr_fkok.area_effective)
    print(no_simplebr_fkok.summary)
    # effective area should be 80% of the shape (40+40)
    assert pytest.approx(no_simplebr_fkok.area_effective.loc[37][14]) == 0.89288


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

def test_validation_nomapping(tmpdir):
    nv = Niche()
    nv.run_config_file("tests/data/bwk_tiny/tiny.yaml")
    with pytest.raises(NicheValidationException):
        NicheValidation(niche=nv,
                                 map="tests/data/bwk_tiny/bwk_clip.shp",
                                 mapping_file="tests/data/hab_niche_test.csv")
