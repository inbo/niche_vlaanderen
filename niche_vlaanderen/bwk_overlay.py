from pkg_resources import resource_filename

import geopandas as gpd
import pandas as pd
from rasterstats import zonal_stats

from .niche import Niche

class NicheOverlay(object):
    """ Creates a new NicheOverlay object

    Overlays the BWK (Biologische waarderingskaart) with niche in order to
    obtain the accuracy of the model

    Parameters:
        niche: niche_vlaanderen.Niche
            Niche object containing predicted variables types according to niche.
            The model must have run prior to the overlay
        map: Path
            Path to a file containing the BWK map in one of the formats supported by fiona.
        mapping_file: Path | None
            optional file containing the mapping
        mapping_columns: list(tuples) | None
            Optional list containing the different mappings between columns.
            If not specified, the default mapping will be used.
            Custom mappings are defined as tuples
            (source column in map, source field in mapping_file, to_field in mapping_file, resulting_column)
            eg:
            [('HAB1', 'HAB', 'NICHE_C', 'NICH_1_1']

        ct_* lnk_*: path
          Optionally, paths to codetables can be provided. These will override
          the standard codetables used by Niche.

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
                'HAB1': 'HAB',
                'HAB2': 'HAB',
                'HAB3': 'HAB',
                'HAB4': 'HAB'
            }
        if mapping_file is None:
            mapping_file = resource_filename(
             "niche_vlaanderen", "system_tables/hab_niche_join.csv")

        self.mapping = pd.read_csv(mapping_file)

        if mapping_columns is not None:
            self.mapping_columns = mapping_columns
        else:
            self.mapping_columns = []
            for i in range(1,6):
                for j in range(1,3):
                    self.mapping_columns.append(
                        {'map_key': f"HAB{i}",
                         'join_key': "HAB",
                         'join_value': f"NICHE_C{j}",
                         'new_column':f"NICH_{i}_{j}"}
                    )

        # TODO: geopandas allows using a bbox or mask
        self.map = gpd.read_file(map)
        self._check_mapping_columns()

    def _check_mapping_columns(self):
        """Checks whether the mapping columns are present in the dataset"""
        # TODO
        pass

    def overlay(self):
        """Overlays the map and the niche object"""

        # add mapping columns to source
        for t in self.mapping_columns:
            source = self.mapping[[t['join_key'], t['join_value']]].rename({t['join_value'],t['new_column'] })
            self.map = pd.merge(self.map,
                                source,
                                left_on=t['map_key'],
                                right_on=t['join_key'],
                                )

        # get potential presence
        potential_presence = self.niche.zonal_stats(self.map, outside=False)

        # actual presence - optimistic
        for row in self.map.iterrows():
            pass

        # combine

        # aggregate

