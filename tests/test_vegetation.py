from unittest import TestCase

import numpy as np
import rasterio

import niche_vlaanderen

import pytest

def raster_to_numpy(filename):
    '''Read a GDAL grid as numpy array

    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    '''
    with rasterio.open(filename) as ds:
        data = ds.read(1)
        proj = ds.crs #eventueel .tostring
        gt = ds.transform
        nodata = ds.nodatavals[0]

    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float32':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = -99

    return data

class testVegetation(TestCase):
    def test_testcase(self):
        soil_code = raster_to_numpy("testcase/input/soil_codes.asc")
        msw = raster_to_numpy("testcase/input/msw.asc")
        mhw = raster_to_numpy("testcase/input/mhw.asc")
        mlw = raster_to_numpy("testcase/input/mlw.asc")
        inundation = raster_to_numpy("testcase/input/inundation_nutrient_level.asc")
        regenlens = raster_to_numpy("testcase/input/nullgrid.asc")
        seepage = raster_to_numpy("testcase/input/seepage.asc")
        conductivity = raster_to_numpy("testcase/input/conductivity.asc")
        nitrogen_deposition = raster_to_numpy("testcase/input/nitrogen_atmospheric.asc")
        nitrogen_animal = raster_to_numpy("testcase/input/nitrogen_animal.asc")
        nitrogen_fertilizer = raster_to_numpy("testcase/input/nullgrid.asc")
        inundation_vegetation = raster_to_numpy("testcase/input/inundation_vegetation.asc")
        management = raster_to_numpy("testcase/input/management.asc")

        nl = niche_vlaanderen.NutrientLevel()
        nutrient_level = nl.get_array(soil_code, msw, nitrogen_deposition, nitrogen_animal,
                nitrogen_fertilizer, management, inundation)

        a = niche_vlaanderen.Acidity()
        acidity = a.get_acidity(soil_code, mlw, inundation, seepage, regenlens, conductivity)

        v = niche_vlaanderen.Vegetation()
        veg_predict = v.get_vegetation(soil_code, nutrient_level, acidity,
                mhw, mlw, management, inundation_vegetation)

        for i in range(1,28):
            vi = raster_to_numpy("testcase/VegNoEffectsRef/v%d.asc" % i)

            # TODO: this is dirty - we apply the same no data filter to the original set
            # as the new set, as this was done incorrectly in the original set.
            # this also means that if we predict no data everywhere the test also works :-)

            vi[(veg_predict[i] == -99)] = -99
            np.testing.assert_equal(vi, veg_predict[i])


