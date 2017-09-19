from unittest import TestCase
from osgeo import gdal
from osgeo import osr

import numpy as np

import niche_vlaanderen

def raster_to_numpy(filename):
    '''Read a GDAL grid as numpy array
    
    Notes
    ------
    No-data values are -99 for integer types and np.nan for real types.
    '''
    # Read the raster file with GDAL
    ds = gdal.Open(filename)

    #  Extract the data, transformation and projection information
    data = ds.ReadAsArray()
    gt = ds.GetGeoTransform()
    raster_wkt = ds.GetProjection()
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(raster_wkt)
    proj = spatial_ref.ExportToProj4()
    
    nodata = ds.GetRasterBand(1).GetNoDataValue()
    # create a mask for no-data values, taking into account the data-types
    if data.dtype == 'float32':
        data[data == nodata] = np.nan
    else:
        data[data == nodata] = -99
    
    # destroy the gdal object
    del ds
    return data

class testAcidity(TestCase):

    def test_get_soil_mlw(self):
        mlw = np.array([50,66])
        soil_codes = np.array([140000, 40000])
        a = niche_vlaanderen.Acidity()
        result = a._get_soil_mlw(soil_codes, mlw)

        np.testing.assert_equal(np.array([1, 9]), result)

    def test_minerality_class(self):
        conductivity = np.array([500, 100, np.nan, 700])
        a = niche_vlaanderen.Acidity()
        result = a._get_mineral_richness_class(conductivity)
        
        np.testing.assert_equal(np.array([2,1,-99, 2]), result)

    def test_acidity_partial(self):
        regenlens = np.array([1])
        mineral_richness = np.array([1])
        inundation = np.array([1])
        seepage = np.array([1])
        soil_mlw = np.array([1])
        
        a = niche_vlaanderen.Acidity()
        result = a._get_acidity(regenlens, mineral_richness, inundation, 
            seepage, soil_mlw)
        
        np.testing.assert_equal(np.array([3]), result)

    def test_seepage_code(self):
        seepage = np.array([5, 0.3, 0.05, -0.04, -0.2, -5])
        a = niche_vlaanderen.Acidity()
        result = a._get_seepage_code(seepage)
        
        # expected below is what you expect from original codetable
        # this is different from the documentation
        # https://github.com/inbo/niche_vlaanderen/issues/9
        expected = np.array([1,1,1,1,2,3])
        np.testing.assert_equal(expected, result)

    def test_acidity(self):
        regenlens = np.array([1])
        conductivity = np.array([400])
        soilcode = np.array([140000])
        inundation = np.array([1])
        seepage = np.array([20])
        mlw = np.array([50])
        
        a = niche_vlaanderen.Acidity()
        result = a.get_acidity(soilcode, mlw, inundation, seepage, regenlens, conductivity)
        np.testing.assert_equal(3, result)

    def test_acidity_testcase(self):
        a = niche_vlaanderen.Acidity()
        soil_code = raster_to_numpy("testcase/input/soil_codes.asc")
        mlw = raster_to_numpy("testcase/input/mlw.asc")
        inundation = raster_to_numpy("testcase/input/inundation_nutrient_level.asc")
        regenlens = raster_to_numpy("testcase/input/nullgrid.asc")
        seepage = raster_to_numpy("testcase/input/seepage.asc")
        conductivity = raster_to_numpy("testcase/input/conductivity.asc")
        
        
        acidity = raster_to_numpy("testcase/intermediate/ph.asc")
        result = a.get_acidity(soil_code, mlw, inundation, seepage, regenlens, conductivity)
        