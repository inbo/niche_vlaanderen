from unittest import TestCase
import pandas as pd
from niche_vlaanderen.codetables import *
import pytest
import niche_vlaanderen

class TestCodeTables(TestCase):
    def test_boundaries_correct(self):
        df = pd.read_csv("niche_vlaanderen/system_tables/soil_mlw_class.csv")
        check_lower_upper_boundaries(
            df, "mlw_min", "mlw_max", "soil_mlw_class")

    def test_boundaries_incorrect(self):
        df = pd.read_csv("tests/data/bad_ct/bad_boundaries.csv")
        with pytest.raises(CodeTableException):
            check_lower_upper_boundaries(
                df, "mlw_min", "mlw_max", "soil_mlw_class")

    def test_unique(self):
        df = pd.read_csv("niche_vlaanderen/system_tables/soil_codes.csv")
        check_unique(df, "soil_code")
        df = pd.read_csv("niche_vlaanderen/system_tables/soil_mlw_class.csv")
        with pytest.raises(CodeTableException):
            check_unique(df, "soil_group")

    def test_codetables_acidity(self):
        ct_acidity = pd.read_csv(
             "niche_vlaanderen/system_tables/acidity.csv")
        ct_soil_mlw_class = pd.read_csv(
             "niche_vlaanderen/system_tables/soil_mlw_class.csv")
        ct_soil_codes = pd.read_csv(
             "niche_vlaanderen/system_tables/soil_codes.csv")
        lnk_acidity = pd.read_csv(
             "niche_vlaanderen/system_tables/lnk_acidity.csv")
        ct_seepage = pd.read_csv(
             "niche_vlaanderen/system_tables/seepage.csv")

        validate_tables_acidity(ct_acidity=ct_acidity,
                                ct_soil_mlw_class=ct_soil_mlw_class,
                                ct_soil_codes=ct_soil_codes,
                                lnk_acidity=lnk_acidity,
                                ct_seepage=ct_seepage)

    def test_vegetation(self):
        # should not raise
        v = niche_vlaanderen.Vegetation()
        badveg =  "tests/data/bad_ct/bad_vegetation.csv"
        with pytest.raises(CodeTableException):
            v = niche_vlaanderen.Vegetation(ct_vegetation=badveg)
