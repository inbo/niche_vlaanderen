from __future__ import division
from unittest import TestCase
import pytest

import numpy as np
import rasterio

import niche_vlaanderen
from niche_vlaanderen.exception import NicheException
from niche_vlaanderen.vegetation import VegSuitable


def raster_to_numpy(filename):
    """Read a GDAL grid as numpy array

    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    """

    with rasterio.open(filename) as ds:
        data = ds.read(1)
        nodata = ds.nodatavals[0]

    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = -99

    return data.astype(float)


class TestVegetation:
    def test_one_value_doc(self):
        nutrient_level = np.array([4])
        acidity = np.array([3])
        mlw = np.array([-50])
        mhw = np.array([-10])
        soil_code = np.array([14])
        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code, mhw, mlw,
                                                     nutrient_level, acidity)
        correct = [7, 8, 12, 16]
        for vi in veg_predict:
            if vi in correct:
                np.testing.assert_equal(np.array([1]), veg_predict[vi])
            else:
                np.testing.assert_equal(np.array([0]), veg_predict[vi])

    def test_one_value_simple(self):
        mlw = np.array([-50])
        mhw = np.array([-10])
        soil_code = np.array([8])
        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code,
                                                     mhw, mlw, full_model=False)
        correct = [3, 8, 11, 18, 23, 27]
        for vi in veg_predict:
            if vi in correct:
                np.testing.assert_equal(np.array([1]), veg_predict[vi])
            else:
                np.testing.assert_equal(np.array([0]), veg_predict[vi])

    def test_borders(self):
        soil_code = np.array([3, 3, 3, 3, 3])
        mhw = -1 * np.array([21, 20, 10, 1, 0])
        mlw = -1 * np.array([30, 30, 30, 30, 30])
        v = niche_vlaanderen.Vegetation()
        veg_predict, _, _ = v.calculate(soil_code, mhw, mlw, full_model=False)
        expected = [0, 1, 1, 1, 0]
        np.testing.assert_equal(expected, veg_predict[1])

    def test_one_value(self):
        nutrient_level = np.array([5])
        acidity = np.array([3])
        mlw = np.array([-50])
        mhw = np.array([-10])
        soil_code = np.array([140000])
        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, veg_detail = v.calculate(soil_code, mhw, mlw,
                                                              nutrient_level, acidity)
        correct = []  # no types should match
        for vi in veg_predict:
            if vi in correct:
                np.testing.assert_equal(np.array([1]), veg_predict[vi])
            else:
                np.testing.assert_equal(np.array([0]), veg_predict[vi])

        for vi in veg_detail:
            np.testing.assert_equal(np.array([0]), veg_detail[vi])

    def test_simple_doc_inundation(self):
        nutrient_level = np.array([4])
        acidity = np.array([3])
        mlw = np.array([-50])
        mhw = np.array([-10])
        soil_code = np.array([14])
        inundation = np.array([1])
        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, veg_detail = \
            v.calculate(soil_code, mhw, mlw, nutrient_level, acidity,
                        inundation=inundation)
        correct = [7, 12, 16]
        veg_detail_exp = {1: 0, 2: 35, 3: 39, 4: 7, 5: 3, 6: 0, 7: 47, 8: 15,
                          9: 1, 10: 0, 11: 0, 12: 47, 13: 1, 14: 0, 15: 1, 16: 47, 17: 0, 18: 11, 19: 39,
                          20: 1, 21: 11, 22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 0}

        # note that in the docs 8 was suitable except for inundation: its value is indeed:
        # 1+2+4+8= 15 so suitable soil, gxg, nutrient and acidity, but unsuitable inundation (32)

        for vi in veg_predict:
            np.testing.assert_equal(veg_detail_exp[vi], veg_detail[vi])
            if vi in correct:
                np.testing.assert_array_less(np.array([0]), veg_detail[vi])
            else:
                np.testing.assert_equal(np.array([0]), veg_predict[vi])

    def test_occurrence(self):
        nutrient_level = np.array([[4, 4], [4, 5]])
        acidity = np.array([[3, 3], [3, 255]])
        mlw = -1 * np.array([[50, 50], [50, 50]])
        mhw = -1 * np.array([[31, 30], [10, 4]])
        soil_code = np.array([[14, 14], [14, 14]])
        inundation = np.array([[1, 1], [1, 1]])
        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = \
            v.calculate(soil_code=soil_code, mhw=mhw, mlw=mlw,
                        nutrient_level=nutrient_level, acidity=acidity,
                        inundation=inundation)
        # check no data propagates nicely
        assert 255 == veg_predict[1][1, 1]
        assert 1 / 3 == veg_occurrence[12]
        assert 1 == veg_occurrence[7]
        assert 2 / 3 == veg_occurrence[16]

    def test_testcase(self, path_testcase):
        input_dir = path_testcase / "zwarte_beek" / "input"
        soil_code = raster_to_numpy(input_dir / "soil_code.asc").astype(int)
        # soil_code_r = soil_code / 10000
        soil_code_r = soil_code
        soil_code_r[soil_code > 0] = np.round(soil_code / 10000)[soil_code > 0]

        msw = raster_to_numpy(input_dir / "msw.asc")
        mhw = raster_to_numpy(input_dir / "mhw.asc")
        mlw = raster_to_numpy(input_dir / "mlw.asc")
        inundation = \
            raster_to_numpy(input_dir / "inundation.asc")
        regenlens = raster_to_numpy(input_dir / "nullgrid.asc")
        seepage = raster_to_numpy(input_dir / "seepage.asc")
        conductivity = raster_to_numpy(input_dir / "minerality.asc")
        nitrogen_deposition = \
            raster_to_numpy(input_dir / "nitrogen_atmospheric.asc")
        nitrogen_animal = raster_to_numpy(input_dir / "nullgrid.asc")
        nitrogen_fertilizer = raster_to_numpy(input_dir / "nullgrid.asc")
        management = raster_to_numpy(input_dir / "management.asc")

        nl = niche_vlaanderen.NutrientLevel()
        nutrient_level = nl.calculate(soil_code_r, msw, nitrogen_deposition,
                                      nitrogen_animal, nitrogen_fertilizer,
                                      management, inundation)

        a = niche_vlaanderen.Acidity()
        acidity = a.calculate(soil_code_r, mlw, inundation, seepage,
                              conductivity, regenlens)

        v = niche_vlaanderen.Vegetation()
        veg_predict, veg_occurrence, _ = v.calculate(soil_code_r, mhw, mlw,
                                                     nutrient_level, acidity)

        for i in range(1, 28):
            vi = raster_to_numpy(
                path_testcase / "zwarte_beek" / "vegetation" / f"v{i}.asc"
            ).astype(int)

            # TODO: this is dirty - we apply the same no data filter to the
            # original set the new set, as this was done incorrectly in the
            # original set.
            # this also means that if we predict no data everywhere the test
            #  also works :-)

            vi[(veg_predict[i] == 255)] = 255
            # np.testing.assert_equal(vi, veg_predict[i])
            np.testing.assert_allclose(vi-veg_predict[i], 0)

    def test_all_nodata(self, path_testdata):
        soil_code = raster_to_numpy(
            path_testdata / "small" / "soil_code.asc")
        mlw = -1 * raster_to_numpy(
            path_testdata / "small" / "mlw.asc")
        mhw = mlw.copy()
        mhw.fill(np.nan)

        v = niche_vlaanderen.Vegetation()
        with pytest.raises(NicheException):
            v.calculate(soil_code, mhw, mlw)

    def test_deviation_mhw(self):
        v = niche_vlaanderen.Vegetation()

        soil_code = np.array([3, 3, 3, 3, -99, 2])
        mhw = -1 * np.array([66, 16, 5, -5, 5, 5])
        mlw = -1 * np.array([35, 35, 35, 35, 35, 35])
        d = v.calculate_deviation(soil_code, mhw, mlw)
        expected = np.array([46, 0, 0, -6, np.nan, np.nan])
        np.testing.assert_equal(expected, d["mhw_01"])

    def test_deviation_mlw(self):
        v = niche_vlaanderen.Vegetation()

        soil_code = np.array([3, 3, 3, 3, 3, -99, 2])
        mhw = -1 * np.array([5, 5, 5, 5, 5, 5, 5])
        mlw = -1 * np.array([66, 50, 38, 25, 5, 25, 25])
        d = v.calculate_deviation(soil_code, mhw, mlw)
        expected = np.array([28, 12, 0, 0, -15, np.nan, np.nan])
        np.testing.assert_equal(expected, d["mlw_01"])

    def test_detailed_vegetation(self):
        v = niche_vlaanderen.Vegetation()
        soil_code = np.array([14])
        veg_bands, occurrence, veg_detail = v.calculate(
            soil_code, mhw=-10, mlw=-50, nutrient_level=5, acidity=3)
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
