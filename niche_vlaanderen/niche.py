import rasterio
import rasterstats

import numpy as np
import numpy.ma as ma
import pandas as pd

from .vegetation import Vegetation
from .acidity import Acidity
from .nutrient_level import NutrientLevel
from .spatial_context import SpatialContext
from .version import __version__
from .floodplain import FloodPlain

from pkg_resources import resource_filename

import logging
import os.path
import numbers
import yaml
import datetime

_allowed_input = {
    "soil_code", "mlw", "msw", "mhw", "seepage",
    "inundation_acidity", "inundation_nutrient", "nitrogen_atmospheric",
    "nitrogen_animal", "nitrogen_fertilizer", "management", "minerality",
    "rainwater", "inundation_vegetation", "management_vegetation", "acidity",
    "nutrient_level"}

_minimal_input = {
    "soil_code", "mlw", "msw", "mhw", "seepage", "inundation_acidity",
    "nitrogen_atmospheric", "nitrogen_animal", "nitrogen_fertilizer",
    "management", "minerality", "rainwater",
    "inundation_nutrient"}


def minimal_input():  # pragma: no cover
    return _minimal_input


_abiotic_keys = {"nutrient_level", "acidity"}

_code_tables = ["ct_acidity", "ct_soil_mlw_class", "ct_soil_codes",
                "lnk_acidity", "ct_seepage", "ct_vegetation", "ct_management",
                "ct_nutrient_level", "ct_mineralisation"]

