from unittest import TestCase

import rasterio

import niche_vlaanderen
from niche_vlaanderen.spatial_context import SpatialContextError
import pytest
import sys

class testSpatialContext(TestCase):
    def test_extent(self):
        small = rasterio.open("tests/data/msw_small.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        expected = ((172762.5, 210637.5), (172937.5, 210487.5))
        self.assertEqual(expected, small_sc.extent)

    def test_repr(self):
        self.maxDiff = None
        small = rasterio.open("tests/data/msw_small.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        exp = "Extent: ((172762.5, 210637.5), (172937.5, 210487.5))\n\n"+ \
              "Affine(25.0, 0.0, 172762.5,\n       0.0, -25.0, 210637.5)\n\n"+\
              "width: 7, height: 6\n\n"
        exp2 = exp + \
              "Projection: +ellps=intl +lat_0=90 +lat_1=51.1666672333 "+\
              "+lat_2=49.8333339 +lon_0=4.36748666667 +no_defs +proj=lcc "+\
              "+towgs84=-106.8686,52.2978,-103.7239,0.3366,-0.457,1.8422,"+\
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

        soil_code = rasterio.open("testcase/grobbendonk/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        overlap = soil_code_sc.check_overlap(glg_sc)
        self.assertTrue(overlap)

        glg_nete = rasterio.open("testcase/grote_nete/input/mlw.asc")
        glg_nete_sc = niche_vlaanderen.niche.SpatialContext(glg_nete)

        overlap = soil_code_sc.check_overlap(glg_nete_sc)
        self.assertFalse(overlap)

        with pytest.raises(SpatialContextError):
            overlap = soil_code_sc.get_read_window(glg_nete_sc)

    def test_check_overlap_cells_moved(self):
        small = rasterio.open("tests/data/msw_small.asc")
        small_sc = niche_vlaanderen.niche.SpatialContext(small)
        # contains cells moved 0.5 m
        small_moved = rasterio.open("tests/data/msw_small_moved.asc")
        small_moved_sc = niche_vlaanderen.niche.SpatialContext(small_moved)
        self.assertFalse(small_sc.check_overlap(small_moved_sc))
        with pytest.raises(SpatialContextError):
            self.assertFalse(small_sc.set_overlap(small_moved_sc))


    def test_check_set_overlap(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # originally we have
        self.assertEqual(737, soil_code_sc.width)
        self.assertEqual(555, soil_code_sc.height)
        self.assertEqual(164487.5, soil_code_sc.affine[2])
        self.assertEqual(216737.5, soil_code_sc.affine[5])

        # after overlap we get
        soil_code_sc.set_overlap(glg_sc)
        self.assertEqual(693, soil_code_sc.width)
        self.assertEqual(501, soil_code_sc.height)
        self.assertEqual(164937.5, soil_code_sc.affine[2])
        self.assertEqual(216162.5, soil_code_sc.affine[5])

    def test_check_no_overlap(self):
        grobbendonk = rasterio.open(
            "testcase/grobbendonk/input/soil_code.asc")
        grote_nete = rasterio.open(
            "testcase/grote_nete/input/soil_code.asc"
        )
        grobbendonk_sc = niche_vlaanderen.niche.SpatialContext(grobbendonk)
        grote_nete_sc = niche_vlaanderen.niche.SpatialContext(grote_nete)

        # check zones don't overlap
        self.assertFalse(grobbendonk_sc.check_overlap(grote_nete_sc))

    def test_get_read_window(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)
        full_window = soil_code_sc.get_read_window(soil_code_sc)

        self.assertEqual(full_window, ((0, 555), (0, 737)))

        part_window = glg_sc.get_read_window(soil_code_sc)

        self.assertEqual(part_window, ((23, 524), (18, 711)))

    def test_get_read_window_smaller(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_code.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # soil_code has a larger extent than glg - this must error
        with pytest.raises(SpatialContextError):
            part_window = soil_code_sc.get_read_window(glg_sc)


    def test_different_crs(self):
        test_l72 = rasterio.open("tests/data/msw_small.asc")
        test_wgs84 = rasterio.open("tests/data/msw_small_wgs84.asc")
        test_l72_sc = niche_vlaanderen.niche.SpatialContext(test_l72)
        test_wgs84_sc = niche_vlaanderen.niche.SpatialContext(test_wgs84)
        self.assertFalse(test_wgs84_sc == test_l72_sc)
        self.assertTrue(test_wgs84_sc != test_l72_sc)

    def test_compare(self):
        test_small_ds = rasterio.open("tests/data/msw_small.asc")
        sc1 = niche_vlaanderen.niche.SpatialContext(test_small_ds)
        sc2 = niche_vlaanderen.niche.SpatialContext(sc1)
        self.assertEqual(sc1, sc2)
        sc2.height = sc2.height + 1
        # height is not equal - should be false
        self.assertFalse(sc1 == sc2)

        # check with different affine
        # we assign
        sc2 = niche_vlaanderen.niche.SpatialContext(
            rasterio.open("testcase/grobbendonk/input/mlw.asc")
        )
        sc2.height = sc1.height
        sc2.width = sc1.width
        sc2.crs = sc1.crs
        self.assertFalse(sc1 == sc2)
