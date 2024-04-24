import warnings
import inspect
import json
from packaging.version import parse
from urllib.request import urlopen, URLError
import logging
import os.path
import numbers
import yaml
import datetime
import sys

import numpy as np
import numpy.ma as ma
import pandas as pd
import rasterio
import rasterstats
from tqdm import tqdm

from niche_vlaanderen.vegetation import Vegetation, VegSuitable
from niche_vlaanderen.acidity import Acidity
from niche_vlaanderen.nutrient_level import NutrientLevel
from niche_vlaanderen.spatial_context import SpatialContext
from niche_vlaanderen.version import __version__
from niche_vlaanderen.flooding import Flooding
from niche_vlaanderen.exception import NicheException
from niche_vlaanderen.codetables import package_resource


_allowed_input = {
    "soil_code",
    "mlw",
    "msw",
    "mhw",
    "seepage",
    "inundation_acidity",
    "inundation_nutrient",
    "nitrogen_atmospheric",
    "nitrogen_animal",
    "nitrogen_fertilizer",
    "management",
    "minerality",
    "rainwater",
    "inundation_vegetation",
    "management_vegetation",
    "acidity",
    "nutrient_level",
}

_minimal_input = {"mlw", "mhw", "soil_code"}

_input_nutrient_level = {
    "msw",
    "soil_code",
    "nitrogen_atmospheric",
    "nitrogen_fertilizer",
    "nitrogen_animal",
    "management",
    "inundation_nutrient",
}

_input_acidity = {
    "soil_code",
    "mlw",
    "minerality",
    "seepage",
    "rainwater",
    "inundation_acidity",
}

_abiotic_keys = {"nutrient_level", "acidity"}

_code_tables = {
    "ct_acidity",
    "ct_soil_mlw_class",
    "ct_soil_codes",
    "lnk_acidity",
    "ct_seepage",
    "ct_vegetation",
    "ct_management",
    "ct_nutrient_level",
    "ct_mineralisation",
}

_code_tables_fp = {"duration", "frequency", "lnk_potential", "potential"}

logging.basicConfig()
logger = logging.getLogger(__name__)