logging.basicConfig()


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
    def __init__(self, config=None, ct_acidity=None, ct_soil_mlw_class=None,
                 ct_soil_codes=None, lnk_acidity=None, ct_seepage=None,
                 ct_vegetation=None, ct_management=None,
                 ct_nutrient_level=None, ct_mineralisation=None):
        self._inputfiles = dict()
        self._inputvalues = dict()
        self._inputarray = dict()
        self._abiotic = dict()
        self._code_tables = dict()
        self._vegetation = dict()
        self._deviation = dict()
        self._options = dict()
        self._options["name"] = ""
        self._options["strict_checks"] = True
        self._files_written = dict()
        self._log = logging.getLogger("niche_vlaanderen")
        self._context = None
        self.occurrence = None

        for k in _code_tables:
            ct = locals()[k]
            if ct is not None:
                self._set_ct(k, ct)

        if ct_vegetation is None:
            self._set_ct("ct_vegetation", resource_filename(
                "niche_vlaanderen",
                "system_tables/niche_vegetation.csv"))

    @property
    def name(self):
        return self._options["name"]

    @name.setter
    def name(self, name):
        self._options["name"] = str(name)

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
        options = yaml.dump(self._options, default_flow_style=False)
        s += indent(options, "  ")

        if len(self._code_tables) > 0:
            s += "\n\n"
            s += "code_tables:\n"
            s += indent(
                yaml.dump(self._code_tables, default_flow_style=False), "  ")

        if self._context is not None:
            s += "\nmodel_properties:\n"
            s += "  model_extent: " + str(self._context.extent) + "\n"

        s += "\n"
        s += "input_layers:\n"
        input = yaml.dump(self._inputfiles, default_flow_style=False)
        input += yaml.dump(self._inputvalues, default_flow_style=False) \
            if len(self._inputvalues) > 0 else ""
        s += indent(input, "  ")

        if self.occurrence is not None:
            s += "\nmodel_result: \n"
            s += indent(
                yaml.dump(self.occurrence, default_flow_style=False), "  ")
        else:
            s += "# No model run completed."

        if len(self._files_written) > 0:
            s += "\nfiles_written:\n"
            s += indent(
                yaml.dump(self._files_written, default_flow_style=False), "  ")

        return s

    def _set_ct(self, key, value):
        if (key not in _code_tables):
            raise NicheException("Unrecognized codetable %s" % key)

        if not os.path.isfile(value):
            raise NicheException("Cannot find file %s" % key)

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

        # check type is valid value from list
        if (key not in _allowed_input):
            raise NicheException("Unrecognized type %s" % key)

        if self.vegetation_calculated:
            self._log.warning("Setting new input after model run, "
                      "clearing results")
            self._clear_result()

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
                self._set_ct(k, value)

        # parse input_layers
        for k in config_loaded['input_layers'].keys():
            # adjust path to be relative to the yaml file
            value = config_loaded['input_layers'][k]
            if not isinstance(value, numbers.Number):
                value = os.path.join(os.path.dirname(config), value)
            self.set_input(k, value)

        if "model_options" in config_loaded.keys():
            if "name" in config_loaded["model_options"].keys():
                self.name = config_loaded["model_options"]["name"]
            if "strict_checks" in config_loaded["model_options"].keys():
                self._options["strict_checks"] = \
                    config_loaded["model_options"]["strict_checks"]

        if "inundation" in config_loaded.keys():
            self._options["inundation"]=[]
            for scen_nr in config_loaded["inundation"]:
                print (scen_nr)
                scen = {k: scen_nr[k]
                        for k in ["name", "depth", "period", "frequency",
                                  "duration"]}
                self._options["inundation"].append(scen)



    def run_config_file(self, config):
        """ Runs Niche using a configuration file

        Note that this will configure the model, run and output as specified
        """

        self.read_config_input(config)

        # Set input values
        with open(config, 'r') as stream:
            config_loaded = yaml.load(stream)

        # Set code tables TODO?

        # Run + write according to model options
        options = config_loaded["model_options"]

        deviation = "deviation" in options and options["deviation"]
        full_model = True
        if "full_model" in options and not options["full_model"]:
            full_model = False

        self.run(full_model, deviation)

        if "inundation" in self._options:
            for scen in self._options["inundation"]:
                self.fp = FloodPlain() #TODO overwrite code tables
                self.fp.calculate(depth_file=scen["depth"],
                                  period=scen["period"],
                                  frequency=scen["frequency"],
                                  duration=scen["duration"])
                self.fp.combine(self)
                if "output_dir" in options:
                    self.fp.write(options["output_dir"])
                    print(self.fp._files_written)
                    self._files_written.update(self.fp._files_written)


        if "output_dir" in options:
            output_dir = options["output_dir"]
            self.write(output_dir)

    def _check_all_lower(self, input_array, a, b):
        if np.any((input_array[a] > input_array[b])
                  & (input_array[a] != -99)
                  & (input_array[b] != -99)):
            # find out which cells have invalid values
            bad_points = np.where(input_array[a] > input_array[b])
            # convert these cells into the projection system
            bad_points = bad_points * self._context.transform

            print("Warning: Not all {} values are lower than {}".format(a, b))
            print("coordinates with invalid values are:")
            print(pd.DataFrame(list(bad_points)))

            if self._options["strict_checks"]:
                raise NicheException(
                    "Error: not all {} values are lower than {}".format(a, b))

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
                band[band != nodata] = np.round(band[band != nodata] / 10000)

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

    def run(self, full_model=True, deviation=False, abiotic=False, strict_checks=True):
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
                Specify the abiotic grids as input rather than calculating
                them.

        """

        self._options["full_model"] = full_model
        self._options["deviation"] = deviation
        self._options["abiotic"] = abiotic
        self._options["strict_checks"] = strict_checks

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
            self._log.warning(
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
            ct_nl = dict()

            keys = set(NutrientLevel.__init__.__code__.co_varnames) \
                & set(self._code_tables)

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

            ct_acidity = dict()

            keys = set(Acidity.__init__.__code__.co_varnames) \
                & set(self._code_tables)

            for k in keys:
                ct_acidity[k] = self._code_tables[k]

            acidity = Acidity(**ct_acidity)
            self._abiotic["acidity"] = acidity.calculate(
                self._inputarray["soil_code"], self._inputarray["mlw"],
                self._inputarray["inundation_acidity"],
                self._inputarray["seepage"],
                self._inputarray["minerality"],
                self._inputarray["rainwater"])

        ct_veg = dict()

        keys = set(Vegetation.__init__.__code__.co_varnames) \
            & set(self._code_tables)

        for k in keys:
            ct_veg[k] = self._code_tables[k]

        vegetation = Vegetation(**ct_veg)
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

        if not self.vegetation_calculated:
            raise NicheException(
                "A valid run must be done before writing the output.")

        self._options["output_dir"] = folder

        if not os.path.exists(folder):
            os.makedirs(folder)

        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            dtype="uint8",
            nodata=255,
            compress="DEFLATE"
        )

        prefix = ""
        if self.name != "":
            prefix=self.name + "_"
        for vi in self._vegetation:
            path = folder + '/{}V{:02d}.tif'.format(prefix,vi)
            with rasterio.open(path, 'w', **params) as dst:
                dst.write(self._vegetation[vi], 1)
                self._files_written[vi] = os.path.normpath(path)

        # also save the abiotic grids
        for vi in self._abiotic:
            path = folder + '/{}{}.tif'.format(prefix,vi)
            with rasterio.open(path, 'w', **params) as dst:
                dst.write(self._abiotic[vi], 1)
                self._files_written[vi] = os.path.normpath(path)

        # deviation
        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            compress="DEFLATE",
            dtype="float64",
            nodata=-99999
        )

        for i in self._deviation:
            path = folder + '/{}{}.tif'.format(prefix, i)
            with rasterio.open(path, 'w', **params) as dst:
                band = self._deviation[i]
                band[band == np.nan] = -99999
                dst.write(band, 1)
                self._files_written[i] = os.path.normpath(path)

        with open(folder + "/{}log.txt".format(prefix), "w") as f:
            f.write(self.__repr__())

    def plot(self, key, ax=None, fixed_scale=True):
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.colors import Normalize

        except (ImportError, RuntimeError):  # pragma: no cover
            msg = "Could not import matplotlib\n"
            msg += "matplotlib required for plotting functions"
            raise ImportError(msg)

        norm = None
        v = None

        if key in self._inputfiles and key not in self._inputarray:
            # if set_input has been done, but no model run yet
            # in this case we will open the file and fetch the data
            with rasterio.open(self._inputfiles[key]) as dst:
                window = self._context.get_read_window(SpatialContext(dst))
                v = dst.read(1, window=window)
                v = ma.masked_equal(v, dst.nodatavals[0])
            title = key

        if key in self._inputarray:
            v = self._inputarray[key]
            v = ma.masked_equal(v, -99)
            title = key
        if key in self._abiotic:
            v = self._abiotic[key]
            v = ma.masked_equal(v, 255)
            title = key
        if key in self._vegetation.keys():
            v = self._vegetation[key]
            v = ma.masked_equal(v, 255)
            title = "{} ({})".format(self._vegcode2name(key), key)
        if key in self._deviation:
            v = self._deviation[key]
            title = key
            if fixed_scale:
                norm = Normalize(-50, 50)

        if v is None:
            raise NicheException("Invalid key specified")

        if ax is None:
            fig, ax = plt.subplots()

        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)

        im = plt.imshow(v, extent=mpl_extent, norm=norm)

        ax.set_title(title)

        if key in self._vegetation:
            labels = ["not present", "present"]
            values = [0, 1]

            colors = [im.cmap(value / (len(values) - 1)) for value in values]
            patches = [mpatches.Patch(color=colors[i],
                                      label=labels[i]) for i in values]
            plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2,
                       borderaxespad=0.)
        else:
            plt.colorbar()

        return(ax)

    @property
    def table(self):
        """Dataframe containing the potential area (m**2) per vegetation type
        """

        if not self.vegetation_calculated:
            raise NicheException(
                "Error: You must run niche prior to requesting the result table")

        td = list()

        presence = dict({0: "not present", 1: "present", 255: "no data"})

        for i in self._vegetation:
            vi = pd.Series(self._vegetation[i].flatten())
            rec =  vi.value_counts() * self._context.cell_area
            for a in rec.index:
                td.append((i,presence[a],rec[a]))

        df = pd.DataFrame(td, columns=['vegetation', 'presence',
                                       'area'])

        return df

    def zonal_stats(self, vectors):
        """Calculates zonal statistics using vectors

        Parameters
        ==========
        vectors: path to a vector source or geo-like python objects
        you can specify a path to a vector file eg "../test.shp", or pass
        geo objects from other python functions.

        Note that the vector should be in the same coordinate system as the
        raster.

        Returns
        =======
        dataframe. The index of the dict is the vector.
        """
        td = dict()
        for i in self._vegetation:
            # Note we use -99 as nodata value to make sure the true nodata
            # value (255) is part of the result table.

            td[i] = rasterstats.zonal_stats(vectors=vectors,
                                            raster=self._vegetation[i],
                                            affine=self._context.transform,
                                            categorical=True,
                                            nodata=-99)

        rs_result = pd.DataFrame.from_dict(td, orient='index')

        ti = list()

        presence = dict({0: "not present", 1: "present", 255: "no data"})

        for vi in td:
            for shape_i, rec in enumerate(td[vi]):
                for a in rec:
                    ti.append((vi, shape_i, presence[int(a)],
                               rec[a] * self._context.cell_area))

        df_list=dict()

        df = pd.DataFrame(ti, columns=['vegetation', 'shape_id', 'presence',
                                       'area'])

        return df

    def _vegcode2name(self, vegcode):
        """Converts a vegetation code to a name

        Uses ct_vegetation columns veg_code and veg_type"""

        if not hasattr(self, "_vegcode2namedict"):
            self._ct_vegetation = pd.read_csv(
                self._code_tables["ct_vegetation"])
            subtable = self._ct_vegetation[["veg_code", "veg_type"]]
            veg_dict = subtable.set_index("veg_code").to_dict()["veg_type"]
            self._vegcode2namedict = veg_dict
        return self._vegcode2namedict[vegcode]

    @property
    def vegetation_calculated(self):
        return len(self._vegetation)>0

    def _clear_result(self):
        """Clears calculated vegetation"""
        self._vegetation.clear()
        self._deviation.clear()


def indent(s, pre):
    return pre + s.replace('\n', '\n' + pre)


class NicheDelta(object):
    """Class containing the difference between two niche runs

    The difference can be visualized using the plot method. It is also
    possible to derive a table with the area's according to each group.
    """

    _values = [0, 1, 2, 3, 4]
    _labels = ["not present in both models", "present in both models",
               "only in model 1", "only in model 2",
               "nodata in one model"]

    def __init__(self, n1, n2):
        self._delta = dict()

        if n1._context is None or n2._context is None:
            raise NicheException(
                "No extent in Niche object. Please run both models prior to "
                "calculating a delta."
            )

        if n1._context != n2._context:
            raise NicheException(
                "Spatial contexts differ, can not make a delta\n"
                "Context 1 %s\n"
                "Context 2 %s" % (n1._context, n2._context))
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
            res = np.full(n1v.size, 4, dtype="uint8")
            res[((n1v == 0) & (n2v == 0))] = 0
            res[((n1v == 1) & (n2v == 1))] = 1
            res[((n1v == 1) & (n2v == 0))] = 2
            res[((n1v == 0) & (n2v == 1))] = 3
            res[((n1v == 255) & (n2v == 255))] = 255
            res.resize(n1._vegetation[vi].shape)
            self._delta[vi] = ma.masked_equal(res, 255)

        self._n1 = n1

    def write(self, folder):
        """ Writes the difference grids to grid files.

        The differences have are coded using these values:
        - 0: "not present in both models"
        - 1: "present in both models"
        - 2: "only in model 1"
        - 3: "only in model 2"
        - 4: "nodata in one model"

        Parameters
        ==========

        folder: path
            Path to which the output files will be written.
        """

        if not os.path.exists(folder):
            os.makedirs(folder)

        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            dtype="uint8",
            nodata=255,
            compress="DEFLATE"
        )

        for vi in self._delta:
            path = folder + '/D%s.tif' % vi
            with rasterio.open(path, 'w', **params) as dst:
                dst.write(self._delta[vi], 1)
                # self._files_written[vi] = os.path.normpath(path)

    def plot(self, key, ax = None):
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.colors import Normalize

        except (ImportError, RuntimeError):  # pragma: no cover
            msg = "Could not import matplotlib\n"
            msg += "matplotlib required for plotting functions"
            raise ImportError(msg)

        if ax is None:
            fig, ax = plt.subplots()
        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)

        im = plt.imshow(self._delta[key], extent=mpl_extent,
                        norm=Normalize(0, max(self._values)))
        ax.set_title("{} ({})".format(self._n1._vegcode2name(key), key))

        labels = self._labels
        values = self._values

        colors = [im.cmap(value/(len(values) - 1)) for value in values]
        patches = [mpatches.Patch(color=colors[i],
                                  label=labels[i]) for i in values]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2,
                   borderaxespad=0.)

        return ax

    @property
    def table(self):
        td = list()
        for i in self._delta:
            vi = pd.Series(self._delta[i].flatten())
            rec = vi.value_counts()
            for a in rec.index:
                td.append((i, self._labels[int(a)], rec[a]* self._context.cell_area))
        df = pd.DataFrame(td, columns = ['vegetation', 'presence', 'area'])


        return df


def conductivity2minerality(conductivity, minerality):
    # converts a grid with conductivity to a grid of minerality
    # in the same grid format
    with rasterio.open(conductivity) as src:
        band = src.read(1)
        band = np.where(band>500,1,0)
        profile = src.profile
        band = band.astype(profile["dtype"])

    with rasterio.open(minerality, 'w', **profile) as dst:
        dst.write(band, 1)