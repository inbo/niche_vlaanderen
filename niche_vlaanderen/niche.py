import rasterio
from affine import Affine

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
    "management", "conductivity", "rainwater",
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
        self.height = dst.height
        self.crs = dst.crs

    def __repr__(self):
        s = "%s" \
        "width: %d, height: %d" \
        "%s" % (self.affine, self.width, self.height, self.crs)
        return s


    def __eq__(self, other):
        """Compare two SpatialContexts

        Equal to: Small differences (<1cm are allowed)
        """

        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.height == other.height:
            return True
        else:
            return False

    def __ne__(self, other):
        """ Compare two SpatialContexts

        Not equal to: Small differences are allowed
        """
        if self.affine.almost_equals(other.affine, precision=0.01)\
                and self.width == other.width and self.height == other.height:
            return False
        else:
            return True

    def check_overlap(self, new_sc):
        """Checks whether two SpatialContexts overlap

        Overlapping spatial contexts are SpatialContexts with the same grid
        dimensions (no resampling is needed to convert them).

        Overlapping SpatialContexts can be used to intersect (set_overlap) or
        can be used to define a read window.
        """
        if not ((self.affine[0] == new_sc.affine[0])
                and (self.affine[1] == new_sc.affine[1])
                and (self.affine[3] == new_sc.affine[3])
                and (self.affine[4] == new_sc.affine[4])):
            print("error: different grid size or orientation")
            return False

            # check cells overlap
        dgx = (~self.affine)[2] - (~new_sc.affine)[2]
        dgy = (~self.affine)[5] - (~new_sc.affine)[5]

        # if this differences are not integer numbers, cells do not overlap
        # we 0.01 m
        if abs(dgx - round(dgx)) > 0.01 or abs(dgy - round(dgy)) > 0.01:
            print("cells do not overlap")
            print(dgx, dgy)
            return False
        else:
            return True

    def set_overlap(self, new_sc):
        """ Gets the window to be read from a different SpatialContext

        """
        # Check orientation and cell size are equal
        if not self.check_overlap(new_sc):
            return None

        # determine the extent in the old and new system
        extent_self = (self.affine) * (0,0), \
                      (self.affine) * (self.width, self.height)

        extent_new = (new_sc.affine) * (0,0),\
                     (new_sc.affine) * (new_sc.width, new_sc.height)

        # The startpoint of the combined raster is the left coordinate
        # (if the 0th coefficient of affine is positive). and the bottom
        # coordinate (if the 4th coefficient is negative)


        if self.affine[0] > 0:
            extent_x = (max(extent_self[0][0], extent_new[0][0]),
                        min(extent_self[1][0], extent_new[1][0]))
        else:
            extent_x = (min(extent_self[0][0], extent_new[0][0]),
                        max(extent_self[1][0], extent_new[1][0]))

        if self.affine[4] > 0:
            extent_y = max(extent_self[0][1], extent_new[0][1]),\
                       min(extent_self[1][1], extent_new[1][1])
        else:
            extent_y = min(extent_self[0][1], extent_new[0][1]),\
                       max(extent_self[1][1], extent_new[1][1])

        self.width = round((extent_x[1] - extent_x[0]) / self.affine[0])
        self.height = round((extent_y[1] - extent_y[0]) / self.affine[4])

        self.affine = Affine(self.affine[0], self.affine[1], extent_x[0],
                             self.affine[3], self.affine[4], extent_y[0])

        return True

    def get_read_window(self, new_sc):
        if not self.check_overlap(new_sc):
            return None

        # TODO: error on negative values

        gminxy = (~new_sc.affine) *((0,0) * self.affine)
        gmaxxy = (~new_sc.affine) *(
            (self.width, self.height) * self.affine)

        return (gminxy[1], gmaxxy[1]), (gminxy[0], gmaxxy[0])




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
                self._context.set_overlap(sc_new)

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

        if np.any(inputarray.msw <= inputarray.mlw):
            self.log.error("Error: not all MSW values are higher than MLW")
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

            if self._check_input_files is False:
                return False

        # Load every input_file in the input_array
        for f in self._inputfiles:
            with rasterio.open(self._inputfiles[f]) as dst:
                window = self._context.get_read_window(SpatialContext(dst))
                self._inputarray[f] = dst.read(
                    1, window = window)

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

        veg_arguments = dict(soil_code=self._inputarray["soil_code"],
                mhw=self._inputarray["mhw"], mlw=self._inputarray["mlw"])

        if full_model:
            veg_arguments.update(
                nutrient_level=self._abiotic["nutrient_level"],
                acidity=self._abiotic["acidity"])

        self._vegetation, veg_occurence = vegetation.calculate(
            full_model=full_model, **veg_arguments)


        occ_table = pd.DataFrame.from_dict(veg_occurence, orient="index")
        occ_table.columns = ['occurence']

        # we convert the occurence values to a table to have a pretty print
        # the values are shown as a percentage
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
            height=self._context.height,
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

    def _readInputPartial(self, path):
        """Reads a window of a raster file based on the current SpatialContext
        """
        if self._context is None:
            self.log.error("Spatial context not yet set")
            return False

        with rasterio.open(path) as dst:
            sc_new = SpatialContext(dst)
