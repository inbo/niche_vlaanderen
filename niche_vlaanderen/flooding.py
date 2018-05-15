from __future__ import division

import logging
import rasterio
import os
from pkg_resources import resource_filename
import copy
from collections import OrderedDict

import pandas as pd
import numpy as np
import numpy.ma as ma

from .spatial_context import SpatialContext
from .codetables import validate_tables_floodplains, check_codes_used


class FloodingException(Exception):
    """"""


class Flooding(object):
    """
    Predict the vegetation response to (frequent) flooding

    A Floodplain object can be used to predict the response of vegetation to
    (frequent) flooding.

    The code tables used can be overwritten when initializing the object.
    Optionally also a name can be given which is used in plots and output
    files.

    """
    def __init__(self, depths=None, duration=None, frequency=None,
                 lnk_potential=None, potential=None, name=""):
        self._ct = dict()
        self._veg = dict()
        self._log = logging.getLogger("niche_vlaanderen")

        for i in ["depths", "duration", "frequency", "lnk_potential",
                  "potential"]:
            if locals()[i] is None:
                ct = resource_filename(
                        "niche_vlaanderen",
                        "system_tables/floodplains/"+i+".csv")
            else:
                ct = locals()[i]
            self._ct[i] = pd.read_csv(ct)
        self.name = name

        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])

        validate_tables_floodplains(inner=inner, **self._ct)

        # Set to true when the model is a combined niche - floodplains model
        self._combined = False

    @property
    def vegetation_calculated(self):
        return len(self._veg) > 0

    @property
    def table(self):
        """Dataframe containing the potential area (ha) per vegetation type
        """
        if not self.vegetation_calculated:
            raise FloodingException(
                "Error: You must run niche prior to requesting the "
                "result table")

        td = list()

        labels = dict(self._ct["potential"].set_index("code")["description"])

        if not self._combined:
            del labels[-1]

        labels[-99] = "no data"

        for i in self._veg:
            vi = pd.Series(self._veg[i].flatten())
            rec = vi.value_counts() * self._context.cell_area / 10000
            for a in rec.index:
                td.append((i, a, labels[a], rec[a]))

        df = pd.DataFrame(td, columns=['vegetation', 'presence_code',
                                       'presence', 'area_ha'])

        return df

    def _calculate(self, depth, frequency, duration, period):
        """
        Low level calculation of a floodplains object.
        Uses a numpy array for depth rather than a grid file (in calculate)
        """
        orig_shape = depth.shape
        depth = depth.flatten()
        nodata = (depth == -99)

        check_codes_used("depth", depth,
                         self._ct["depths"]["code"])
        check_codes_used("frequency", frequency,
                         self._ct["frequency"]["code"])
        check_codes_used("duration", duration,
                         self._ct["duration"]["code"])
        check_codes_used("period", period,
                         ["summer", "winter"])

        for veg_code, subtable_veg in \
                self._ct["lnk_potential"].groupby(["veg_code"]):
            subtable_veg = subtable_veg.reset_index()
            # by default we give code 4 (no information/flooding)
            # https://github.com/inbo/niche_vlaanderen/issues/87
            self._veg[veg_code] = np.full(depth.shape, 4, dtype="int16")
            self._veg[veg_code][nodata] = -99
            groupby_cols = ["period", "frequency", "duration"]
            for index, subtable in subtable_veg.groupby(groupby_cols):
                if (period, frequency, duration) == index:
                    subtable.reset_index()
                    for row in subtable.itertuples():
                        veg = self._veg[veg_code]
                        veg[row.depth == depth] = row.potential
                        self._veg[veg_code] = np.maximum(veg,
                                                         self._veg[veg_code])
            self._veg[veg_code] = self._veg[veg_code].reshape(orig_shape)

    def calculate(self, depth_file, frequency, period, duration):
        """ Calculate a floodplain object

        Parameters
        ==========
        depth_file: filename
           The filename containing a classified grid with inundation dephts.
           The classes used must correspond to the codes in the
           depths.csv_ code table.


        frequency: code
           The frequency with which flooding occurs, eg T2, T50. Valid values
           are given in the frequency.csv_ code table.

        period: winter|summer
            period in which the flooding occurs. Must be either "summer" or
            "winter"

        duration: code
            Period with which the flooding occurs, from duration.csv_


        """
        with rasterio.open(depth_file, "r") as dst:
            depth = dst.read(1)
            self._context = SpatialContext(dst)
            if depth.dtype.kind == 'u':
                depth = depth.astype(int)
            depth[depth == dst.nodatavals[0]] = -99
        self._calculate(depth, frequency, duration, period)

        self.options = {'frequency': frequency,
                        "duration": duration,
                        "period": period}

    def plot(self, key, ax=None):
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
            from matplotlib.colors import Normalize

        except (ImportError, RuntimeError):  # pragma: no cover
            msg = "Could not import matplotlib\n"
            msg += "matplotlib required for plotting functions"
            raise ImportError(msg)

        if key not in self._veg.keys():
            msg = "vegetation type {} not modeled".format(key)
            raise FloodingException(msg)

        if ax is None:
            fig, ax = plt.subplots()

        ((a, b), (c, d)) = self._context.extent
        mpl_extent = (a, c, d, b)

        veg = ma.masked_equal(self._veg[key], -99)

        im = plt.imshow(veg, extent=mpl_extent,
                        norm=Normalize(-1, 4))
        options = self.options.copy()
        options["duration"] = "< 14 days" \
            if self.options["duration"] == 1 else "> 14 days"
        ax.set_title("{} ({})".format(key, options))

        labels = self._ct["potential"].set_index(
            "code")["description"].to_dict(into=OrderedDict)

        colors = [im.cmap(i/(len(labels) - 1))
                  for (i, value) in enumerate(labels)]

        patches = [mpatches.Patch(color=colors[i],
                                  label=labels[code])
                   for (i, code) in enumerate(labels)
                   if code > -1 or self._combined]
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2,
                   borderaxespad=0.)

        return ax

    def write(self, folder, overwrite_files = False):
        """ Writes the floodplain grids to grid files.

         The differences are coded using the values specified in the
         potential.csv table.

         Parameters
         ==========

         folder: path
             Path to which the output files will be written.

         overwrite_files: bool
            Overwrite files when saving.
            Note writing will fail if any of the files to be written already
            exists.
         """
        if len(self._veg) == 0:
            raise FloodingException(
                "A valid run must be done before writing the output.")

        if not os.path.exists(folder):
            os.makedirs(folder)

        params = dict(
            driver='GTiff',
            height=self._context.height,
            width=self._context.width,
            crs=self._context.crs,
            transform=self._context.transform,
            count=1,
            dtype="int16",
            nodata=-99,
            compress="DEFLATE"
        )

        self._files_written = dict()
        name = ""
        if self.name != "":
            name = self.name + "-"

        files = {'summary': folder + '/' + name + "summary.csv",
                 'log': "{}/{}log.txt".format(folder, name)}

        for vi in self._veg:
            filename = "{}/{}F{:02d}-{}-P{}-{}.tif".format(
                folder,
                name,
                vi, self.options["frequency"], self.options["duration"],
                self.options["period"])
            files[vi] = filename

        for key in files:
            if os.path.exists(files[key]):
                if overwrite_files:
                    self._log.warning(
                        "Warning: file {} already exists".format(files[key]))
                else:
                    raise FloodingException(
                        "File {} already exists".format(files[key]))

        self.table.to_csv(files["summary"], index=False)

        for vi in self._veg:
            path = files[vi]
            with rasterio.open(path, 'w', **params) as dst:
                dst.write(self._veg[vi], 1)
                self._files_written[filename] = os.path.normpath(path)

    def combine(self, niche_result):
        """Combines a FloodPlain model with a Niche model

        Both models must be run prior to combining them. The niche model will
        act as a "mask" making areas where Niche predicts a vegetation type
        to be not present are set to "not combinable".

        Parameters
        ==========
        niche_result: Niche
            Niche model that must be run prior to running combine.

        Returns
        =======
        combined: Flooding
        """

        # check niche model has been run
        if not niche_result.vegetation_calculated:
            raise FloodingException(
                "Niche model must be run prior to running this module.")

        if not self.vegetation_calculated:
            raise FloodingException(
                "Floodplain model must be run prior to running this module.")

        if self._context != niche_result._context:
            raise FloodingException(
                "Niche model has a different spatial context:\n" +
                str(self._context) + str(niche_result._context)
                )

        new = copy.copy(self)
        new._veg = self._veg.copy()
        for vi in new._veg:
            nodata = ((niche_result._vegetation[vi] == 255) |
                      (new._veg[vi] == -99))
            new._veg[vi] = niche_result._vegetation[vi] * new._veg[vi]
            new._veg[vi][niche_result._vegetation[vi] == 0] = -1
            new._veg[vi][nodata] = -99

        new._combined = True

        return new
