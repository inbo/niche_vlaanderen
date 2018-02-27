from unittest import TestCase

import rasterio

import niche_vlaanderen
from niche_vlaanderen.spatial_context import SpatialContextError
import pytest
import sys


class testSpatialContext(TestCase):
    def test_extent(self):
        small = rasterio.open("tests/data/small/msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        expected = ((172762.5, 210637.5), (172937.5, 210487.5))
        self.assertEqual(expected, small_sc.extent)

    def test_repr(self):
        self.maxDiff = None
        small = rasterio.open("tests/data/small/msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        exp = "Extent: ((172762.5, 210637.5), (172937.5, 210487.5))\n\n" \
              "Affine(25.0, 0.0, 172762.5,\n       0.0, -25.0, 210637.5)\n\n" \
              "width: 7, height: 6\n\n"
        exp2 = exp + \
            "Projection: +ellps=intl +lat_0=90 +lat_1=51.1666672333 " + \
            "+lat_2=49.8333339 +lon_0=4.36748666667 +no_defs +proj=lcc " + \
            "+towgs84=-106.8686,52.2978,-103.7239,0.3366,-0.457,1.8422," + \
            "-1.2747 +units=m +x_0=150000.013 +y_0=5400088.438"
        # Python 3 has slightly different formatting (more numbers)
        exp3 = exp + \
            "Projection: +ellps=intl +lat_0=90 +lat_1=51.16666723333333 " \
            "+lat_2=49.8333339 +lon_0=4.367486666666666 +no_defs +proj=lcc " \
            "+towgs84=-106.8686,52.2978,-103.7239,0.3366,-0.457,1.8422," \
            "-1.2747 +units=m +x_0=150000.013 +y_0=5400088.438"
        if sys.version_info > (3, 0):
            self.assertEqual(exp3, small_sc.__repr__())
        else:
            self.assertEqual(exp2, small_sc.__repr__())

    def test_check_overlap(self):

        soil_code = rasterio.open("tests/data/small/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("tests/data/small/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        overlap = soil_code_sc.check_overlap(glg_sc)
        self.assertTrue(overlap)

        glg_nete = rasterio.open("testcase/zwarte_beek/input/mlw.asc")
        glg_nete_sc = niche_vlaanderen.niche.SpatialContext(glg_nete)

        overlap = soil_code_sc.check_overlap(glg_nete_sc)
        self.assertFalse(overlap)

        with pytest.raises(SpatialContextError):
            overlap = soil_code_sc.get_read_window(glg_nete_sc)

    def test_check_overlap_cells_moved(self):
        small = rasterio.open("tests/data/small/msw.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        # contains cells moved 0.5 m
        small_moved = rasterio.open("tests/data/msw_small_moved.asc")
        small_moved_sc = niche_vlaanderen.niche.SpatialContext(small_moved)
        self.assertFalse(small_sc.check_overlap(small_moved_sc))
        with pytest.raises(SpatialContextError):
            self.assertFalse(small_sc.set_overlap(small_moved_sc))

    def test_check_set_overlap(self):
        soil_code = rasterio.open("testcase/zwarte_beek/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("tests/data/part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # originally we have
        self.assertEqual(188, soil_code_sc.width)
        self.assertEqual(84, soil_code_sc.height)
        self.assertEqual(216580, soil_code_sc.transform[2])
        self.assertEqual(198580, soil_code_sc.transform[5])

        # after overlap we get

        soil_code_sc.set_overlap(glg_sc)
        print(soil_code_sc)
        self.assertEqual(37, soil_code_sc.width)
        self.assertEqual(37, soil_code_sc.height)
        self.assertEqual(216910, soil_code_sc.transform[2])
        self.assertEqual(198445, soil_code_sc.transform[5])

    def test_check_no_overlap(self):
        small = rasterio.open(
            "tests/data/small/soil_code.asc")
        zwarte_beek = rasterio.open(
            "testcase/zwarte_beek/input/soil_code.asc"
        )
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        zwarte_beek_sc = niche_vlaanderen.niche.SpatialContext(zwarte_beek)

        # check zones don't overlap
        self.assertFalse(small_sc.check_overlap(zwarte_beek_sc))

    def test_get_read_window(self):
        soil_code = rasterio.open("testcase/zwarte_beek/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("tests/data/part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)
        full_window = soil_code_sc.get_read_window(soil_code_sc)

        self.assertEqual(full_window, ((0, 84), (0, 188)))

        part_window = glg_sc.get_read_window(soil_code_sc)

        self.assertEqual(part_window, ((27, 64), (66, 103)))

    def test_get_read_window_smaller(self):
        soil_code = rasterio.open("testcase/zwarte_beek/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("tests/data/part_zwarte_beek_mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # soil_code has a larger extent than glg - this must error
        with pytest.raises(SpatialContextError):
            soil_code_sc.get_read_window(glg_sc)

    def test_different_crs(self):
        test_l72 = rasterio.open("tests/data/small/msw.asc")
        test_wgs84 = rasterio.open("tests/data/msw_small_wgs84.asc")
        test_l72_sc = niche_vlaanderen.niche.SpatialContext(test_l72)
        test_wgs84_sc = niche_vlaanderen.niche.SpatialContext(test_wgs84)
        self.assertFalse(test_wgs84_sc == test_l72_sc)
        self.assertTrue(test_wgs84_sc != test_l72_sc)

    def test_compare(self):
        test_small_ds = rasterio.open("tests/data/small/msw.asc")
        sc1 = niche_vlaanderen.niche.SpatialContext(test_small_ds)
        sc2 = niche_vlaanderen.niche.SpatialContext(sc1)
        self.assertEqual(sc1, sc2)
        sc2.height = sc2.height + 1
        # height is not equal - should be false
        self.assertFalse(sc1 == sc2)

        # check with different affine
        # we assign
        sc2 = niche_vlaanderen.niche.SpatialContext(
            rasterio.open("testcase/zwarte_beek/input/mlw.asc")
        )
        sc2.height = sc1.height
        sc2.width = sc1.width
        sc2.crs = sc1.crs
        self.assertFalse(sc1 == sc2)

    def test_area(self):
        test_small_ds = rasterio.open("tests/data/small/msw.asc")
        sc1 = niche_vlaanderen.niche.SpatialContext(test_small_ds)
        self.assertEqual(625, sc1.cell_area)

    def test_topdown(self):
        topdown = rasterio.open("tests/data/mlw_small.xyz")
        with pytest.raises(SpatialContextError):
            niche_vlaanderen.niche.SpatialContext(topdown)

    def test_nocrs(self):
        nocrs = rasterio.open("tests/data/small_nocrs.asc")
        sc = niche_vlaanderen.niche.SpatialContext(nocrs)
        assert sc.crs == ""
