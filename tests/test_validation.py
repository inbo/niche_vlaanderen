import os

import numpy as np
import geopandas as gpd
import pandas as pd
import pytest

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.validation import NicheValidation, NicheValidationException


def test_validation(zwarte_beek_niche, path_testdata):
    myniche = zwarte_beek_niche()
    myniche.name = "zwarte beek"
    myniche.run()

    no = NicheValidation(
        niche=myniche,
        map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek_simplified.shp",
    )

    # get the index of a record we know should have a nich_1_1 value
    test_index = no.map.reset_index().set_index("OBJECTID").loc[[37]]["index"].values[0]
    assert test_index == 4
    item = no.map.iloc[test_index]
    assert item["NICH_1_1"] == 14
    assert item["NICH_2_1"] == 14
    assert item["NICH_3_1"] == 18

    # calibration score
    assert np.isclose(no.summary["score"][2], 63.75896700)
    assert np.isclose(no.summary["score_phab"][14], 60.970486)
    assert np.isclose(no.summary["score_phab"][18], 100)

    # repr
    assert "BWK_2020_clip_ZwarteBeek_simplified.shp" in str(no)
    assert "niche object: zwarte beek" in str(no)


def test_validation_custom_vegetation(zwarte_beek_niche, path_testdata):
    myniche = zwarte_beek_niche()
    myniche.run()

    no = NicheValidation(
        niche=myniche,
        map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek_simplified.shp",
        mapping_file=path_testdata / "hab_niche_test.csv",
    )

    # 5 hab columns * 3 potential values
    # three niche types for all 2 HAB types
    assert len(no.map.columns[no.map.columns.str.startswith("NICH")]) == 15


def test_validation_multiple_mapping(tmp_path, zwarte_beek_niche, path_testdata):
    """
    Test that area's are correct if multiple vegetation types map to the same niche type
    """
    myniche = zwarte_beek_niche()
    myniche.run()

    mapping = pd.read_csv(path_testdata / "hab_niche_test.csv")
    mapping["NICHE"] = 4
    mapping.drop_duplicates(inplace=True, ignore_index=True)
    mapping.to_csv(tmp_path / "mapping.csv")
    no = NicheValidation(
        niche=myniche,
        map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek_simplified.shp",
        mapping_file=tmp_path / "mapping.csv"
    )

    np.testing.assert_almost_equal(
        no.potential_presence.sum()["area_ha"].to_numpy(),
        (no.area_pot.sum() + no.area_nonpot.sum()).to_numpy(),
    )


def test_validation_invalid_niche(path_testdata):
    nv = 6
    with pytest.raises(ValueError):
        NicheValidation(niche=nv,
                        map=path_testdata / "bwk_fake" / "bwk_fake_extentok.shp")


def test_validation_warning_overlap(zwarte_beek_niche, path_testdata):
    myniche = zwarte_beek_niche()
    myniche.run()
    with pytest.warns(UserWarning):
        NicheValidation(
            niche=myniche,
            map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek.shp",
            upscale=1,
        )


def test_validation_write(tmp_path, zwarte_beek_niche, path_testdata):
    myniche = zwarte_beek_niche()
    myniche.run()
    validation = NicheValidation(
        niche=myniche,
        map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek_simplified.shp",
    )
    validation.write(tmp_path)
    files_written = os.listdir(tmp_path)
    expected_files = {
        "area_nonpot_phab.csv",
        "area_pot_perc.csv",
        "potential_presence.csv",
        "area_pot.csv",
        "validation.gpkg",
        "area_effective.csv",
        "summary.csv",
        "veg_present.csv",
        "area_pot_perc_phab.csv",
        "area_nonpot.csv",
    }
    assert set(files_written) == expected_files

    # should raise because the dir exists and is not empty
    with pytest.raises(NicheValidationException):
        validation.write(tmp_path)

    # raises because the path exists and is not a folder
    with pytest.raises(NicheValidationException):
        validation.write(tmp_path / "validation.gpkg")

    # should not raise
    validation.write(tmp_path, overwrite_files=True)


def test_validation_write_customid(tmp_path, path_testdata):
    """Test writing using a custom id"""
    nv = Niche()
    nv.run_config_file(path_testdata / "bwk_tiny" / "tiny.yaml")

    map = gpd.read_file(path_testdata / "bwk_tiny" / "bwk_clip.shp")
    map["new_id"] = [6, 7, 8, 9, 10]
    map.to_file(str(tmp_path / "sel_id.shp"))

    validation = NicheValidation(niche=nv,
                                 map=str(tmp_path / "sel_id.shp"),
                                 id="new_id")
    validation.write(tmp_path / "validation")
    files_written = os.listdir(tmp_path / "validation")
    expected_files = {
        "area_nonpot_phab.csv",
        "area_pot_perc.csv",
        "potential_presence.csv",
        "area_pot.csv",
        "validation.gpkg",
        "area_effective.csv",
        "summary.csv",
        "veg_present.csv",
        "area_pot_perc_phab.csv",
        "area_nonpot.csv",
    }
    assert set(files_written) == expected_files

    overlay = gpd.read_file(str(tmp_path / "validation" / "validation.gpkg"))
    area = pd.read_csv(tmp_path / "validation" / "area_pot_perc.csv")

    assert "new_id" in overlay.columns
    assert "new_id" in area.columns


def test_validation_multiple_veg(zwarte_beek_niche, path_testdata):
    """Test that multiple mappings are used when converting to niche

    cfr issue #314
    """
    myniche = zwarte_beek_niche()
    myniche.run()

    no_simplebr_fkok = NicheValidation(
        niche=myniche,
        map=path_testdata / "bwk" / "BWK_2020_clip_ZwarteBeek_simplified.shp",
        id="OBJECTID",
    )  # see zip attached
    # effective area should be 80% of the shape (40+40)
    assert pytest.approx(no_simplebr_fkok.area_effective.loc[37][14]) == 0.89288


def test_validation_hablegend(tmp_path, path_testdata):
    """Test that fields starting with hab but not hab1-9 are skipped

    cfr issue #313
    """
    nv = Niche()
    nv.run_config_file(path_testdata / "bwk_tiny" / "tiny.yaml")

    map = gpd.read_file(path_testdata / "bwk_tiny" / "bwk_clip.shp")
    map["HAB_legend"] = "little text"
    map.to_file(str(tmp_path / "hablegend.shp"))
    NicheValidation(niche=nv, map=str(tmp_path / "hablegend.shp"))


def test_validation_nomapping(tmp_path, path_testdata):
    nv = Niche()
    nv.run_config_file(path_testdata / "bwk_tiny" / "tiny.yaml")
    with pytest.raises(NicheValidationException):
        NicheValidation(niche=nv,
                        map=path_testdata / "bwk_tiny" / "bwk_clip.shp",
                        mapping_file=path_testdata / "hab_niche_test.csv")
