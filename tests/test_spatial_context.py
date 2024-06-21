from unittest import TestCase

import pytest
import rasterio

import niche_vlaanderen
from niche_vlaanderen.spatial_context import SpatialContextError


class TestSpatialContext:
    def test_extent(self, path_testdata):
        small = rasterio.open(path_testdata / "small" / "msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        expected = ((172762.5, 210637.5), (172937.5, 210487.5))
        assert expected == small_sc.extent

    def test_repr(self, path_testdata):
        self.maxDiff = None
        small = rasterio.open(path_testdata / "small" / "msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        exp = "Extent: ((172762.5, 210637.5), (172937.5, 210487.5))\n\n" \
              "Affine(25.0, 0.0, 172762.5,\n       0.0, -25.0, 210637.5)\n\n" \
              "width: 7, height: 6\n\n"

        print(small_sc.__repr__())
        # projection definitions can be formatted quite differently
        # it is checked that the extent is correct
        assert exp in small_sc.__repr__()
        # it should contain parts of lambert_conformal_conic
        assert "Lambert_Conformal_Conic" in small_sc.__repr__()


    def test_check_overlap(self, path_testdata, path_testcase):

        soil_code = rasterio.open(path_testdata / "small" / "soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open(path_testdata / "small" / "mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        overlap = soil_code_sc.check_overlap(glg_sc)
        assert overlap

        glg_nete = rasterio.open(path_testcase / "zwarte_beek" / "input" / "mlw.asc")
        glg_nete_sc = niche_vlaanderen.niche.SpatialContext(glg_nete)

        overlap = soil_code_sc.check_overlap(glg_nete_sc)
        assert not overlap

        with pytest.raises(SpatialContextError):
            soil_code_sc.get_read_window(glg_nete_sc)

    def test_check_overlap_cells_moved(self, path_testdata):
        small = rasterio.open(path_testdata / "small" / "msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        # contains cells moved 0.5 m
        small_moved = rasterio.open(path_testdata / "msw_small_moved.asc")
        small_moved_sc = niche_vlaanderen.niche.SpatialContext(small_moved)
        assert not small_sc.check_overlap(small_moved_sc)
        with pytest.raises(SpatialContextError):
            small_sc.set_overlap(small_moved_sc)

    def test_check_set_overlap(self, path_testdata, path_testcase):
        soil_code = rasterio.open(
            path_testcase / "zwarte_beek" / "input" / "soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open(path_testdata / "part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # originally we have
        assert 188 == soil_code_sc.width
        assert 84 == soil_code_sc.height
        assert 216580 == soil_code_sc.transform[2]
        assert 198580 == soil_code_sc.transform[5]

        # after overlap we get
        soil_code_sc.set_overlap(glg_sc)
        assert 37 == soil_code_sc.width
        assert 37 == soil_code_sc.height
        assert 216910 == soil_code_sc.transform[2]
        assert 198445 == soil_code_sc.transform[5]

    def test_check_no_overlap(self, path_testdata, path_testcase):
        small = rasterio.open(
            path_testdata/ "small" / "soil_code.asc")
        zwarte_beek = rasterio.open(
            path_testcase / "zwarte_beek" / "input" / "soil_code.asc"
        )
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        zwarte_beek_sc = niche_vlaanderen.niche.SpatialContext(zwarte_beek)

        # check zones don't overlap
        assert not small_sc.check_overlap(zwarte_beek_sc)

    def test_get_read_window(self, path_testdata, path_testcase):
        soil_code = rasterio.open(
            path_testcase / "zwarte_beek" / "input" / "soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open(path_testdata / "part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)
        full_window = soil_code_sc.get_read_window(soil_code_sc)

        assert full_window == ((0, 84), (0, 188))

        part_window = glg_sc.get_read_window(soil_code_sc)

        assert part_window == ((27, 64), (66, 103))

    def test_get_read_window_smaller(self,  path_testdata, path_testcase):
        soil_code = rasterio.open(
            path_testcase / "zwarte_beek" / "input" / "soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open(path_testdata / "part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # soil_code has a larger extent than glg - this must error
        with pytest.raises(SpatialContextError):
            soil_code_sc.get_read_window(glg_sc)

    def test_different_crs(self, path_testdata):
        test_l72 = rasterio.open(path_testdata / "small" / "msw.asc")
        test_wgs84 = rasterio.open(path_testdata / "msw_small_wgs84.asc")
        test_l72_sc = niche_vlaanderen.niche.SpatialContext(test_l72)
        test_wgs84_sc = niche_vlaanderen.niche.SpatialContext(test_wgs84)
        # Check for both custom dunder methods __eq__ and __ne__
        assert test_wgs84_sc != test_l72_sc
        assert not test_wgs84_sc == test_l72_sc

    def test_compare(self, path_testdata, path_testcase):
        test_small_ds = rasterio.open(path_testdata / "small" / "msw.asc")
        sc1 = niche_vlaanderen.niche.SpatialContext(test_small_ds)
        sc2 = niche_vlaanderen.niche.SpatialContext(sc1)
        assert sc1 == sc2
        sc2.height = sc2.height + 1
        # height is not equal - should be false
        assert sc1 != sc2

        # check with different affine
        # we assign
        sc2 = niche_vlaanderen.niche.SpatialContext(
            rasterio.open(path_testcase / "zwarte_beek" / "input" / "mlw.asc")
        )
        sc2.height = sc1.height
        sc2.width = sc1.width
        sc2.crs = sc1.crs
        assert sc1 != sc2

    def test_area(self, path_testdata):
        test_small_ds = rasterio.open(path_testdata / "small" / "msw.asc")
        sc1 = niche_vlaanderen.niche.SpatialContext(test_small_ds)
        assert 625 == sc1.cell_area

    def test_topdown(self, path_testdata):
        topdown = rasterio.open(path_testdata / "mlw_small.xyz")
        with pytest.raises(SpatialContextError):
            niche_vlaanderen.niche.SpatialContext(topdown)

    def test_nocrs(self, path_testdata):
        nocrs = rasterio.open(path_testdata / "small_nocrs.asc")
        sc = niche_vlaanderen.niche.SpatialContext(nocrs)
        assert sc.crs == ""
