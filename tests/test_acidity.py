from unittest import TestCase

import rasterio
import numpy as np

import niche_vlaanderen


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
    if data.dtype == 'float32':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = nodata

    return data


class testAcidity(TestCase):

    def test_get_soil_mlw(self):
        mlw = np.array([50, 66])
        soil_code = np.array([14, 7])
        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)

        np.testing.assert_equal(np.array([1, 9]), result)

    def test_get_soil_mlw_borders(self):
        mlw = np.array([79,80, 100, 110, 111])
        soil_code = np.array([14, 14, 14, 14, 14])
        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)
        expected =  np.array([1,1,2,2,3])
        np.testing.assert_equal(expected, result)

    def test_minerality_class(self):
        conductivity = np.array([500, 100, np.nan, 700])
        a = niche_vlaanderen.Acidity()
        result = a._calculate_mineral_richness_class(conductivity)

        np.testing.assert_equal(np.array([1, 0, -99, 1]), result)

    def test_acidity_partial(self):
        rainwater = np.array([0])
        mineral_richness = np.array([1])
        inundation = np.array([1])
        seepage = np.array([1])
        soil_mlw = np.array([1])

        a = niche_vlaanderen.Acidity()
        result = a._get_acidity(rainwater, mineral_richness, inundation,
                                seepage, soil_mlw)

        np.testing.assert_equal(np.array([3]), result)

    def test_seepage_code(self):
        seepage = np.array([5, 0.3, 0.05, -0.04, -0.2, -5])
        a = niche_vlaanderen.Acidity()
        result = a._get_seepage(seepage)

        expected = np.array([1, 1, 1, 1, 2, 3])
        np.testing.assert_equal(expected, result)

    def test_acidity(self):
        rainwater = np.array([0])
        conductivity = np.array([400])
        soilcode = np.array([14])
        inundation = np.array([1])
        seepage = np.array([20])
        mlw = np.array([50])

        a = niche_vlaanderen.Acidity()
        result = a.calculate(soilcode, mlw, inundation, seepage, conductivity,
                             rainwater)
        np.testing.assert_equal(3, result)

    def test_acidity_testcase(self):
        a = niche_vlaanderen.Acidity()
        soil_code = raster_to_numpy("testcase/grote_nete/input/soil_code.asc")
        soil_code_r = soil_code
        soil_code_r[soil_code > 0] = np.round(soil_code / 10000)[soil_code > 0]

        mlw = raster_to_numpy("testcase/grote_nete/input/mlw.asc")
        inundation = \
            raster_to_numpy("testcase/grote_nete/input/inundation_nutrient_level.asc")
        rainwater = raster_to_numpy("testcase/grote_nete/input/nullgrid.asc")
        seepage = raster_to_numpy("testcase/grote_nete/input/seepage.asc")
        conductivity = raster_to_numpy("testcase/grote_nete/input/conductivity.asc")
        acidity = raster_to_numpy("testcase/grote_nete/intermediate/ph.asc")
        acidity[np.isnan(acidity)] = 255
        result = a.calculate(soil_code_r, mlw, inundation, seepage,
                             conductivity, rainwater)

        np.testing.assert_equal(acidity, result)
