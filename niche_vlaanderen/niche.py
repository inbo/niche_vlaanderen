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

    This class is based on the rasterio model of a grid.

    Attributes
    affine: Affine
        Matrix that contains the affine transformation of the plane to convert
        grid coordinates to real world coordinates.
        https://pypi.python.org/pypi/affine/1.0
    width, height: int
        Integer numbers containing the width and height of the raster
    crs: rasterio.CRS
        Container class for coordinate reference system info

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
    """ Creates a new Niche object

    A niche object can be used to predict vegetation types according to the
    NICHE Vlaanderen model.

    The default codetables are used unless other tables are supplied to the
    constructor.

    """
    def __init__(self):
        self._inputfiles = dict()
        self._inputarray = dict()
        self._abiotic = dict()
        self._result = dict()
        self.log = logging.getLogger()
        self._context = None

    def set_input(self, type, path, set_spatial_context=False):
        """ Adds a raster as input layer

        Parameters
        ----------
        type: string
            The type of grid that you want to assign (eg msw, soil_code, ...).
            Possible options are listed in _allowed_input
        path: string
            Path to a file containing the grid. Can also be a folder for
            certain grid types (eg arcgis rasters).

        Returns
        -------
        bool
            Boolean that will be true if the file was added successfully and
            false otherwise.

        """
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
        """Run the niche model

        Runs niche Vlaanderen model. Requires that the necessary input values
        have been added using set_input.

        Returns
        -------

        bool:
            Returns true if the calculation was succesfull.
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
            index=occ_table.index)
        print(occ_table)

    def write(self, folder):
        """Saves the model results to a folder

        Saves the model results to a folder. Files will be written as geotiff.
        Vegetation files have names V1 ... V28
        Abiotic files are exported as well (nutrient_level.tif and
        acidity.tif).

        Parameters
        ----------

        Folder: string
            Output folder to which files will be written. Parent directory must
            exist already.

        Returns
        -------

        bool:
            Returns True on success.
        """

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
