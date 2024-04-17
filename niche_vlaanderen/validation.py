import logging
import warnings
from collections import defaultdict
from pathlib import Path

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    import geopandas as gpd

import numpy as np
import pandas as pd

from niche_vlaanderen.niche import Niche
from niche_vlaanderen.codetables import package_resource

logger = logging.getLogger(__name__)


class NicheValidationException(Exception):
    msg = "Error using Niche Overlay"


class NicheValidation(object):
    """Creates a new NicheValidation object

    Overlays a vegetation map with niche in order to
    obtain the accuracy of the model.

    Parameters:
        niche: niche_vlaanderen.Niche
            Niche object containing predicted variables types according to niche.
            The model must have run prior to the overlay
        map: Path
            Path to a file containing the vegetation map in one of the formats supported
            by fiona, eg shape.
            must contain these attributes:
            * HABx: vegetation type
            * pHABx: proportion of the vegetation type

            different vegetation types can be supplied, eg HAB1, HAB2, ...
            for every HABx variable a proportion must be given.

        mapping_file: Path | None
            optional file containing the mapping between habitat (HAB) code on the vegetation map
            and Niche vegetation types. The default mapping is a mapping of the
            BWK map (biologische waarderingskaart), and is
            part of the package at niche_vlaanderen/system_tables/hab_nich_join.csv

            If a mapping is provided by the user, it must contain a HAB and a NICHE column.
            Other columns are ignored.

        upscale: int
            optional upscale value that is used to increase the resolution of
            the niche rasters while doing the overlay.
            instead of using only the cell center, the comparison between the
            vegetation map and the niche model is done at upscale*upscale places
            in the cell. Defaults to 5.
            More details in
            https://inbo.github.io/niche_vlaanderen/validation.html

        id: str
            (optional) field to use as id for the provided map file. This id will
            be used in the overlay. If no id is supplied, the shape_index (row number)
            of the vector file will be used, starting from 0.


    """

    def __init__(self, niche, map, mapping_file=None, upscale=5, id=None):
        if type(niche) is Niche:
            self.niche = niche
        else:
            raise ValueError(
                f"pass a valid Niche object - type of niche object is {type(niche)}"
            )

        self.filename_map = map
        self.map = gpd.read_file(map)

        # the mapping columns contain are the field in the shapefile that contain a field starting with HAB{1-9}
        # (case insensitive)
        columns = self.map.columns
        vegetation_columns = columns[columns.str.upper().str.match("HAB[0-9]")]
        proportion_index = {
            veg: list(columns.str.upper()).index(f"PHAB{veg}")
            for veg in vegetation_columns.str[-1]
        }
        self.proportion_columns = {
            i: columns[proportion_index[i]] for i in proportion_index
        }

        if mapping_file is None:
            mapping_file = package_resource(["system_tables"],
                                            "hab_niche_join.csv")

        mapping = pd.read_csv(mapping_file)

        # drop any row containing niche vegetation 0
        mapping = mapping[mapping["NICHE"] != 0]

        # convert to wide format
        mapping["col"] = mapping.groupby("HAB").cumcount()
        mapping["col"] = "NICHE_C" + (mapping["col"] + 1).astype("str")

        self.mapping = mapping.pivot(
            index="HAB", columns="col", values="NICHE"
        ).reset_index()

        niche_columns = self.map.columns[self.map.columns.str.startswith("NICH_")]
        self.map = self.map.drop(columns=niche_columns)
        self.map["area_shape"] = self.map.area / 10000

        for hab_column in vegetation_columns:
            for nich_column in self.mapping.columns[
                self.mapping.columns.str.startswith("NICHE_C")
            ]:
                logger.debug(f"habi: {hab_column}; nichj: {nich_column}")
                source = self.mapping[["HAB", nich_column]].rename(
                    columns={
                        "HAB": hab_column,
                        nich_column: f"NICH_{hab_column[-1]}_{nich_column[-1]}",
                    }
                )

                self.map = pd.merge(self.map, source, on=hab_column, how="left")

        self._niche_columns = self.map.columns[self.map.columns.str.startswith("NICH")]

        self.id = id
        self.overlay(upscale=upscale)

    def __repr__(self):

        o = "# Niche Validation object\n"
        o += f"map: {self.filename_map}\n"
        o += f"niche object: {self.niche.name}"
        return o

    def overlay(self, upscale=5):
        """Overlays the map and the niche object"""

        # Remove any existing "NICH" columns

        present_vegetation_types = np.unique(self.map[self._niche_columns])

        present_vegetation_types = present_vegetation_types[
            ~np.isnan(present_vegetation_types)
        ]
        logger.debug(f"present niche types: {present_vegetation_types}")

        if len(present_vegetation_types) == 0:
            raise NicheValidationException(
                "No Niche vegetation present in validation map"
            )
        # get potential presence
        # upscale niche rasters to that before calculating statistics
        self.potential_presence = self.niche.zonal_stats(
            self.map,
            outside=False,
            vegetation_types=present_vegetation_types,
            upscale=upscale,
        )

        self.potential_presence = self.potential_presence.pivot(
            columns=["vegetation"], index=["presence", "shape_id"]
        )

        self._tables = [
            "area_pot",
            "area_nonpot",
            "area_nonpot_phab",
            "area_pot_perc_phab",
            "area_effective",
            "area_pot_perc",
            "veg_present",
        ]

        self.area_pot = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_nonpot = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_effective = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_pot_perc = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_pot_perc_phab = self.area_pot_perc * np.nan
        self.area_nonpot_phab = self.area_pot_perc * np.nan
        self.veg_present = self.area_pot_perc * 0

        # Only if actual present: (pHAB * present) / (present + not present)
        for i, row in self.map.iterrows():
            logger.debug(f"row: {row.area_shape}")
            # different mappings can exist which lead to the same vegetation
            # type. First we aggregate them in shape_veg which contains
            # the niche vegetation and the sum of its pHAB
            shape_veg = defaultdict(lambda: 0)

            for veg in self._niche_columns:
                if np.isfinite(row[veg]) and row[veg] != 0:
                    pHab = row[self.proportion_columns[veg[5]]]
                    shape_veg[int(row[veg])] += pHab

            for veg in shape_veg:
                pHab = shape_veg[veg]

                area_pot = (
                    self.potential_presence.loc["present"].loc[i].loc["area_ha"][veg]
                )

                self.area_pot.loc[i, veg] = area_pot

                area_nonpot = (
                    self.potential_presence.loc["not present"]
                    .loc[i]
                    .loc["area_ha"][veg]
                )

                self.area_nonpot.loc[i, veg] = area_nonpot
                area_effective = pHab * (area_pot + area_nonpot) / 100
                self.area_effective.loc[i, veg] = area_effective

                if (area_pot + area_nonpot) == 0:
                    warnings.warn(
                        f"No overlap between potential vegetation map and "
                        f"shape_id {i}"
                    )
                else:
                    # vegetation type is present (actual presence)
                    # used in polygon count
                    self.veg_present.loc[i, veg] = 1

        # aggregate statistics
        self.area_pot_perc = 100 * self.area_pot / (self.area_pot + self.area_nonpot)
        self.area_pot_perc_phab = np.minimum(
            100 * self.area_pot / self.area_effective, 100
        )
        self.area_nonpot_phab = np.maximum(0, self.area_effective - self.area_pot)

        # Set id column for every polygon based table
        if self.id is not None:
            for table in self._tables:
                setattr(self, table, getattr(self, table).set_index(self.map[self.id]))

        # create summary table per vegetation type

        summary = {}
        summary["area_effective"] = self.area_effective.sum()
        summary["nonpot"] = self.area_nonpot.sum()
        summary["nonpot_phab"] = self.area_nonpot_phab.sum()
        summary["pot"] = self.area_pot.sum()
        summary["polygon_count"] = self.veg_present.sum()

        summary["score"] = 100 * summary["pot"] / (summary["pot"] + summary["nonpot"])
        summary["score_phab"] = (
            100 * summary["pot"] / (summary["pot"] + summary["nonpot_phab"])
        )

        self.summary = pd.DataFrame(summary)

    def write(self, path, overwrite_files=False):
        """Write the result of the validation to a folder

        path: string | pathlib.Path
            Output folder to which files will be written. Parent directory must
            already exist.

        overwrite_files: bool
            Overwrite files when saving.
            Note writing will fail if any of the files to be written already
            exists.
        """

        path = Path(path)
        if path.exists() and not overwrite_files:
            if not path.is_dir():
                raise NicheValidationException(f"path {path} is not an empty folder")
            if any(path.iterdir()):
                raise NicheValidationException(f"path {path} exists and is not empty")
        path.mkdir(parents=True, exist_ok=True)

        # save individual tables

        for t in self._tables:
            getattr(self, t).dropna(axis=0, how="all").to_csv(path / (t + ".csv"))

        self.potential_presence.to_csv(path / "potential_presence.csv")
        self.summary.to_csv(path / "summary.csv")

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            self.joined_map().to_file(path / "validation.gpkg")

    def joined_map(self):
        """Create a geopandas dataframe with all tables joined"""
        merged = self.map
        if self.id:
            merged = merged.set_index(self.id)
        for table in self._tables:
            merged = merged.join(getattr(self, table).add_prefix(f"{table}_"))

        return merged
