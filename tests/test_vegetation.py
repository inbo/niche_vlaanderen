from __future__ import division
import pytest

import numpy as np
import rasterio

import niche_vlaanderen
from niche_vlaanderen.exception import NicheException
from niche_vlaanderen.vegetation import VegSuitable


class TestVegetation:

    @pytest.mark.parametrize("arr_in, expected_1, expected_0",
                        [("single_value_input_arrays",
                          np.array([1]), np.array([0])),
                         ("single_value_input_arrays_nodata",
                          np.array([1, 1, 255]), np.array([0, 0, 255]))
                         ], ids=["one_value", "one_value_nodata"])
    def test_one_value_doc(self, arr_in, expected_1, expected_0, request):
        """Correct vegetation prediction is calculated from single-value grids
        with empty and non-empty mask (as used in documentation)"""
        # Load the fixture values by name
        input_arrays = request.getfixturevalue(arr_in)
        nutrient_level, acidity, mlw, mhw, soil_code, _ = input_arrays

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code, mhw, mlw,
                                                     nutrient_level, acidity)
        correct = [7, 8, 12, 16]
        for vi in veg_predict:
            if vi in correct:
                np.testing.assert_equal(expected_1, veg_predict[vi])
            else:
                np.testing.assert_equal(expected_0, veg_predict[vi])
            assert veg_predict[vi].dtype == np.uint8

    @pytest.mark.parametrize("arr_in, expected_1, expected_0",
                        [("single_value_input_arrays",
                          np.array([1]), np.array([0])),
                         ("single_value_input_arrays_nodata",
                          np.array([1, 1, 255]),
                          np.array([0, 0, 255]))
                         ], ids=["simple_nomask", "simple_nodata"])
    def test_one_value_simple(self, arr_in, expected_1, expected_0, request):
        """Correct vegetation prediction is calculated from single-value grids
        with empty mask on a simplified niche model"""
        input_arrays = request.getfixturevalue(arr_in)
        _, _, mlw, mhw, soil_code, _ = input_arrays
        soil_code[:] = 8  # overwrite soil code with custom value

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code, mhw, mlw,
                                                     full_model=False)
        correct = [3, 8, 11, 18, 23, 27]
        for vi in veg_predict:
            if vi in correct:
                np.testing.assert_equal(expected_1, veg_predict[vi])
            else:
                np.testing.assert_equal(expected_0, veg_predict[vi])
            assert veg_predict[vi].dtype == np.uint8

    def test_borders(self):
        """Correct vegetation prediction for border values"""
        soil_code = np.array([3, 3, 3, 3, 3], dtype="uint8")
        mhw = -1 * np.array([21, 20, 10, 1, 0], dtype="float32")
        mlw = -1 * np.array([30, 30, 30, 30, 30], dtype="float32")

        v = niche_vlaanderen.Vegetation()
        veg_predict, _, _ = v.calculate(soil_code, mhw, mlw, full_model=False)
        expected = np.array([0, 1, 1, 1, 0], dtype="uint8")
        np.testing.assert_equal(expected, veg_predict[1])
        assert veg_predict[1].dtype == np.uint8

    def test_one_value_nomatch(self, single_value_input_arrays):
        """Correct vegetation prediction is calculated from single-value grids
        with empty mask and no-mathcing soil codes"""

        nutrient_level, acidity, mlw, mhw, soil_code, _ = single_value_input_arrays
        soil_code[:] = 254  # Provide out of bound soil code

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, veg_detail = v.calculate(soil_code, mhw, mlw,
                                                              nutrient_level, acidity)
        # no types should match
        for vi in veg_predict:
            np.testing.assert_equal(np.array([0]), veg_predict[vi])

        for vi in veg_detail:
            np.testing.assert_equal(np.array([0]), veg_detail[vi])

    @pytest.mark.parametrize("arr_in, expected_0",
                        [("single_value_input_arrays", np.array([0])),
                         ("single_value_input_arrays_nodata", np.array([0, 0, 255]))
                         ], ids=["doc_inundation_nomask", "doc_inundation_nodata"])
    def test_simple_doc_inundation(self, arr_in, expected_0, request):
        """Correct vegetation prediction is calculated from single-value grids
        with empty mask when inindation is added (as used in documentation)"""
        input_arrays = request.getfixturevalue(arr_in)
        nutrient_level, acidity, mlw, mhw, soil_code, inundation = input_arrays

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, veg_detail = v.calculate(
            soil_code, mhw, mlw, nutrient_level, acidity,
            inundation=inundation)

        correct = [7, 12, 16]
        veg_detail_exp = {1: 0, 2: 35, 3: 39, 4: 7, 5: 3, 6: 0, 7: 47, 8: 15,
                          9: 1, 10: 0, 11: 0, 12: 47, 13: 1, 14: 0, 15: 1,
                          16: 47, 17: 0, 18: 11, 19: 39, 20: 1, 21: 11, 22: 0,
                          23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0}

        # Note: in the docs '8' is suitable except for inundation: 1+2+4+8=15 with
        # suitable soil, gxg, nutrient and acidity, but unsuitable inundation (32)
        for vi in veg_predict:
            expected = np.repeat(veg_detail_exp[vi], nutrient_level.size)
            expected[soil_code == 255] = 255
            np.testing.assert_equal(expected, veg_detail[vi])
            if vi in correct:
                # Only consider data-values
                np.testing.assert_array_less(expected_0[:2], veg_detail[vi][:2])
            else:
                np.testing.assert_equal(expected_0, veg_predict[vi])
            assert veg_predict[vi].dtype == np.uint8

    def test_occurrences_nodata_propagation(self):
        """Occurrences are correclty calculated with propagating no-data values."""
        nutrient_level = np.array([[4, 4], [4, 5]], dtype="uint8")
        mlw = -1 * np.array([[50, 50], [50, 50]], dtype="float32")
        mhw = -1 * np.array([[31, 30], [10, 4]], dtype="float32")
        soil_code = np.array([[14, 14], [14, 14]], dtype="uint8")
        inundation = np.array([[1, 1], [1, 1]], dtype="uint8")

        # Add masked (no-data value) for acidity
        acidity = np.array([[3, 3], [3, 255]], dtype="uint8")

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = \
            v.calculate(soil_code=soil_code, mhw=mhw, mlw=mlw,
                        nutrient_level=nutrient_level, acidity=acidity,
                        inundation=inundation)

        # check no data propagates nicely
        for pred in veg_predict.values():
            assert pred[1, 1] == 255
            assert pred.dtype == np.uint8

        # occurrences are not taking into account masked values
        assert 1 / 3 == veg_occurrence[12]
        assert 1 == veg_occurrence[7]
        assert 2 / 3 == veg_occurrence[16]

    def test_testcase(self, path_testcase, zwarte_beek_data):
        """Correct vegetation prediction for test case of the zwarte beek"""
        n, (soil_code, msw, mhw, mlw, inundation,
            rainwater, seepage, minerality,
            nitrogen_deposition, nitrogen_animal,
            nitrogen_fertilizer, management) = zwarte_beek_data

        nl = niche_vlaanderen.NutrientLevel()
        nutrient_level = nl.calculate(soil_code, msw, nitrogen_deposition,
                                      nitrogen_animal, nitrogen_fertilizer,
                                      management, inundation)

        a = niche_vlaanderen.Acidity()
        acidity = a.calculate(soil_code, mlw, inundation, seepage,
                              minerality, rainwater)

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code, mhw, mlw,
                                                     nutrient_level, acidity)

        for i in range(1, 28):
            file_path = path_testcase / "zwarte_beek" / "vegetation" / f"v{i}.asc"
            with rasterio.open(file_path, "r") as dst:
                vi = dst.read(1, masked=True)
                vi = vi.filled(fill_value=255)
            np.testing.assert_allclose(vi - veg_predict[i], 0)

    def test_all_nodata(self, path_testdata):
        """Variable with all no-data values raises error"""
        soil_code = np.array([14, 14, 14], dtype="uint8")
        mlw = np.array([np.nan, np.nan, np.nan], dtype="float32")
        mhw = mlw.copy()

        v = niche_vlaanderen.Vegetation()
        with pytest.raises(NicheException):
            v.calculate(soil_code, mhw, mlw, full_model=False)

    def test_deviation_mhw(self):
        """Correct deviation calculated for mhw with mask-nan versus calculated nan"""
        v = niche_vlaanderen.Vegetation()

        soil_code = np.array([3, 3, 3, 3, 255, 2], dtype="uint8")
        mhw = -1 * np.array([66, 16, 5, -5, 5, 5], dtype="float32")
        mlw = -1 * np.array([35, 35, 35, 35, 35, 35], dtype="float32")
        d = v.calculate_deviation(soil_code, mhw, mlw)

        # Both a Nan inside the mask as well as a calculated Nan in the data
        expected = np.array([46, 0, 0, -6, np.nan, np.nan])
        np.testing.assert_equal(expected, d["mhw_01"])

    def test_deviation_mlw(self):
        """Correct deviation calculated for mhw with mask-nan versus calculated nan"""
        v = niche_vlaanderen.Vegetation()

        soil_code = np.array([3, 3, 3, 3, 3, 255, 2], dtype="uint8")
        mhw = -1 * np.array([5, 5, 5, 5, 5, 5, 5], dtype="float32")
        mlw = -1 * np.array([66, 50, 38, 25, 5, 25, 25], dtype="float32")
        d = v.calculate_deviation(soil_code, mhw, mlw)

        expected = np.array([28, 12, 0, 0, -15, np.nan, np.nan])
        np.testing.assert_equal(expected, d["mlw_01"])

    def test_detailed_vegetation(self, single_value_input_arrays):
        """Correct vegetation example in docs"""
        nutrient_level, acidity, mlw, mhw, soil_code, _ = single_value_input_arrays
        nutrient_level[:] = 5

        v = niche_vlaanderen.Vegetation()
        veg_bands, occurrence, veg_detail = v.calculate(soil_code, mhw, mlw,
                                                        nutrient_level, acidity)
        # cfr examples in vegetatie.rst
        np.testing.assert_equal(11, veg_detail[8])
        np.testing.assert_equal(0, veg_detail[6])

    def test_vegsuitable(self):
        legend = VegSuitable.legend()
        assert list(legend.keys()) == sorted(
            list(np.add.outer(
                np.add.outer([0, 4], [0, 8]),
                np.add.outer([0, 16], [0, 32])).flatten() + 3) + [0, 1])
        assert legend[63] == "soil+mxw+nutrient+acidity+management+flooding suitable"