class Niche(object):
    """Creates a new Niche object

    A niche object can be used to predict vegetation types according to the
    NICHE Vlaanderen model.

    The default codetables are used unless other tables are supplied to the
    constructor.

    Parameters:
        ct_* lnk_*: path
          Optionally, paths to codetables can be provided. These will override
          the standard codetables used by Niche.

    """

    def __init__(
        self,
        ct_acidity=None,
        ct_soil_mlw_class=None,
        ct_soil_codes=None,
        lnk_acidity=None,
        ct_seepage=None,
        ct_vegetation=None,
        ct_management=None,
        ct_nutrient_level=None,
        ct_mineralisation=None,
    ):
        self._inputfiles = dict()
        self._inputvalues = dict()
        self._inputarray = dict()
        self._abiotic = dict()
        self._code_tables = dict()
        self._vegetation = dict()
        self._vegetation_detail = dict()
        self._deviation = dict()
        self._options = dict()
        self._options["name"] = ""
        self._options["strict_checks"] = True
        self._files_written = dict()
        self._log = logging.getLogger("niche_vlaanderen")
        self._context = None
        self.occurrence = None

        self._latest_version = self._check_latest_version()

        for k in _code_tables:
            ct = locals()[k]
            if ct is not None:
                self._set_ct(k, ct)

    @property
    def name(self):
        return self._options["name"]

    @name.setter
    def name(self, name):
        self._options["name"] = str(name)

    def __repr__(self):
        s = "# Niche Vlaanderen version: {}\n".format(__version__)
        s += self._latest_version + "\n"
        s += "# Run at: {}\n\n".format(datetime.datetime.now())
        # Also add some versions of the major packages we use - easy for
        # debugging
        s += "package_versions:\n"
        s += "  pandas: {}\n".format(pd.__version__)
        s += "  numpy: {}\n".format(np.__version__)
        s += "  rasterio: {}\n".format(rasterio.__version__)
        s += "  gdal: {}\n".format(rasterio.__gdal_version__)
        s += "  python: '{}'\n".format(sys.version)

        s += "\n"
        s += "model_options:\n"
        options = yaml.dump(self._options, default_flow_style=False)
        s += indent(options, "  ")

        if len(self._code_tables) > 0:
            s += "\n\n"
            s += "code_tables:\n"
            s += indent(yaml.dump(self._code_tables, default_flow_style=False), "  ")

        if self._context is not None:
            s += "\nmodel_properties:\n"
            s += "  model_extent: " + str(self._context.extent) + "\n"

        s += "\n"
        s += "input_layers:\n"
        input = yaml.dump(self._inputfiles, default_flow_style=False)
        input += (
            yaml.dump(self._inputvalues, default_flow_style=False)
            if len(self._inputvalues) > 0
            else ""
        )
        s += indent(input, "  ")

        if self.vegetation_calculated:
            s += "# Model run completed"
        else:
            s += "# No model run completed."

        if len(self._files_written) > 0:
            s += "\nfiles_written:\n"
            s += indent(yaml.dump(self._files_written, default_flow_style=False), "  ")

        return s

    def _check_latest_version(self):
        url = "https://pypi.python.org/pypi/niche_vlaanderen/json"
        try:
            response = urlopen(url, timeout=5)
            json_response = json.loads(response.read().decode("utf-8"))
            releases = json_response["releases"]
            versions = sorted(releases, key=parse, reverse=True)

            # remove alpha, beta, rc versions
            dev = ["rc", "a", "b"]
            indev = lambda a: any(devstring in a for devstring in dev)
            versions = [v for v in versions if not indev(v)]

            last = versions[0]

            if last == __version__:
                s = "# Using latest niche_vlaanderen  %s" % __version__
            else:
                s = "# Newer niche_vlaanderen  %s available" % last  # pragma: no cover
        except URLError:  # pragma: no cover
            s = "# Error determinining last upstream version"
        return s

    def _set_ct(self, key, value):
        if key not in _code_tables and key not in _code_tables_fp:
            raise NicheException("Unrecognized codetable %s" % key)

        if not os.path.isfile(value):
            raise NicheException("Cannot find file %s" % key)

        self._code_tables[key] = value

    def set_input(self, key, value):
        """Adds a raster or numeric value as input layer

        Parameters
        ----------
        key: string
            The type of grid that you want to assign (eg msw, soil_code, ...).
            Possible options are listed in
            https://inbo.github.io/niche_vlaanderen/cli.html#id1
        value: string / number
            Path to a file containing the grid. Can be a folder for
            certain grid types (eg ArcGIS rasters).
            Can also be a number: in that case a constant value is applied
            everywhere.

        """

        # check type is valid value from list
        if key not in _allowed_input:
            raise NicheException("Unrecognized type %s" % key)

        if self.vegetation_calculated:
            self._log.warning("Setting new input after model run, " "clearing results")
            self._clear_result()

        if isinstance(value, numbers.Number):
            # Remove any existing values to make sure last value is used
            self._inputfiles.pop(key, None)
            self._inputvalues[key] = value

        else:
            with rasterio.open(value, "r") as dst:
                sc_new = SpatialContext(dst)
            if self._context is None:
                self._context = sc_new
            else:
                if self._context != sc_new:
                    self._context.set_overlap(sc_new)
            # Remove any existing values to make sure last value is used
            self._inputvalues.pop(key, None)
            self._inputfiles[key] = value

    def read_config_file(self, config, overwrite_ct=False):
        """Sets the input based on an input file, without running it

        Configures a model based on a config file

        Parameters:
            overwrite_ct: bool (False)
               Allows the user to override the default codetables (after
               the class has been initialized).
        """
        with open(config, "r") as stream:
            config_loaded = yaml.safe_load(stream)

        if overwrite_ct and "code_tables" in config_loaded.keys():
            for k in config_loaded["code_tables"].keys():
                value = config_loaded["code_tables"][k]
                value = os.path.join(os.path.dirname(config), value)
                self._set_ct(k, value)

        # parse input_layers
        for k in config_loaded["input_layers"].keys():
            # adjust path to be relative to the yaml file
            value = config_loaded["input_layers"][k]
            if not isinstance(value, numbers.Number):
                value = os.path.join(os.path.dirname(config), value)
            self.set_input(k, value)

        if "model_options" in config_loaded.keys():
            if "name" in config_loaded["model_options"].keys():
                self.name = config_loaded["model_options"]["name"]
            if "strict_checks" in config_loaded["model_options"].keys():
                self._options["strict_checks"] = config_loaded["model_options"][
                    "strict_checks"
                ]
            if "overwrite_files" in config_loaded["model_options"].keys():
                self._options["overwrite_files"] = config_loaded["model_options"][
                    "overwrite_files"
                ]
            if "output_dir" in config_loaded["model_options"].keys():
                self._options["output_dir"] = config_loaded["model_options"][
                    "output_dir"
                ]

        if "flooding" in config_loaded.keys():
            self._options["flooding"] = []
            for scen_nr in config_loaded["flooding"]:
                scen = {
                    k: scen_nr[k]
                    for k in ["name", "depth", "period", "frequency", "duration"]
                }
                self._options["flooding"].append(scen)

    def run_config_file(self, config, overwrite_ct=False):
        """Runs Niche using a configuration file

        This will configure the model, run and output as specified.

        Parameters:
            config: string
               path to a config file
            overwrite_ct: boolean (False)
               overwrite codetables using the values specified in
               the configuration file.
        """

        self.read_config_file(config, overwrite_ct=overwrite_ct)

        # Set input values
        with open(config, "r") as stream:
            config_loaded = yaml.safe_load(stream)

        # Run + write according to model options
        options = {
            k: config_loaded["model_options"][k]
            for k in inspect.getfullargspec(self.run).args
            if k in config_loaded["model_options"].keys()
        }
        self.run(**options)

        overwrite = False

        if "overwrite_files" in self._options and self._options["overwrite_files"]:
            overwrite = True

        if "flooding" in self._options:
            for scen in self._options["flooding"]:
                ct_nl = dict()

                keys = set(Flooding.__init__.__code__.co_varnames) & set(
                    self._code_tables
                )

                for k in keys:
                    ct_nl[k] = self._code_tables[k]

                fp = Flooding(name=scen["name"], **ct_nl)

                depth_file = os.path.join(os.path.dirname(config), scen["depth"])

                fp.calculate(
                    depth_file=depth_file,
                    period=scen["period"],
                    frequency=scen["frequency"],
                    duration=scen["duration"],
                )
                self.fp = fp.combine(self)
                if "output_dir" in self._options:
                    self.fp.write(self._options["output_dir"], overwrite)
                    self._files_written.update(self.fp._files_written)

        if "output_dir" in self._options:
            output_dir = self._options["output_dir"]
            self.write(output_dir, overwrite)

    def _check_all_lower(self, input_array, a, b):
        # We ignore comparison problems with np.nan (nodata)
        warnings.simplefilter(action="ignore", category=RuntimeWarning)
        higher = (
            (input_array[a] > input_array[b])
            & (input_array[a] != -99)
            & (input_array[b] != -99)
        )
        warnings.simplefilter("default")

        if np.any(higher):
            # find out which cells have invalid values
            bad_points = np.where(higher)
            # convert these cells into the projection system
            bad_points = self._context.transform * bad_points

            print("Warning: Not all {} values are lower than {}".format(a, b))
            print("coordinates with invalid values are:")
            print(pd.DataFrame(list(bad_points)))

            if self._options["strict_checks"]:
                raise NicheException(
                    "Error: not all {} values are lower than {}".format(a, b)
                )

    def _check_input_files(self, full_model):
        """basic input checks (valid files etc)"""

        # Load every input_file in the input_array
        inputarray = dict()
        for f in self._inputfiles:
            dst = rasterio.open(self._inputfiles[f], "r")

            nodata = dst.nodatavals[0]

            window = self._context.get_read_window(SpatialContext(dst))
            band = dst.read(1, window=window)

            # if we have unsigned integers - switch to signed otherwise
            # no data (-99) will fail.

            if band.dtype.kind == "u":
                band = band.astype(int)

            if f in (
                "nitrogen_animal",
                "nitrogen_fertilizer",
                "nitrogen_atmospheric",
                "mhw",
                "mlw",
                "msw",
            ):
                band = band.astype("float32")

            # create a mask for no-data values, taking into account data-types
            if band.dtype == "float32" and nodata is not None:
                band[np.isclose(nodata, band)] = np.nan
            else:
                band[band == nodata] = -99
            
            # convert old soil codes to new soil codes
            if f == "soil_code" and np.all((band >= 10000)|(band==-99)|np.isnan(band)):
                band[band>=10000] = np.round(band[band>=10000] / 10000)
            
            if f == "soil_code" and band.dtype == "float32":
                band[np.isnan(band)] = -99
                band = band.astype(int)

            inputarray[f] = band

        # Load in all constant inputvalues
        for f in self._inputvalues:
            shape = (int(self._context.height), int(self._context.width))
            inputarray[f] = np.full(shape, self._inputvalues[f])

        # check if valid values are used in inputarrays
        # check for valid datatypes - values will be checked in the low-level
        # api (eg soil_code present in codetable)

        self._check_all_lower(inputarray, "mhw", "mlw")

        if "msw" in inputarray.keys():
            self._check_all_lower(inputarray, "msw", "mlw")
            self._check_all_lower(inputarray, "mhw", "msw")

        if full_model and "nutrient_level" not in inputarray.keys():
            with np.errstate(invalid="ignore"):  # ignore NaN comparison errors
                if np.any(
                    (inputarray["nitrogen_animal"] < 0)
                    | (inputarray["nitrogen_animal"] > 10000)
                    | (inputarray["nitrogen_fertilizer"] < 0)
                    | (inputarray["nitrogen_fertilizer"] > 10000)
                    | (inputarray["nitrogen_atmospheric"] < 0)
                    | (inputarray["nitrogen_atmospheric"] > 10000)
                ):
                    raise NicheException("Error: nitrogen values must be >0 and <10000")

        # if all is successful:
        self._inputarray = inputarray

    def run(self, full_model=True, deviation=False, strict_checks=True):
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

        strict_checks: bool
                By default running a model will fail if impossible combinations
                of MxW exist somewhere in the input files. By disabling strict
                checks models can still be run. It will still emit a warning.
                Note that this is provided to be backwards compatibility and
                it is recommended to fix the data rather than disabling this.
        """

        self._options["full_model"] = full_model
        self._options["deviation"] = deviation
        self._options["strict_checks"] = strict_checks

        if full_model:
            required_input = set(_minimal_input)

            given_input = set(self._inputfiles.keys()) | set(self._inputvalues.keys())

            if "nutrient_level" not in given_input:
                required_input |= set(_input_nutrient_level)

            if "acidity" not in given_input:
                required_input |= set(_input_acidity)

            missing_keys = required_input - given_input

            if len(missing_keys) > 0:
                print("Different keys are missing: ")
                print(missing_keys)
                raise NicheException("Error, different obliged keys are missing")

        self._check_input_files(full_model)

        if full_model:
            if "nutrient_level" not in self._inputarray:
                ct_nl = dict()

                keys = set(NutrientLevel.__init__.__code__.co_varnames) & set(
                    self._code_tables
                )

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
                    inundation=self._inputarray["inundation_nutrient"],
                )

            if "acidity" not in self._inputarray:
                ct_acidity = dict()

                keys = set(Acidity.__init__.__code__.co_varnames) & set(
                    self._code_tables
                )

                for k in keys:
                    ct_acidity[k] = self._code_tables[k]

                acidity = Acidity(**ct_acidity)
                self._abiotic["acidity"] = acidity.calculate(
                    self._inputarray["soil_code"],
                    self._inputarray["mlw"],
                    self._inputarray["inundation_acidity"],
                    self._inputarray["seepage"],
                    self._inputarray["minerality"],
                    self._inputarray["rainwater"],
                )

        ct_veg = dict()

        keys = set(Vegetation.__init__.__code__.co_varnames) & set(self._code_tables)

        for k in keys:
            ct_veg[k] = self._code_tables[k]

        vegetation = Vegetation(**ct_veg)
        if "inundation_vegetation" not in self._inputarray:
            self._inputarray["inundation_vegetation"] = None

        if "management_vegetation" not in self._inputarray:
            self._inputarray["management_vegetation"] = None

        veg_arguments = dict(
            soil_code=self._inputarray["soil_code"],
            mhw=self._inputarray["mhw"],
            mlw=self._inputarray["mlw"],
        )

        if full_model:
            veg_arguments.update(
                inundation=self._inputarray["inundation_vegetation"],
                management=self._inputarray["management_vegetation"],
            )

            if "nutrient_level" in self._inputarray:
                veg_arguments["nutrient_level"] = self._inputarray["nutrient_level"]
            else:
                veg_arguments["nutrient_level"] = self._abiotic["nutrient_level"]

            if "acidity" in self._inputarray:
                veg_arguments["acidity"] = self._inputarray["acidity"]
            else:
                veg_arguments["acidity"] = self._abiotic["acidity"]

        (
            self._vegetation,
            self.occurrence,
            self._vegetation_detail,
        ) = vegetation.calculate(full_model=full_model, **veg_arguments)

        if deviation:
            self._deviation = vegetation.calculate_deviation(
                self._inputarray["soil_code"],
                self._inputarray["mhw"],
                self._inputarray["mlw"],
            )

    def write(self, folder, overwrite_files=False, detailed_files=False):
        """Saves the model results to a folder

        Saves the model results to a folder. Files will be written as geotiff.
        Vegetation files have names V1 ... V28
        Abiotic files are exported as well (nutrient_level.tif and
        acidity.tif) if they were not input files.

        Parameters
        ----------

        folder: string
            Output folder to which files will be written. Parent directory must
            already exist.

        overwrite_files: bool
            Overwrite files when saving.
            Note writing will fail if any of the files to be written already
            exists.

        detailed_files : bool
            Save detailed information on factor affecting vegetation possibility

        """

        if not self.vegetation_calculated:
            raise NicheException("A valid run must be done before writing the output.")

        folder = str(folder)
        self._options["output_dir"] = folder

        if not os.path.exists(folder):
            os.makedirs(folder)

        params = dict(
            driver="GTiff",
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            dtype="uint8",
            nodata=255,
            compress="DEFLATE",
        )

        prefix = ""
        if self.name != "":
            prefix = self.name + "_"

        files = {
            "summary": folder + "/" + prefix + "summary.csv",
            "log": "{}/{}log.txt".format(folder, prefix),
        }

        for vi in self._vegetation:
            path = "{}/{}V{:02d}.tif".format(folder, prefix, vi)
            files[vi] = path

        for vi in self._abiotic:
            path = "{}/{}{}.tif".format(folder, prefix, vi)
            files[vi] = path

        for i in self._deviation:
            path = "{}/{}{}.tif".format(folder, prefix, i)
            files[i] = path

        if detailed_files:
            for vi in self._vegetation_detail:
                path = "{}/{}V{:02d}_detail.tif".format(folder, prefix, vi)
                files["%02d_detail" % vi] = path

        for key in files:
            if os.path.exists(files[key]):
                if overwrite_files:
                    self._log.info("Warning: file {} already exists".format(files[key]))
                else:
                    raise NicheException("File {} already exists".format(files[key]))

        # write a summary file containing the table of the model
        self.table.to_csv(files["summary"], index=False)

        for vi in self._vegetation:
            with rasterio.open(files[vi], "w", **params) as dst:
                dst.write(self._vegetation[vi], 1)
                self._files_written[vi] = os.path.normpath(files[vi])

        # also save the abiotic grids
        for vi in self._abiotic:
            with rasterio.open(files[vi], "w", **params) as dst:
                dst.write(self._abiotic[vi], 1)
                self._files_written[vi] = os.path.normpath(files[vi])

        if detailed_files:
            # write legend file
            legend = VegSuitable.legend()
            pd.DataFrame({"legend": pd.Series(legend)}).to_csv(folder + "/" + prefix + "legend_detail.csv")
            # and the actual grids
            for vi in self._vegetation_detail:
                filename = files["%02d_detail" % vi]
                with rasterio.open(filename, "w", **params) as dst:
                    dst.write(self._vegetation_detail[vi], 1)
                    self._files_written["%02d_detail" % vi] = os.path.normpath(filename)

        # deviation
        params.update(dtype="float64", nodata=-99999)

        for i in self._deviation:
            with rasterio.open(files[i], "w", **params) as dst:
                band = self._deviation[i]
                band[band == np.nan] = -99999
                dst.write(band, 1)
                self._files_written[i] = os.path.normpath(files[i])

        with open(files["log"], "w") as f:
            f.write(self.__repr__())

    def plot(self, key, ax=None, fixed_scale=True):
        """Plots the result or input of a Niche object

        Creates a plot of an input layer of a Niche object or of the result
        of a Niche object.

        Note that depending on your matplotlib environment you may still have
        to call the matplotlib show method to actually show the plot::

          >>> myniche.plot(11)
          >>> import matplotlib.pyplot as plt
          >>> plt.show()

        Parameters
        ==========
        key: veg_code (1..28) or input_code
          key of the vegetation type that should be plotted, eg myniche.plot(7)
          or key of the input layer you want to plot eg myniche("mhw").
          If deviation was calculated with the model, this can also be plotted,
          by using `input_code_veg_code` eg `mhw_14`

        ax: `matplotlib.axes.Axes`_
          optional axis parameter. Can be specified when you want to plot
          different plots in one layout

        fixed_scale: boolean (default: True)
           Use a fixed scale

        Returns
        =======
        ax: `matplotlib.axes.Axes`_
          Can be used to update the plot (eg change the
          title).
        """
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

        # Inform user that data is not available to plot
        # (key is present, but value is None)
        if key not in self._inputfiles and key in self._inputarray:
            if not self._inputarray[key]:
                raise KeyError(f"{key} data is not available to plot.")

        if key in self._inputfiles and key not in self._inputarray:
            # if set_input has been done, but no model run yet
            # in this case we will open the file and fetch the data
            with rasterio.open(self._inputfiles[key], "r") as dst:
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
            norm = Normalize(0, 1)
        if key in self._deviation:
            v = self._deviation[key]
            title = key
            if fixed_scale:
                norm = Normalize(-50, 50)

        if key in {"mhw", "mlw", "msw"} and fixed_scale:
            norm = Normalize(200, 0)

        if v is None:
            raise NicheException("Invalid key specified")

        if ax is None:
            fig, ax = plt.subplots()

        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)

        im = plt.imshow(v, extent=mpl_extent, norm=norm, interpolation="none")

        if self.name != "":
            title = self.name + " " + title

        ax.set_title(title)

        if key in self._vegetation:
            labels = ["not present", "present"]
            values = [0, 1]

            colors = [im.cmap(value / (len(values) - 1)) for value in values]
            patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in values]
            plt.legend(
                handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0
            )
        else:
            plt.colorbar()

        return ax

    def plot_detail(self, key, limit_legend=True, cmap="tab20"):
        """Detailed plot for a vegetation type
        key: veg_code (1..28)
          key of the vegetation type that should be plotted
        limit_legend: boolean
            limits the legend to the types present in the figure
        cmap: colormap
            colormap to use for the maps. Note that 9 combinations of
            presence/absence are possible, so keep this in mind if changing
            from the default value.
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            import matplotlib

        except (ImportError, RuntimeError):  # pragma: no cover
            msg = "Could not import matplotlib\n"
            msg += "matplotlib required for plotting functions"
            raise ImportError(msg)

        if key not in self._vegetation.keys():
            raise NicheException("invalid key for plot, must be a number of a vegetation type")

        title = "{} ({})".format(self._vegcode2name(key), key)

        v = self._vegetation_detail[key]
        v = ma.masked_equal(v, 255)
        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)

        fig, ax = plt.subplots()

        legend = VegSuitable.legend()
        legend_keys = np.array(list(legend.keys()))

        # convert vegetation matrix to legend item matrix
        v_un = np.digitize(v, legend_keys, right=True)
        v_un = ma.masked_equal(v_un, len(legend))

        plt.imshow(
            v_un,
            extent=mpl_extent,
            cmap=cmap,
            interpolation="None",
            vmin=0,
            vmax=len(VegSuitable.possible()) + 1,
        )

        if limit_legend:
            present = ma.unique(v_un[~v_un.mask])

            patches = [
                mpatches.Patch(color=matplotlib.colormaps[cmap](i), label=legend[legend_keys[i]])
                for i in present
            ]
        else:
            patches = [
                mpatches.Patch(color=matplotlib.colormaps[cmap](i), label=legend[j])
                for i, j in enumerate(legend)
            ]

        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

        if self.name != "":
            title = self.name + " " + title

        ax.set_title(title)

        return ax

    @property
    def table(self):
        """Dataframe containing the potential area (ha) per vegetation type"""
        return self._table()

    def _table(self, detail=False):
        """Dataframe containing the potential area (ha) per vegetation type

        detail: boolean
            add info why vegetation is present, rather than just present/not present
        """
        if not self.vegetation_calculated:
            raise NicheException(
                "Error: You must run niche prior to requesting the " "result table"
            )

        td = list()
        if detail is False:
            presence = dict({0: "not present", 1: "present", 255: "no data"})

            for i in self._vegetation:
                vi = pd.Series(self._vegetation[i].flatten())
                rec = vi.value_counts() * self._context.cell_area / 10000
                for a in rec.index:
                    td.append((i, presence[a], rec[a]))
        else:
            legend = VegSuitable.legend()
            legend[255] = "no data"
            for i in self._vegetation_detail:
                vi = pd.Series(self._vegetation_detail[i].flatten())
                rec = vi.value_counts() * self._context.cell_area / 10000
                for a in rec.index:
                    td.append((i, legend[a], rec[a]))

        df = pd.DataFrame(td, columns=["vegetation", "presence", "area_ha"])

        return df

    def zonal_stats(
        self, vectors, outside=True, attribute=None, vegetation_types=None, upscale=1
    ):
        """Calculates zonal statistics using vectors

        Parameters
        ==========
        vectors: path to a vector source or geo-like python objects
            you can specify a path to a vector file eg "../test.shp", or pass
            geo objects from other python functions.

            Note that the vector should be in the same coordinate system as the
            raster.
        outside: bool (default: True)
           report values outside shapes as well. The area which is not covered
           by any shapefile will get shape_id -1.
        attribute: string(default None):
            attribute of the vector source that will be exported along in the
            table.
        vegetation_types: List | None
            optional list of vegetation types (as integer number) for which the
            statistics must be calculated. Calculation will happen for all
            niche vegetation types by default.
        upscale : int
            upscaling factor: decrease the cell size by this factor to increase
            the resolution

        Returns
        =======
        table: pandas.DataFrame
        """
        td = dict()

        # Ignore the warnings from rasterstats - code must be adjusted
        # in that package - not in our code.
        #warnings.simplefilter(action="ignore", category=FutureWarning)
        #warnings.simplefilter(action="ignore", category=DeprecationWarning)

        presence = dict({0: "not present", 1: "present", 255: "no data"})

        if vegetation_types is None:
            vegetation_types = self._vegetation.keys()

        if len(vegetation_types) == 0:
            raise NicheException("Can not calculate zonal statistics for "
                                 "empty vegetation list")

        logger.debug(f"vegetation_types: {vegetation_types}")
        logger.debug(f"upscaling to {upscale}")

        for i in tqdm(vegetation_types):
            # Note we use -99 as nodata value to make sure the true nodata
            # value (255) is part of the result table.

            if upscale == 1:
                raster = self._vegetation[i]
                affine = self._context.transform
            else:
                # based on
                # https://rasterio.readthedocs.io/en/latest/topics/resampling.html
                raster = (
                    self._vegetation[i].repeat(upscale, axis=0).repeat(upscale, axis=1)
                )
                affine = self._context.transform * self._context.transform.scale(
                    self._context.width / raster.shape[1],
                    self._context.height / raster.shape[0],
                )

            td[i] = rasterstats.zonal_stats(
                vectors=vectors,
                raster=raster,
                affine=affine,
                categorical=True,
                nodata=Vegetation.nodata_veg,
                geojson_out=attribute is not None,
            )
        warnings.simplefilter("default")

        ti = []
        attribute_list = []

        for vi in td:
            for shape_i, rec in enumerate(td[vi]):
                if attribute is not None:
                    rec = rec["properties"]
                for a in presence:
                    pixels = rec.get(a) if rec.get(a) is not None else 0
                    ti.append(
                        (
                            int(vi),
                            shape_i,
                            presence[a],
                            pixels * self._context.cell_area / 10000 / (upscale ** 2),
                        )
                    )
                    if attribute is not None:
                        attribute_list.append(rec[attribute])

        df = pd.DataFrame(ti, columns=["vegetation", "shape_id", "presence", "area_ha"])

        if outside:
            # calculate area outside polygons
            a = pd.concat(
                [
                    self.table.groupby(by=["vegetation", "presence"])["area_ha"].sum(),
                    df.groupby(by=["vegetation", "presence"])["area_ha"].sum(),
                ],
                axis=1,
            )
            a = a.reset_index().fillna(0)
            a.columns = ["vegetation", "presence", "all", "inshape"]
            a["area_ha"] = a["all"] - a["inshape"]
            a["shape_id"] = -1
            a = a[["vegetation", "shape_id", "presence", "area_ha"]]
            df = pd.concat([df, a])
            attribute_list.extend(a["shape_id"])

        if attribute is not None:
            df[attribute] = attribute_list

        return df

    def _vegcode2name(self, vegcode):
        """Converts a vegetation code to a name

        Uses ct_vegetation columns veg_code and veg_type"""

        if not hasattr(self, "_vegcode2namedict"):
            if "ct_vegetation" in self._code_tables:
                ct_vegetation = self._code_tables["ct_vegetation"]
            else:
                ct_vegetation = package_resource(
                    ["system_tables"], "niche_vegetation.csv")

            ct_vegetation = pd.read_csv(ct_vegetation)
            subtable = ct_vegetation[["veg_code", "veg_type"]]
            veg_dict = subtable.set_index("veg_code").to_dict()["veg_type"]
            self._vegcode2namedict = veg_dict
        return self._vegcode2namedict[vegcode]

    @property
    def vegetation_calculated(self):
        return len(self._vegetation) > 0

    def _clear_result(self):
        """Clears calculated vegetation"""
        self._vegetation.clear()
        self._deviation.clear()


