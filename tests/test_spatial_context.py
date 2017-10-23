from unittest import TestCase

import rasterio

import niche_vlaanderen


class testSpatialContext(TestCase):
    def test_check_overlap(self):

        soil_code = rasterio.open("testcase/grobbendonk/input/soil_codes.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        overlap = soil_code_sc.check_overlap(glg_sc)
        self.assertEqual(True, overlap)

        glg_nete = rasterio.open("testcase/grote_nete/input/mlw.asc")
        glg_nete_sc = niche_vlaanderen.niche.SpatialContext(glg_nete)

        overlap = soil_code_sc.check_overlap(glg_nete_sc)
        self.assertEqual(False, overlap)

    def test_check_set_overlap(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_codes.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # originally we have
        self.assertEqual(737, soil_code_sc.width)
        self.assertEqual(555, soil_code_sc.height)
        self.assertEqual(164487.5, soil_code_sc.affine[2])
        self.assertEqual(216737.5, soil_code_sc.affine[5])

        # after overlap we get
        overlap_success = soil_code_sc.set_overlap(glg_sc)
        self.assertEqual(True, overlap_success)
        self.assertEqual(693, soil_code_sc.width)
        self.assertEqual(501, soil_code_sc.height)
        self.assertEqual(164937.5, soil_code_sc.affine[2])
        self.assertEqual(216162.5, soil_code_sc.affine[5])

    def test_get_read_window(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_codes.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)
        full_window = soil_code_sc.get_read_window(soil_code_sc)

        self.assertEqual(full_window, ((0, 555), (0, 737)))

        part_window = glg_sc.get_read_window(soil_code_sc)

        self.assertEqual(part_window, ((23, 524), (18, 711)))

    def test_get_read_window_smaller(self):
        soil_code = rasterio.open("testcase/grobbendonk/input/soil_codes.asc")
        soil_code_sc = niche_vlaanderen.niche.SpatialContext(soil_code)
        glg = rasterio.open("testcase/grobbendonk/input/mlw.asc")
        glg_sc = niche_vlaanderen.niche.SpatialContext(glg)

        # soil_code has a larger extent than glg - this must error
        part_window = soil_code_sc.get_read_window(glg_sc)

        self.assertEqual(part_window, None)

    def test_different_crs(self):
        test_l72 = rasterio.open("tests/data/msw_small.asc")
        test_wgs84 = rasterio.open("tests/data/msw_small_wgs84.asc")
        test_l72_sc = niche_vlaanderen.niche.SpatialContext(test_l72)
        test_wgs84_sc = niche_vlaanderen.niche.SpatialContext(test_wgs84)
        self.assertFalse(test_wgs84_sc == test_l72_sc)
        self.assertTrue(test_wgs84_sc != test_l72_sc)
