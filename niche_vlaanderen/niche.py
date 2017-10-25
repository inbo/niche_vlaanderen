import rasterio

import numpy as np
import pandas as pd

from .vegetation import Vegetation
from .acidity import Acidity
from .nutrient_level import NutrientLevel
from .spatial_context import SpatialContext

import logging
import os.path

_allowed_input = [
    "soil_code", "mlw", "msw", "mhw", "seepage", "nutrient_level",
    "inundation_acidity", "inundation_nutrient", "nitrogen_atmospheric",
    "nitrogen_animal", "nitrogen_fertilizer", "management", "conductivity",
    "rainwater", "inundation_vegetation", "management_vegetation"]

_minimal_input = [
    "soil_code", "mlw", "msw", "mhw", "seepage", "inundation_acidity",
    "nitrogen_atmospheric", "nitrogen_animal", "nitrogen_fertilizer",
    "management", "conductivity", "rainwater",
    "inundation_nutrient"]

logging.basicConfig()

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

    def set_input(self, type, path):
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
        if self._context is None:
            self._context = sc_new
        else:
            if self._context != sc_new:
                self._context.set_overlap(sc_new)

        self._inputfiles[type] = path
        return True

    def _check_input_files(self, full_model):
        """ basic input checks (valid files etc)

        """

        # check files exist
        for f in self._inputfiles:
            p = self._inputfiles[f]
            if not os.path.exists(p):
                self.log.error("File %s does not exist" % p)
                return False

        # Load every input_file in the input_array
        inputarray = dict()
        for f in self._inputfiles:
            try:
                dst = rasterio.open(self._inputfiles[f])
            except:
                self.log.error("Error while opening file %s" % f)
                return False

            nodata = dst.nodatavals[0]

            window = self._context.get_read_window(SpatialContext(dst))
            band = dst.read(1, window = window)

            if band.dtype == "uint8":
                band = band.astype(int)

            if f in ('mhw','mlw','msw'):
                band = band.astype(int)

            if f in ("nitrogen_animal", "nitrogen_fertilizer",
                     "nitrogen_atmospheric"):
                band = band.astype('float32')

            # create a mask for no-data values, taking into account data-types
            if band.dtype == 'float32':
                band[band == nodata] = np.nan
            else:
                band[band == nodata] = -99

            inputarray[f] = band

        # check if valid values are used in inputarrays
        # check for valid datatypes - values will be checked in the low-level
        # api (eg soilcode present in codetable)

        if np.any((inputarray['mhw'] > inputarray['mlw'])
                          & (inputarray["mhw"] != -99)):
            self.log.error("Error: not all MHW values are lower than MLW:")
            badpoints = np.where(inputarray['mhw'] > inputarray['mlw'])
            print (badpoints * self._context.affine)
            #return False

        if full_model:
            if np.any((inputarray['msw'] > inputarray['mlw'])
                    & (inputarray["mhw"] != -99)
                    & (inputarray["msw"] != -99)):
                self.log.error("Error: not all MSW values are lower than MLW:")
                badpoints = np.where(inputarray['mhw'] > inputarray['mlw'])
                print (badpoints)
                print (badpoints * self._context.affine)
                return False

            with np.errstate(invalid='ignore'): # ignore NaN comparison errors
                if np.any((inputarray['nitrogen_animal'] < 0)
                        | (inputarray['nitrogen_animal'] > 10000)
                        | (inputarray['nitrogen_fertilizer'] < 0)
                        | (inputarray['nitrogen_fertilizer'] > 10000)
                        | (inputarray['nitrogen_atmospheric'] < 0)
                        | (inputarray['nitrogen_atmospheric'] > 10000)):
                    self.log.error(
                        "Error: nitrogen values must be >0 and <10000")
                    return False

        # if all is successful:
        self._inputarray = inputarray

        return(True)

    def run(self, full_model=True):
        """Run the niche model

        Runs niche Vlaanderen model. Requires that the necessary input values
        have been added using set_input.

        Returns
        -------

        bool:
            Returns true if the calculation was succesfull.
        """
        if full_model:
            missing_keys = set(_minimal_input) - set(self._inputfiles.keys())
            if len(missing_keys) > 0:
                print("error, different obliged keys are missing")
                print(missing_keys)
                return False

        if self._check_input_files(full_model) is False:
            return False

        if full_model:
            nl = NutrientLevel()

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
                self._inputarray["conductivity"],
                self._inputarray["rainwater"])

        vegetation = Vegetation()
        if "inundation_vegetation" not in self._inputarray:
            self._inputarray["inundation_vegetation"] = None

        if "management_vegetation" not in self._inputarray:
            self._inputarray["management_vegetation"] = None

        veg_arguments = dict(soil_code=self._inputarray["soil_code"],
                mhw=self._inputarray["mhw"], mlw=self._inputarray["mlw"])

        if full_model:
            veg_arguments.update(
                nutrient_level=self._abiotic["nutrient_level"],
                acidity=self._abiotic["acidity"],
                inundation=self._inputarray["inundation_vegetation"],
                management=self._inputarray["management_vegetation"]
            )

        self._vegetation, self.occurence = vegetation.calculate(
            full_model=full_model, **veg_arguments)

        occ_table = pd.DataFrame.from_dict(self.occurence, orient="index")
        occ_table.columns = ['occurence']

        # we convert the occurence values to a table to have a pretty print
        # the values are shown as a percentage
        occ_table['occurence'] = pd.Series(
            ["{0:.2f}%".format(v * 100) for v in occ_table['occurence']],
            index=occ_table.index)
        print(occ_table)

    def calculate_difference(self):
        """Calculates the amount MHW/MLW should change to allow vegetation type

        Creates the maps with the difference between the needed MHW and MLW
        and the actual MHW/MLW for a vegetation type.

        Calculated results will be stored in the niche class in a dict
        _difference

        keys are "mhw_01" etc
        """
        if self._check_input_files(full_model=False) == False:
            return False

        v = Vegetation()
        self._difference = v.calculate_difference(
            self._inputarray["soil_code"], self._inputarray["mhw"],
            self._inputarray["mlw"]
        )

    def write(self, folder):
        """Saves the model results to a folder

        Saves the model results to a folder. Files will be written as geotiff.
        Vegetation files have names V1 ... V28
        Abiotic files are exported as well (nutrient_level.tif and
        acidity.tif).

        Parameters
        ----------

        folder: string
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
            return False

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                self.log.error("Error creating path")
                return False

        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            affine=self._context.affine,
            count=1,
            dtype="uint8",
            nodata=255,
            compress="DEFLATE"
        )

        for vi in self._vegetation:
            with rasterio.open(folder + '/V%s.tif' % vi, 'w', **params) as dst:
                dst.write(self._vegetation[vi], 1)

        # also save the abiotic grids
        for vi in self._abiotic:
            with rasterio.open(folder + '/%s.tif' % vi, 'w', **params) as dst:
                dst.write(self._abiotic[vi], 1)

    def write_difference(self, folder):
        """Write the calculated differences to a folder

        Saves the modeled differences to a folder. Files will be written as
        geotiff. Files will have names mhw_01.tif, mlw_01.tif

        Parameters
        ----------

        folder: string
            Output folder to which files will be written. Parent directory must
            exist already.

        Returns
        -------

        bool:
            Returns True on success.
        """
        if not hasattr(self, "_difference"):
            self.log.error(
                "A valid calculate_difference must be done before writing the output.")
            return False

        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
            except OSError as e:
                self.log.error("Error creating path")
                return False

        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            affine=self._context.affine,
            count=1,
            compress="DEFLATE",
            dtype="float64",
            nodata = -99999
        )

        for i in self._difference:
            with rasterio.open(folder + '/%s.tif' % i, 'w', **params) as dst:
                band = self._difference[i]
                band[band==np.nan] = -99999
                dst.write(band, 1)

        return True