def indent(s, pre):
    return pre + s.replace("\n", "\n" + pre)


class NicheDelta(object):
    """Class containing the difference between two niche runs

    The difference can be visualized using the plot method. It is also
    possible to derive a table with the area's according to each group.

    See the tutorial at: `Comparing Niche classes`_
    """

    _values = [0, 1, 2, 3, 4]
    _labels = [
        "not present in both models",
        "present in both models",
        "only in model 1",
        "only in model 2",
        "nodata in one model",
    ]
    name = ""

    def __init__(self, n1, n2):
        self._delta = dict()
        self._log = logging.getLogger("niche_vlaanderen")

        if n1._context is None or n2._context is None:
            raise NicheException(
                "No extent in Niche object. Please run both models prior to "
                "calculating a delta."
            )

        if n1._context != n2._context:
            raise NicheException(
                "Spatial contexts differ, can not make a delta\n"
                "Context 1 %s\n"
                "Context 2 %s" % (n1._context, n2._context)
            )
        self._context = n1._context

        if len(n1._vegetation) == 0 or len(n2._vegetation) == 0:
            raise NicheException(
                "No vegetation in Niche object. Please run both models prior "
                "to calculating a delta."
            )

        # the error below should not occur as we check the context, but
        # better safe than sorry
        if n1._vegetation[1].size != n2._vegetation[1].size:  # pragma: no cover
            raise NicheException("Arrays have different size.")

        if len(n1._vegetation) != len(n2._vegetation):
            raise NicheException("Niche vegetation objects have different length.")

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

    def write(self, folder, overwrite_files=False):
        """Writes the difference grids to grid files.

        The differences are coded using these values:

         * 0: "not present in both models"
         * 1: "present in both models"
         * 2: "only in model 1"
         * 3: "only in model 2"
         * 4: "nodata in one model"

        Parameters
        ==========

        folder: path
            Path to which the output files will be written.
        overwrite_files: bool
            Whether files should be overwritten on save.
        """

        if not os.path.exists(folder):
            os.makedirs(folder)

        params = dict(
            driver="GTiff",
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            dtype="uint8",
            nodata=255,
            compress="DEFLATE",
        )

        prefix = ""
        if self.name != "":
            prefix = self.name + "_"

        files = {
            "summary": "{}/{}delta_summary.csv".format(folder, prefix),
            "legend": "{}/{}legend_delta.csv".format(folder, prefix),
        }

        for vi in self._delta:
            files[vi] = "{}/{}D{}.tif".format(folder, prefix, vi)

        for key in files:
            if os.path.exists(files[key]):
                if overwrite_files:
                    self._log.warning(
                        "Warning: file {} already exists".format(files[key])
                    )
                else:
                    raise NicheException("File {} already exists".format(files[key]))

        for vi in self._delta:
            with rasterio.open(files[vi], "w", **params) as dst:
                dst.write(self._delta[vi], 1)

        # Also the resulting table is written
        self.table.to_csv(files["summary"], index=False)

        # And a small file containing the legend
        legend = pd.DataFrame(dict(code=self._values, labels=self._labels))
        legend.to_csv(files["legend"], index=False)

    def plot(self, key, ax=None):
        """
        Plots the difference between two classes

        Parameters
        ==========
        key: number
            The vegetation code (1-28)

        """
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

        im = plt.imshow(
            self._delta[key],
            extent=mpl_extent,
            norm=Normalize(0, max(self._values)),
            interpolation="none",
        )

        if self.name != "":
            title = "{} ({}-{})".format(self.name, self._n1._vegcode2name(key), key)
        else:
            title = "{} ({})".format(self._n1._vegcode2name(key), key)

        ax.set_title(title)

        labels = self._labels
        values = self._values

        colors = [im.cmap(value / (len(values) - 1)) for value in values]
        patches = [mpatches.Patch(color=colors[i], label=labels[i]) for i in values]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.0)

        return ax

    @property
    def table(self):
        """Return a summarized dataframe for a NicheDelta object

        Returns
        =======
        df: `pandas.DataFrame`_
        """
        td = list()
        for i in self._delta:
            vi = pd.Series(self._delta[i].flatten())
            rec = vi.value_counts()
            for a in rec.index:
                td.append(
                    (i, self._labels[int(a)], rec[a] * self._context.cell_area / 10000)
                )
        df = pd.DataFrame(td, columns=["vegetation", "presence", "area_ha"])

        return df


def conductivity2minerality(conductivity, minerality):
    """Convert a grid with conductivity to a grid of minerality

    Helper function that converts a grid with conductivity values
    to a grid of minerality values (where conductivity > 500).

    Supplied for backwards compatibility with the original niche vlaanderen
    model.

    Parameters
    ==========
    conductivity: filename
      Original grid with conductivity values.
    minerality: filename
      New grid where minerality values are stored. This will be a geotiff, so
      extension .tif is recommended.
    """

    # we will ignore future warnings from rasterio
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)

        with rasterio.open(conductivity, "r") as src:
            band = src.read(1)
            band = np.where(band > 500, 1, 0)
            profile = src.profile
            profile["driver"] = "GTiff"
            profile["compress"] = "DEFLATE"
            band = band.astype(profile["dtype"])

        with rasterio.open(minerality, "w", **profile) as dst:
            dst.write(band, 1)
