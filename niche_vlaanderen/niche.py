import rasterio
import rasterio.plot

import numpy as np
import numpy.ma as ma
import pandas as pd

from .vegetation import Vegetation
from .acidity import Acidity
from .nutrient_level import NutrientLevel
from .spatial_context import SpatialContext
from .version import __version__

import logging
import os.path
import numbers
import yaml
import textwrap
import datetime
import sys

_allowed_input = set([
    "soil_code", "mlw", "msw", "mhw", "seepage",
    "inundation_acidity", "inundation_nutrient", "nitrogen_atmospheric",
    "nitrogen_animal", "nitrogen_fertilizer", "management", "conductivity",
    "rainwater", "inundation_vegetation", "management_vegetation", "acidity",
    "nutrient_level"])

_minimal_input = set([
    "soil_code", "mlw", "msw", "mhw", "seepage", "inundation_acidity",
    "nitrogen_atmospheric", "nitrogen_animal", "nitrogen_fertilizer",
    "management", "conductivity", "rainwater",
    "inundation_nutrient"])

_abiotic_keys = set(["nutrient_level", "acidity"])

_code_tables = ["ct_acidity", "ct_soil_mlw_class", "ct_soil_codes",
                "lnk_acidity", "ct_seepage", "ct_vegetation", "ct_management",
                "ct_nutrient_level", "ct_mineralisation"]

logging.basicConfig()


class TypeException(Exception):
    """
    Type is not allowed
    """


class NicheException(Exception):
    """
    Exception from niche code
    """


