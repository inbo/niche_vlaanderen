from unittest import TestCase
import pandas as pd
from niche_vlaanderen.codetables import check_join, check_unique,\
    check_lower_upper_boundaries, CodeTableException, validate_tables_acidity
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

        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])

        validate_tables_acidity(ct_acidity=ct_acidity,
                                ct_soil_mlw_class=ct_soil_mlw_class,
                                ct_soil_codes=ct_soil_codes,
                                lnk_acidity=lnk_acidity,
                                ct_seepage=ct_seepage,
                                inner=inner)

    def test_vegetation(self):
        # should not raise
        niche_vlaanderen.Vegetation()
        badveg = "tests/data/bad_ct/bad_vegetation.csv"
        with pytest.warns(UserWarning):
            with pytest.raises(CodeTableException):
                niche_vlaanderen.Vegetation(ct_vegetation=badveg)

    def test_inner_join(self):
        df1 = pd.read_csv("niche_vlaanderen/system_tables/soil_codes.csv")
        print(df1)
        with pytest.raises(CodeTableException):
            check_join(df1, df1, "soil_code", "soil_group")

    def test_inner_join2(self):
        '''

        The previous test only check whether two completely separate
        codes raise - this test checks for partly overlapping sets.
        '''
        df1 = pd.read_csv("tests/data/bad_ct/one_vegetation.csv")
        df2 = pd.read_csv("niche_vlaanderen/system_tables/niche_vegetation.csv")

        with pytest.raises(CodeTableException):
            check_join(df2, df1, "veg_code", "veg_code", inner=False)
        with pytest.warns(UserWarning):
            check_join(df1, df2, "veg_code", "veg_code", inner=False)


    def test_unique_mlw(self):
        badveg = "tests/data/bad_ct/differentmlw.csv"
        with pytest.raises(CodeTableException):
            niche_vlaanderen.Vegetation(ct_vegetation=badveg)
