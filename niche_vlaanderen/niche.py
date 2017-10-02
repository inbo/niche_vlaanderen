import rasterio

import numpy as np
import pandas as pd

from .vegetation import Vegetation
from .acidity import Acidity
from .nutrient_level import NutrientLevel

import logging
import os.path

_allowed_input = [
    "soil_code", "mlw", "msw", "mhw", "seepage", "nutrient_level",
    "inundation_acidity", "inundation_nutrient", "nitrogen_atmospheric",
    "nitrogen_animal", "nitrogen_fertilizer", "management", "conductivity",
    "rainwater", "inundation_vegetation"]

_minimal_input = [
    "soil_code", "mlw", "msw", "mhw", "seepage", "inundation_acidity",
    "nitrogen_atmospheric", "nitrogen_animal", "nitrogen_fertilizer",
    "management", "conductivity", "rainwater", "inundation_vegetation",
    "inundation_nutrient"]

logging.basicConfig()


class SpatialContext(object):
    """Stores the spatial context of the grids in niche
    """

    def __init__(self, dst):
        self.affine = dst.affine
        self.width = dst.width
        self.heigth = dst.height
        self.crs = dst.crs

    def __eq__(self, other):
        """Compare two SpatialContexts

        Small differences (<1cm are allowed)
        """

        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.heigth == other.heigth:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.heigth == other.heigth:
            return False
        else:
            return True


class Niche(object):
    '''
    '''
    def __init__(self):
        self._inputfiles = dict()
        self._inputarray = dict()
        self._abiotic = dict()
        self._result = dict()
        self.log = logging.getLogger()
        self._context = None

    def set_input(self, type, path, set_spatial_context=False):

        if not set_spatial_context and self._context is None:
            self.log.error("Spatial context not yet set")
            return False

        if set_spatial_context and self._context is True:
            self.log.error("Spatial context can only be set once")
            return False

        # check type is valid value from list
        if (type not in _allowed_input):
            self.log.error("Unrecognized type %s" % type)
            return False

        # check file exists
        if not os.path.exists(path):
            self.log.error("File %s does not exist" % path)
            return False

        with rasterio.open(path) as dst:
            sc_new = SpatialContext(dst)
            if set_spatial_context:
                self._context = sc_new
            else:
                if self._context != sc_new:
                    self.log.error("Spatial context differs (%s)" % path)
                    self._context.affine
                    sc_new.affine
                    return False

        self._inputfiles[type] = path
        return True

    def _check_input_files(self):
        """ basic input checks (valid files etc)

        """

        # check files exist
        for f in self._inputfiles:
            if not os.path.exists(f):
                self.log.error("File %s does not exist" % f)
                return False

        # check boundaries overlap with study area + same grid
        # we should also check for files top/bottom and bottom/top
        for f in self._inputfiles:
            try:
                dst = rasterio.open(f)
            except:
                self.log.error("Error while opening file %s" % f)

        # Load every input_file in the input_array
        inputarray = dict()
        for f in self._inputfiles:
            dst = rasterio.open(self._inputfiles[f])
            nodata = dst.nodatavals[0]

            band = dst.read(1)
            # create a mask for no-data values, taking into account data-types
            if band.dtype == 'float32':
                band[band == nodata] = np.nan
            else:
                band[band == nodata] = -99

            inputarray[f] = band

        # check if valid values are used in inputarrays
        # check for valid datatypes - values will be checked in the low-level
        # api (eg soilcode present in codetable)

        if np.any(inputarray.mhw <= inputarray.mlw):
            self.log.error("Error: not all MHW values are higher than MLW")
            return False

        # if all is successful:
        self._inputarray = inputarray

        return(True)

    def run(self):
        """
        Runs niche Vlaanderen and saves the predicted vegetation to 17 grids.
        """

        missing_keys = set(_minimal_input) - set(self._inputfiles.keys())
        if len(missing_keys) > 0:
            print("error, different obliged keys are missing")
            print(missing_keys)
            return False

        if self._check_input_files is False:
            return False

        # Load every input_file in the input_array
        for f in self._inputfiles:
            with rasterio.open(self._inputfiles[f]) as dst:
                self._inputarray[f] = dst.read(1)

        nl = NutrientLevel()
        # TODO: error handling
        self._abiotic["nutrient_level"] = nl.calculate(
            self._inputarray["soil_code"], self._inputarray["msw"],
            self._inputarray["nitrogen_atmospheric"],
            self._inputarray["nitrogen_animal"],
            self._inputarray["nitrogen_fertilizer"],
            self._inputarray["management"],
            self._inputarray["inundation_nutrient"])

        acidity = Acidity()
        self._abiotic["acidity"] = acidity.calculate(
            self._inputarray["soil_code"], self._inputarray["mlw"],
            self._inputarray["inundation_acidity"],
            self._inputarray["seepage"],
            self._inputarray["conductivity"], self._inputarray["rainwater"])

        vegetation = Vegetation()
        self._vegetation, veg_occurence = vegetation.calculate(
            soil_code=self._inputarray["soil_code"],
            nutrient_level=self._abiotic["nutrient_level"],
            acidity=self._abiotic["acidity"],
            inundation=self._inputarray["inundation_vegetation"],
            mhw=self._inputarray["mhw"],
            mlw=self._inputarray["mlw"])
        occ_table = pd.DataFrame.from_dict(veg_occurence, orient="index")
        occ_table.columns = ['occurence']

        occ_table['occurence'] = pd.Series(
            ["{0:.2f}%".format(v * 100) for v in occ_table['occurence']],
            index= occ_table.index)
        print(occ_table)

    def write(self, folder):

        if not hasattr(self, "_vegetation"):
            self.log.error(
                "A valid run must be done before writing the output.")

        params = dict(
            driver='GTiff',
            height=self._context.heigth,
            width=self._context.width,
            crs=self._context.crs,
            affine=self._context.affine,
            count=1,
            dtype="int16",
            nodata=-99,
            compress="DEFLATE"
        )

        for vi in self._vegetation:
            with rasterio.open(folder + '/V%s.tif' % vi, 'w', **params) as dst:
                dst.write(self._vegetation[vi], 1)

        # also save the abiotic grids
        for vi in self._abiotic:
            with rasterio.open(folder + '/%s.tif' % vi, 'w', **params) as dst:
                dst.write(self._abiotic[vi], 1)