class Niche(object):
    """ Creates a new Niche object

    A niche object can be used to predict vegetation types according to the
    NICHE Vlaanderen model.

    The default codetables are used unless other tables are supplied to the
    constructor.

    """
    def __init__(self):
        self._inputfiles = dict()
        self._inputvalues = dict()
        self._inputarray = dict()
        self._abiotic = dict()
        self._code_tables = dict()
        self._result = dict()
        self._deviation = dict()
        self._model_options=dict()
        self._files_written = dict()
        self.log = logging.getLogger()
        self._context = None
        self.occurrence = None

    def __repr__(self):
        s = "# Niche Vlaanderen version: {}\n".format(__version__)
        s += "# Run at: {}\n\n".format(datetime.datetime.now())
        # Also add some versions of the major packages we use - easy for
        # debugging
        s += "package_versions:\n"
        s += "  pandas: {}\n".format(pd.__version__)
        s += "  numpy: {}\n".format(np.__version__)
        s += "  rasterio: {}\n".format(rasterio.__version__)
        s += "  gdal: {}\n".format(rasterio.__gdal_version__)

        s += "\n"
        s += "model_options:\n"
        options = yaml.dump(self._model_options, default_flow_style=False)
        s += indent(options, "  ")

        if self._context is not None:
            s+="\nmodel_properties:\n"
            s+="  model_extent: " + str(self._context.extent) + "\n"

        s += "\n"
        s += "input_layers:\n"
        input = yaml.dump(self._inputfiles, default_flow_style=False)
        input += yaml.dump(self._inputvalues, default_flow_style=False) \
            if len(self._inputvalues)>0 else ""
        s += indent(input, "  ")



        if self.occurrence is not None:
            s += "\nmodel_result: \n"
            s += indent(
                yaml.dump(self.occurrence, default_flow_style=False), "  ")
        else:
            s += "# No model run completed."


        if len(self._files_written) > 0:
            s+= "\nfiles_written:\n"
            s += indent(
                yaml.dump(self._files_written, default_flow_style=False), "  ")

        return s

    def _set_ct(self, key, value):
        if (key not in _code_tables):
            raise TypeException("Unrecognized codetable %s" % key)

        self._code_tables[key] = value

    def set_input(self, key, value):
        """ Adds a raster or numeric value as input layer

        Parameters
        ----------
        key: string
            The type of grid that you want to assign (eg msw, soil_code, ...).
            Possible options are listed in _allowed_input
        value: string / number
            Path to a file containing the grid. Can also be a folder for
            certain grid types (eg ArcGIS rasters).
            Can also be a number: in that case a constant value is applied
            everywhere.

        """
        if (key in _code_tables):
            self._set_ct(key, value)
            return

        # check type is valid value from list
        if (key not in _allowed_input):
            raise TypeException("Unrecognized type %s" % key)

        if isinstance(value, numbers.Number):
            # Remove any existing values to make sure last value is used
            self._inputfiles.pop(key, None)
            self._inputvalues[key] = value

        else:
            with rasterio.open(value) as dst:
                sc_new = SpatialContext(dst)
            if self._context is None:
                self._context = sc_new
            else:
                if self._context != sc_new:
                    self._context.set_overlap(sc_new)
            # Remove any existing values to make sure last value is used
            self._inputvalues.pop(key, None)
            self._inputfiles[key] = value

    def read_config_input(self, config):
        """ Sets the input based on an input file, without run or output
        """
        with open(config, 'r') as stream:
            config_loaded = yaml.load(stream)

        if "code_tables" in config_loaded.keys():
            for k in config_loaded['code_tables'].keys():
                value = config_loaded['code_tables'][k]
                value = os.path.join(os.path.dirname(config), value)
                self.set_input(k, value)

        # parse input_layers
        for k in config_loaded['input_layers'].keys():
            # adjust path to be relative to the yaml file
            value = config_loaded['input_layers'][k]
            if not isinstance(value, numbers.Number):
                value = os.path.join(os.path.dirname(config), value)
            self.set_input(k, value)

    def run_config_file(self, config):
        """ Runs Niche using a configuration file

        Note that this will configure the model, run and output as specified
        """

        self.read_config_input(config)

        # Set input values
        with open(config, 'r') as stream:
            config_loaded = yaml.load(stream)

        # Set code tables

        # Run + write according to model options
        options = config_loaded["model_options"]

        deviation = "deviation" in options and options["deviation"]
        full_model = True
        if "simple_model" in options and options["simple_model"]:
            full_model = False

        self.run(full_model, deviation)

        if "output_dir" in options:
            output_dir = options["output_dir"]
        else:
            return

        self.write(output_dir)

    def _check_all_lower(self, input_array, a, b):
        if np.any((input_array[a] > input_array[b])
                          & (input_array[a] != -99)
                          & (input_array[b] != -99)):
            # find out which cells have invalid values
            bad_points = np.where(input_array[a] > input_array[b])
            # convert these cells into the projection system
            bad_points = bad_points * self._context.affine

            print("Not all {} values are lower than {}".format(a,b))
            print("coordinates with invalid values are:")
            print(pd.DataFrame(list(bad_points)))
            raise NicheException(
                "Error: not all {} values are lower than {}".format(a,b))

    def _check_input_files(self, full_model):
        """ basic input checks (valid files etc)

        """

        # Load every input_file in the input_array
        inputarray = dict()
        for f in self._inputfiles:
            dst = rasterio.open(self._inputfiles[f])

            nodata = dst.nodatavals[0]

            window = self._context.get_read_window(SpatialContext(dst))
            band = dst.read(1, window=window)

            if band.dtype == "uint8":
                band = band.astype(int)

            if f in ('mhw', 'mlw', 'msw'):
                band = band.astype(int)

            if f in ("nitrogen_animal", "nitrogen_fertilizer",
                     "nitrogen_atmospheric"):
                band = band.astype('float32')

            if f == 'soil_code' and np.all(band[band != nodata] >= 10000):
                band[band != nodata] = np.round(
                band[band != nodata] / 10000)

            # create a mask for no-data values, taking into account data-types
            if band.dtype == 'float32':
                band[band == nodata] = np.nan
            else:
                band[band == nodata] = -99



            inputarray[f] = band

        # Load in all constant inputvalues
        for f in self._inputvalues:
            shape = (int(self._context.height), int(self._context.width))
            inputarray[f] = np.full(shape, self._inputvalues[f])

        # check if valid values are used in inputarrays
        # check for valid datatypes - values will be checked in the low-level
        # api (eg soil_code present in codetable)

        self._check_all_lower(inputarray, "mhw", "mlw")

        if full_model:
            self._check_all_lower(inputarray, "msw", "mlw")
            self._check_all_lower(inputarray, "mhw", "msw")

            with np.errstate(invalid='ignore'):  # ignore NaN comparison errors
                if np.any((inputarray['nitrogen_animal'] < 0)
                          | (inputarray['nitrogen_animal'] > 10000)
                          | (inputarray['nitrogen_fertilizer'] < 0)
                          | (inputarray['nitrogen_fertilizer'] > 10000)
                          | (inputarray['nitrogen_atmospheric'] < 0)
                          | (inputarray['nitrogen_atmospheric'] > 10000)):
                    raise NicheException(
                        "Error: nitrogen values must be >0 and <10000")

        # if all is successful:
        self._inputarray = inputarray

    def run(self, full_model=True, deviation=False, abiotic=False):
        """Run the niche model

        Runs niche Vlaanderen model. Requires that the necessary input values
        have been added using set_input.

        Parameters
        ----------
        full_model: bool
                   Uses the full niche model. The simple model only uses mhw,
                   mlw and soil_code as input.

        deviation: bool
                    Create the maps with the difference between the needed MHW
                    and MLW and the actual MHW/MLW for a vegetation type.

                    Calculated results will be stored in the niche class in a
                    dict _difference
        abiotic:  bool
                Specify the abiotic grids as input rather than calculating them.

        """

        self._model_options["full_model"] = full_model
        self._model_options["deviation"] = deviation
        self._model_options["abiotic"] = abiotic

        if abiotic and not full_model:
            raise NicheException(
                "Abiotic calculation is only possible with a full model")

        if abiotic:
            missing_keys = (_abiotic_keys
                           - set(self._inputfiles.keys())
                           - set(self._inputvalues.keys()))
            if len(missing_keys) > 0:
                print("Abiotic input are missing: (abiotic=True)")
                print(missing_keys)
                raise NicheException(
                    "Error, abiotic keys are missing")

        if not abiotic and (
                (_abiotic_keys & set(self._inputfiles.keys()))
                    or (_abiotic_keys & set(self._inputvalues.keys()))):
            self.log.warning(
                "abiotic inputs specified but not specified in model options\n"
                "abiotic inputs will not be used")

        if full_model:
            missing_keys = _minimal_input - set(self._inputfiles.keys()) \
                           - set(self._inputvalues.keys())
            if len(missing_keys) > 0:
                print("Different keys are missing: ")
                print(missing_keys)
                raise NicheException(
                    "Error, different obliged keys are missing")

        self._check_input_files(full_model)

        if full_model and not abiotic:
            if sys.version_info >= (3, 3):
                keys = self._code_tables.keys()
            else:
                keys = self._code_tables.viewkeys()

            keys = keys & \
                   ['ct_acidity', 'ct_soil_mlw_class', 'ct_soil_codes',
                    'lnk_acidity', 'ct_seepage']

            ct_nl = dict()

            for k in keys:
                ct_nl[k] = self._code_tables[k]

            nl = NutrientLevel(**ct_nl)

            self._abiotic["nutrient_level"] = nl.calculate(
                soil_code=self._inputarray["soil_code"],
                msw=self._inputarray["msw"],
                nitrogen_atmospheric=self._inputarray["nitrogen_atmospheric"],
                nitrogen_animal=self._inputarray["nitrogen_animal"],
                nitrogen_fertilizer=self._inputarray["nitrogen_fertilizer"],
                management=self._inputarray["management"],
                inundation=self._inputarray["inundation_nutrient"])

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
                             mhw=self._inputarray["mhw"],
                             mlw=self._inputarray["mlw"])

        if full_model:
            veg_arguments.update(
                inundation=self._inputarray["inundation_vegetation"],
                management=self._inputarray["management_vegetation"]
            )
            if not abiotic:
                veg_arguments.update(
                    nutrient_level=self._abiotic["nutrient_level"],
                    acidity=self._abiotic["acidity"])
            else:
                veg_arguments.update(
                    nutrient_level=self._inputarray["nutrient_level"],
                    acidity=self._inputarray["acidity"])


        self._vegetation, self.occurrence = vegetation.calculate(
            full_model=full_model, **veg_arguments)

        if deviation:
            self._deviation = vegetation.calculate_deviation(
                self._inputarray["soil_code"], self._inputarray["mhw"],
                self._inputarray["mlw"]
            )

        occ_table = pd.DataFrame.from_dict(self.occurrence, orient="index")
        occ_table.columns = ['occurrence']

        # we convert the occurrence values to a table to have a pretty print
        # the values are shown as a percentage
        occ_table['occurrence'] = pd.Series(
            ["{0:.2f}%".format(v * 100) for v in occ_table['occurrence']],
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

        folder: string
            Output folder to which files will be written. Parent directory must
            exist already.

        """

        if not hasattr(self, "_vegetation"):
            raise NicheException(
                "A valid run must be done before writing the output.")

        self._model_options["output_dir"] = folder

        if not os.path.exists(folder):
            os.makedirs(folder)

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
            path = folder + '/%s.tif' % vi
            with rasterio.open(folder + '/V%s.tif' % vi, 'w', **params) as dst:
                dst.write(self._vegetation[vi], 1)
                self._files_written[vi] = os.path.normpath(path)

        # also save the abiotic grids
        for vi in self._abiotic:
            path = folder + '/%s.tif' % vi
            with rasterio.open(path, 'w', **params) as dst:
                dst.write(self._abiotic[vi], 1)
                self._files_written[vi] = os.path.normpath(path)

        # deviation
        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            affine=self._context.affine,
            count=1,
            compress="DEFLATE",
            dtype="float64",
            nodata=-99999
        )

        for i in self._deviation:
            path = folder + '/%s.tif' % i
            with rasterio.open(path, 'w', **params) as dst:
                band = self._deviation[i]
                band[band == np.nan] = -99999
                dst.write(band, 1)
                self._files_written[i] = os.path.normpath(path)


        with open(folder + "/log.txt", "w") as f:
            f.write(self.__repr__())

    def show(self, key, contour=False):
        plt = rasterio.plot.get_plt()
        fig, ax = plt.subplots()

        if key in self._inputarray:
            v = self._inputarray[key]
            v = ma.masked_equal(v, -99)
        if key in self._abiotic:
            v = self._abiotic[key]
            v = ma.masked_equal(v, 255)
        if key in self._vegetation.keys():
            v = self._vegetation[key]
            v = ma.masked_equal(v, 255)
        if key in self._deviation:
            v = self._deviation[key]

        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)
        #rasterio.plot.show(v, contour, title=key, extent=mpl_extent, ax=ax)
        plt.imshow(v, extent=mpl_extent)
        ax.set_title(key)
        plt.colorbar()
        plt.show()

def indent(s, pre):
    if sys.version_info >= (3,3):
        return textwrap.indent(s, pre)
    else:
        return pre + s.replace('\n', '\n' + pre)

class NicheDelta(object):
    """Class containing the difference between two niche runs
    """

    def __init__(self, n1, n2):
        self._delta=dict()

        self.deltaconv = dict()

        self.deltaconv[(0, 1)] = 1
        self.deltaconv[(1, 0)] = -1
        self.deltaconv[(1, 1)] = 2
        self.deltaconv[(0, 0)] = 0
        self.deltaconv[(255, 255)] = 255
        self.deltaconv[(255, 0)] = -255
        self.deltaconv[(255, 1)] = -255
        self.deltaconv[(0, 255)] = -255
        self.deltaconv[(1, 255)] = -255

        if n1._context is None or n2._context is None:
            raise NicheException(
                "No extent in Niche object. Please run both models prior to "
                "calculating a delta."
            )

        if n1._context != n2._context:
            raise NicheException(
                "Spatial contexts differ, can not make a delta")
        self._context = n1._context

        if len(n1._vegetation) == 0 or len(n2._vegetation) == 0:
            raise NicheException(
                "No vegetation in Niche object. Please run both models prior "
                "to calculating a delta."
            )

        # the error below should not occur as we check the context, but
        # better safe than sorry
        if n1._vegetation[1].size != n2._vegetation[1].size:
            raise NicheException(
                "Arrays have different size."
            )

        if len(n1._vegetation) != len(n2._vegetation):
            raise NicheException(
                "Niche vegetation objects have different length."
            )

        for vi in n1._vegetation:
            n1v = n1._vegetation[vi].flatten()
            n2v = n2._vegetation[vi].flatten()
            res = np.full( n1v.size, 4)
            res[((n1v == 0) & (n2v == 0))] = 0
            res[((n1v == 1) & (n2v == 1))] = 1
            res[((n1v == 1) & (n2v == 0))] = 2
            res[((n1v == 0) & (n2v == 1))] = 3
            res[((n1v == 255) & (n2v == 255))] = 255
            res.resize(n1._vegetation[vi].shape)
            self._delta[vi] = res

    def write(self, output_dir):
        pass

    def table(self):
        pass
