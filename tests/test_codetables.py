from unittest import TestCase
import pandas as pd
from niche_vlaanderen.codetables import CodeTableException
from niche_vlaanderen.codetables import CodeTableValidator as ctv
import pytest


class TestCodeTables(TestCase):
    def test_boundaries_correct(self):
        df = pd.read_csv("niche_vlaanderen/system_tables/soil_mlw_class.csv")
        ctv.check_lower_upper_boundaries(
            df, "mlw_min", "mlw_max", "soil_mlw_class")

    def test_boundaries_incorrect(self):
        df = pd.read_csv("tests/data/bad_ct/bad_boundaries.csv")
        with pytest.raises(CodeTableException):
            ctv.check_lower_upper_boundaries(
                df, "mlw_min", "mlw_max", "soil_mlw_class")
