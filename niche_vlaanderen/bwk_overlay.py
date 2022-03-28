from pkg_resources import resource_filename
import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=UserWarning)
    import geopandas as gpd

import pandas as pd
import numpy as np
from rasterstats import zonal_stats

from .niche import Niche

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
            and Niche vegetation types. An example mapping type is part of the
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
            eg:
            [{'map_key': 'HAB1',
              'join_key': 'HAB',
              'join_value': 'NICHE_C1',
              'new_column': 'NICH_1_1'}, ...]

    """

    def __init__(self, niche, map, mapping_file=None, mapping_columns=None):

        if type(niche) is Niche:
            self.niche = niche
        else:
            raise ValueError("pass a valid Niche object")

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

        self.mapping = pd.read_csv(mapping_file)

        # TODO: check if we can force the values to be integer instead of float

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
        self.map = gpd.read_file(map)
        self._check_mapping_columns()

    def _check_mapping_columns(self):
        """Checks whether the mapping columns are present in the dataset"""
        for item in self.mapping_columns:
            print(item["map_key"])
            if item["map_key"] not in self.map.columns:
                raise(NicheOverlayException(f"expected column {item['map_key']} not found in shape file"))
            if f'p{item["map_key"]}' not in self.map.columns:
                raise (NicheOverlayException(
                    f"expected column p{item['map_key']} not found in shape file"))
        pass

    def overlay(self):
        """Overlays the map and the niche object"""

        # add mapping columns to source
        for t in self.mapping_columns:
            source = self.mapping[[t["join_key"], t["join_value"]]].rename(
                columns={t["join_value"]: t["new_column"], t["join_key"]: t["map_key"]}
            )
            self.map = pd.merge(self.map, source, on=t["map_key"], how="left")
        self._niche_columns = self.map.columns[self.map.columns.str.startswith("NICH")]
        # get potential presence
        self.potential_presence = self.niche.zonal_stats(self.map, outside=False)

        self.potential_presence = self.potential_presence.pivot(
            columns=["vegetation"], index=["presence", "shape_id"]
        )

        summary = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        summary_area = self.potential_presence.loc["no data"]["area_ha"] * np.nan
        # Only if actual present: (pHAB * present) / (present + not present)
        for i, row in self.map.iterrows():
            for veg in self._niche_columns:
                if np.isfinite(row[veg]) and row[veg] != 0:
                    area_pot = (
                        self.potential_presence.loc["present"]
                        .loc[i]
                        .loc["area_ha"][row[veg]]
                    )
                    area_nopot = (
                        self.potential_presence.loc["not present"]
                        .loc[i]
                        .loc["area_ha"][row[veg]]
                    )

                    # use correct pHAB for vegetation
                    # note that veg has this form: NICH_1_2 -> position 5 is the corresponding
                    # pHAB part.
                    pHab = row["pHAB" + veg[5]]
                    summary[row[veg]].loc[i] = pHab * area_pot
                    summary_area[row[veg]].loc[i] = area_pot + area_nopot

            pass
        self.summary = summary
        self.summary_area = summary_area

        self.score = self.summary.sum() / self.summary_area.sum()

        # aggregate

class NicheOverlayException(Exception):
    msg = "Error using Niche Overlay"