from unittest import TestCase

import rasterio
import numpy as np
import niche_vlaanderen
import pytest
from niche_vlaanderen.exception import NicheException


def raster_to_numpy(filename):
    """Read a GDAL grid as numpy array

    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    """
    with rasterio.open(filename) as ds:
        data = ds.read(1)
        nodata = ds.nodatavals[0]
    print(nodata)
    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float32':
        data[np.isclose(data, nodata)] = np.nan
    else:
        data[np.isclose(data, nodata)] = -99

    return data


class testAcidity(TestCase):

    def test_get_soil_mlw(self):
        mlw = np.array([50, 66])
        soil_code = np.array([14, 7])
        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)

        np.testing.assert_equal(np.array([1, 9]), result)

    def test_get_soil_mlw_borders(self):
        mlw = np.array([79, 80, 100, 110, 111])
        soil_code = np.array([14, 14, 14, 14, 14])
        a = niche_vlaanderen.Acidity()
        result = a._calculate_soil_mlw(soil_code, mlw)
        expected = np.array([1, 1, 2, 2, 3])
        np.testing.assert_equal(expected, result)

    def test_acidity_partial(self):
        rainwater = np.array([0])
        minerality = np.array([1])
        inundation = np.array([1])
        seepage = np.array([1])
        soil_mlw = np.array([1])

        a = niche_vlaanderen.Acidity()
        result = a._get_acidity(rainwater, minerality, inundation,
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
        minerality = np.array([0])
        soilcode = np.array([14])
        inundation = np.array([1])
        seepage = np.array([20])
        mlw = np.array([50])

        a = niche_vlaanderen.Acidity()
        result = a.calculate(soilcode, mlw, inundation, seepage, minerality,
                             rainwater)
        np.testing.assert_equal(3, result)

    def test_acidity_testcase(self):
        a = niche_vlaanderen.Acidity()
        inputdir = "testcase/zwarte_beek/input/"
        soil_code = raster_to_numpy(inputdir + "soil_code.asc")
        soil_code_r = soil_code
        soil_code_r[soil_code > 0] = np.round(soil_code / 10000)[soil_code > 0]

        mlw = raster_to_numpy(inputdir + "mlw.asc")
        inundation = \
            raster_to_numpy(inputdir + "inundation.asc")
        rainwater = raster_to_numpy(inputdir + "nullgrid.asc")
        seepage = raster_to_numpy(inputdir + "seepage.asc")
        minerality = raster_to_numpy(inputdir + "minerality.asc")
        acidity = raster_to_numpy("testcase/zwarte_beek/abiotic/acidity.asc")
        acidity[np.isnan(acidity)] = 255
        acidity[acidity == -99] = 255
        result = a.calculate(soil_code_r, mlw, inundation, seepage,
                             minerality, rainwater)

        np.testing.assert_equal(acidity, result)

    def test_acidity_invalidsoil(self):
        a = niche_vlaanderen.Acidity()
        rainwater = np.array([0])
        minerality = np.array([0])
        soilcode = np.array([-1])
        inundation = np.array([1])
        seepage = np.array([20])
        mlw = np.array([50])

        a = niche_vlaanderen.Acidity()
        with pytest.raises(NicheException):
            a.calculate(soilcode, mlw, inundation, seepage, minerality,
                        rainwater)

    def test_acidity_invalidminerality(self):
        a = niche_vlaanderen.Acidity()
        rainwater = np.array([0])
        minerality = np.array([500])
        soilcode = np.array([14])
        inundation = np.array([1])
        seepage = np.array([20])
        mlw = np.array([50])
        with pytest.raises(NicheException):
            a.calculate(soilcode, mlw, inundation, seepage, minerality,
                        rainwater)
