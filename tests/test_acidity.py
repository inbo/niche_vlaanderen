import numpy as np
import pytest

import niche_vlaanderen
from niche_vlaanderen.exception import NicheException


class TestAcidity:

    def test_get_soil_mlw(self):
        """Correct soil_mlw class calculated from grids with empty mask"""
        mlw = np.array([-50, -66], dtype="float32")
        soil_code = np.array([14, 7], dtype="uint8")

        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)
        np.testing.assert_equal(np.array([1, 9]), result)
        assert result.dtype == np.uint8

    def test_get_soil_mlw_nodata(self):
        """Correct soil_mlw class calculated from grids with non-empty mask"""
        mlw = np.array([-50, -66, np.nan], dtype="float32")
        soil_code = np.array([14, 7, 255], dtype="uint8")

        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)
        np.testing.assert_equal(np.array([1, 9, 255]), result)
        assert result.dtype == np.uint8

    def test_get_soil_mlw_borders(self):
        """Correct acidity calculated for border values"""
        mlw = np.array([-79, -80, -100, -110, -111], dtype="float32")
        soil_code = np.array([14, 14, 14, 14, 14], dtype="uint8")

        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)
        expected = np.array([1, 1, 2, 2, 3])
        np.testing.assert_equal(expected, result)
        assert result.dtype == np.uint8

    def test_acidity_support(self):
        """Correct acidity calculated from grids with empty mask"""
        rainwater = np.array([0], dtype="uint8")
        minerality = np.array([1], dtype="uint8")
        inundation = np.array([1], dtype="uint8")
        seepage = np.array([1], dtype="float32")
        soil_mlw = np.array([1], dtype="uint8")

        a = niche_vlaanderen.Acidity()
        result = a._get_acidity(rainwater, minerality, inundation,
                                seepage, soil_mlw)

        np.testing.assert_equal(np.array([3]), result)
        assert result.dtype == np.uint8

    def test_acidity_support_nodata(self):
        """Correct acidity calculated from grids with non-empty mask"""
        rainwater = np.array([0, 0, 255], dtype="uint8")
        minerality = np.array([1, 1, 255], dtype="uint8")
        inundation = np.array([1, 1, 255], dtype="uint8")
        seepage = np.array([1, 1, np.nan], dtype="float32")
        soil_mlw = np.array([1, 1, 255], dtype="uint8")

        a = niche_vlaanderen.Acidity()
        result = a._get_acidity(rainwater, minerality, inundation,
                                seepage, soil_mlw)

        np.testing.assert_equal(np.array([3, 3, 255]), result)
        assert result.dtype == np.uint8

    def test_seepage(self):
        """Correct seepage calculated from grids with empty mask"""
        seepage = np.array([5, 0.3, 0.05, -0.04, -0.2, -5, -0.1, -1],
                              dtype="float32")
        a = niche_vlaanderen.Acidity()
        result = a._get_seepage(seepage)

        expected = np.array([1, 1, 1, 1, 2, 3, 2, 3])
        np.testing.assert_equal(expected, result)
        assert result.dtype == np.uint8

    def test_seepage_nodata(self):
        """Correct seepage calculated from grids with non-empty mask"""
        seepage = np.array(
            [5, 0.3, 0.05, -0.04, -0.2, -5, -0.1, -1, np.nan],
            dtype="float32")
        a = niche_vlaanderen.Acidity()
        result = a._get_seepage(seepage)

        expected = np.array([1, 1, 1, 1, 2, 3, 2, 3, 255])
        np.testing.assert_equal(expected, result)
        assert result.dtype == np.uint8

    def test_acidity(self):
        """Correct acidity calculated from grids with empty mask"""
        rainwater = np.array([0], dtype="uint8")
        minerality = np.array([0], dtype="uint8")
        soilcode = np.array([14], dtype="uint8")
        inundation = np.array([1], dtype="uint8")
        seepage = np.array([20], dtype="float32")
        mlw = -1 * np.array([50], dtype="float32")

        a = niche_vlaanderen.Acidity()
        result = a.calculate(soilcode, mlw, inundation, seepage, minerality,
                             rainwater)
        np.testing.assert_equal(3, result)
        assert result.dtype == np.uint8

    def test_acidity_nodata(self):
        """Correct acidity calculated from grids with non-empty mask"""
        rainwater = np.array([0, 0, 255], dtype="uint8")
        minerality = np.array([0, 0, 255], dtype="uint8")
        soilcode = np.array([14, 14, 255], dtype="uint8")
        inundation = np.array([1, 1, 255], dtype="uint8")
        seepage = np.array([20, 20, np.nan], dtype="float32")
        mlw = -1 * np.array([50, 50, np.nan], dtype="float32")

        a = niche_vlaanderen.Acidity()
        result = a.calculate(soilcode, mlw, inundation,
                             seepage, minerality, rainwater)
        np.testing.assert_equal(np.array([3, 3, 255]), result)
        assert result.dtype == np.uint8

    def test_acidity_testcase(self, path_testcase, zwarte_beek_data):
        """Correct acidity calculated for test case of the zwarte beek"""

        n, (soil_code, _, _, mlw, inundation, rainwater, seepage, minerality,
            _, _, _, management) = zwarte_beek_data

        a = niche_vlaanderen.Acidity()

        acidity_file_path = path_testcase / "zwarte_beek" / "abiotic" / "acidity.asc"
        n.set_input("acidity",acidity_file_path)
        acidity = n.read_rasterio_to_grid(acidity_file_path, variable_name="acidity")

        result = a.calculate(soil_code, mlw, inundation,
                             seepage, minerality, rainwater)
        np.testing.assert_equal(acidity, result)
        assert result.dtype == np.uint8

    def test_acidity_invalid_variable(self):
        """Raise an exception when an invalid soil code is used"""
        rainwater = np.array([0], dtype="uint8")
        minerality = np.array([0], dtype="uint8")
        inundation = np.array([1], dtype="uint8")
        seepage = np.array([20], dtype="float32")
        mlw = -1 * np.array([50], dtype="float32")
        soilcode = np.array([14], dtype="uint8")

        # set soil_code and minerality one by one as invalid value
        for invalid_variable in [soilcode, minerality]:
            invalid_variable[0] = 254
            a = niche_vlaanderen.Acidity()
            with pytest.raises(NicheException):
                a.calculate(soilcode, mlw, inundation, seepage,
                            minerality, rainwater)
