import logging
from pkg_resources import resource_filename
from pathlib import Path
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    import geopandas as gpd

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

from niche_vlaanderen.niche import Niche


class NicheOverlayException(Exception):
    msg = "Error using Niche Overlay"


class NicheOverlay(object):
    """Creates a new NicheOverlay object

    Overlays the BWK (Biologische waarderingskaart) with niche in order to
    obtain the accuracy of the model.

    Parameters:
        niche: niche_vlaanderen.Niche
            Niche object containing predicted variables types according to niche.
            The model must have run prior to the overlay
        map: Path
            Path to a file containing the BWK map in one of the formats supported
            by fiona, eg shape.
            must contain these attributes:
            * HABx:
            * pHABx:

        mapping_file: Path | None
            optional file containing the mapping between habitat (HAB) code on BWK
            and Niche vegetation types. An example (and the default) mapping is part of the
            package at niche_vlaanderen/system_tables/hab_nich_join.csv
        mapping_columns: list(dict) | None
            Optional list containing the different mappings between columns.
            If not specified, the default mapping will be used.
            Custom mappings are defined as dicts:
            {
                map_key: source column in map,
                join_key: source field in mapping_file,
                join_value: to_field in mapping_file,
                new_column: resulting_column
            }
            TODO: adjust to long table
            eg:
            [{'map_key': 'HAB1',
              'join_key': 'HAB',
              'join_value': 'NICHE_C1',
              'new_column': 'NICH_1_1'}, ...]

    """

    def __init__(self, niche, map, mapping_file=None, mapping_columns=None, upscale=5):
        if type(niche) is Niche:
            self.niche = niche
        else:
            raise ValueError(
                f"pass a valid Niche object - type of niche object is {type(niche)}"
            )

        if mapping_columns is not None:
            self.mapping_columns = mapping_columns
        else:
            self.mapping_columns = {
                "HAB1": "HAB",
                "HAB2": "HAB",
                "HAB3": "HAB",
                "HAB4": "HAB",
            }
        if mapping_file is None:
            mapping_file = resource_filename(
                "niche_vlaanderen", "system_tables/hab_niche_join.csv"
            )

        mapping = pd.read_csv("niche_vlaanderen/system_tables/hab_niche_join.csv")
        mapping["col"] = mapping["HAB"].duplicated()
        mapping["col"] = "NICHE_C" + (mapping["col"] + 1).astype("str")

        self.mapping = mapping.pivot(
            index="HAB", columns="col", values="NICHE"
        ).reset_index()

        self.mapping.iloc[
            self.mapping["NICHE_C1"] == 0, self.mapping.columns.get_loc("NICHE_C1")
        ] = np.nan
        self.mapping.iloc[
            self.mapping["NICHE_C2"] == 0, self.mapping.columns.get_loc("NICHE_C2")
        ] = np.nan
        self.mapping.iloc[
            self.mapping["NICHE_C2"] == self.mapping["NICHE_C1"],
            self.mapping.columns.get_loc("NICHE_C2"),
        ] = np.nan

        if mapping_columns is not None:
            self.mapping_columns = mapping_columns
        else:
            self.mapping_columns = []
            for i in range(1, 6):
                for j in range(1, 3):
                    self.mapping_columns.append(
                        {
                            "map_key": f"HAB{i}",
                            "join_key": "HAB",
                            "join_value": f"NICHE_C{j}",
                            "new_column": f"NICH_{i}_{j}",
                        }
                    )

        # TODO: geopandas allows using a bbox or mask
        # what should be done if file does not overlap with grid?
        self.filename_map = map
        self.map = gpd.read_file(map)
        self._check_mapping_columns()

        # Use mapping table to link vegetation types

        niche_columns = self.map.columns[self.map.columns.str.startswith("NICH_")]
        self.map = self.map.drop(columns=niche_columns)
        self.map["area_shape"] = self.map.area / 10000
        # add mapping columns to source
        for t in self.mapping_columns:
            source = self.mapping[[t["join_key"], t["join_value"]]].rename(
                columns={t["join_value"]: t["new_column"], t["join_key"]: t["map_key"]}
            )
            self.map = pd.merge(self.map, source, on=t["map_key"], how="left")
        self._niche_columns = self.map.columns[self.map.columns.str.startswith("NICH")]

        self.overlay(upscale=upscale)

    def __repr__(self):

        o = "# Niche overlay object\n"
        o += f"map: {self.filename_map}\n"
        o += f"niche object: {self.niche.name}"
        return o

    def _check_mapping_columns(self):
        """Checks whether the mapping columns are present in the dataset"""
        for item in self.mapping_columns:
            if item["map_key"] not in self.map.columns:
                raise (
                    NicheOverlayException(
                        f"expected column {item['map_key']} not found in shape file"
                    )
                )
            if f'p{item["map_key"]}' not in self.map.columns:
                raise (
                    NicheOverlayException(
                        f"expected column p{item['map_key']} not found in shape file"
                    )
                )
        pass

    def overlay(self, upscale=4):
        """Overlays the map and the niche object"""

        # Remove any existing "NICH" columns

        present_vegetation_types = np.unique(self.map[self._niche_columns])

        present_vegetation_types = present_vegetation_types[
            ~np.isnan(present_vegetation_types)
        ]

        logger.debug(f"present niche types: {present_vegetation_types}")
        # get potential presence
        # TODO: add parameter cellsize to zonal statistics: eg 0.5
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
            "area_nonpot_optimistic",
            "area_pot_perc_optimistic",
            "area_effective",
            "area_pot_perc",
            "veg_present",
        ]

        self.area_pot = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_nonpot = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_effective = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_pot_perc = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        self.area_pot_perc_optimistic = self.area_pot_perc * np.nan
        self.area_nonpot_optimistic = self.area_pot_perc * np.nan

        self.veg_present = self.area_pot_perc * 0

        # Only if actual present: (pHAB * present) / (present + not present)
        for i, row in self.map.iterrows():
            for veg in self._niche_columns:
                if np.isfinite(row[veg]) and row[veg] != 0:
                    logger.debug(f"row: {row.area_shape}")
                    area_pot = (
                        self.potential_presence.loc["present"]
                        .loc[i]
                        .loc["area_ha"][row[veg]]
                    )
                    self.area_pot[row[veg]].loc[i] = area_pot

                    area_nonpot = (
                        self.potential_presence.loc["not present"]
                        .loc[i]
                        .loc["area_ha"][row[veg]]
                    )
                    self.area_nonpot[row[veg]].loc[i] = area_nonpot

                    pHab = row["pHAB" + veg[5]]  # pHAB1 --> pHAB5
                    # TODO: in ha ?
                    area_effective = pHab * row.area_shape / 100
                    # area of the shape
                    self.area_effective[row[veg]].loc[i] = area_effective

                    if (area_pot + area_nonpot) == 0:
                        warnings.warn(
                            f"No overlap between potential vegetation map and shape_id {i}"
                        )
                    else:
                        area_pot_perc = area_pot / (area_pot + area_nonpot)
                        self.area_pot_perc[row[veg]].loc[i] = area_pot_perc

                        area_pot_perc_optimistic = np.min(
                            [100 * area_pot / area_effective, 100]
                        )

                        self.area_pot_perc_optimistic[row[veg]].loc[
                            i
                        ] = area_pot_perc_optimistic

                        area_nonpot_optimistic = np.max([0, area_effective - area_pot])
                        self.area_nonpot_optimistic[row[veg]].loc[
                            i
                        ] = area_nonpot_optimistic

                        # vegetation type is present (actual presence), for polygon count
                        self.veg_present[row[veg]].loc[i] = 1

        # create summary table per vegetation type

        summary = {}
        summary["area_effective"] = self.area_effective.sum()
        summary["nonpot"] = self.area_nonpot.sum()
        summary["nonpot_opt"] = self.area_nonpot_optimistic.sum()
        summary["pot"] = self.area_pot.sum()
        summary["polygon_count"] = self.veg_present.sum()

        summary["score"] = 100 * summary["pot"] / (summary["pot"] + summary["nonpot"])
        summary["score_opt"] = (
            100 * summary["pot"] / (summary["pot"] + summary["nonpot_opt"])
        )

        self.summary = pd.DataFrame(summary)

    def store(self, path, overwrite=False):
        path = Path(path)
        if path.exists() and not overwrite:
            if not path.is_dir():
                raise NicheOverlayException(f"path {path} is not an empty folder")
            if any(path.iterdir()):
                raise NicheOverlayException(f"path {path} exists and is not empty")
        path.mkdir(parents=True, exist_ok=True)

        # save individual tables

        for t in self._tables:
            getattr(self, t).dropna(axis=0, how="all").to_csv(path / (t + ".csv"))

        self.potential_presence.to_csv(path / "potential_presence.csv")
        self.summary.to_csv(path / "summary.csv")

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=DeprecationWarning)
            warnings.filterwarnings("ignore", category=FutureWarning)
            self.joined_map().to_file(path / "overlay.gpkg")

    def joined_map(self):
        merged = self.map
        for table in self._tables:
            merged = merged.join(getattr(self, table).add_prefix(f"{table}_"))

        return merged
