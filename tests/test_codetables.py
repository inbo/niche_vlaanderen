import pandas as pd
import pytest
from unittest import TestCase

import niche_vlaanderen
from niche_vlaanderen.codetables import check_join, check_unique,\
    check_lower_upper_boundaries, CodeTableException, validate_tables_acidity


class TestCodeTables:
    def test_boundaries_correct(self, path_system_tables):
        df = pd.read_csv(path_system_tables / "soil_mlw_class.csv")
        check_lower_upper_boundaries(
            df, "mlw_min", "mlw_max", "soil_mlw_class")

    def test_boundaries_incorrect(self, path_system_tables, path_testdata):
        df = pd.read_csv(path_testdata / "bad_ct" / "bad_boundaries.csv")
        with pytest.raises(CodeTableException):
            check_lower_upper_boundaries(
                df, "mlw_min", "mlw_max", "soil_mlw_class")

    def test_unique(self, path_system_tables):
        df = pd.read_csv(path_system_tables / "soil_codes.csv")
        check_unique(df, "soil_code")
        df = pd.read_csv(path_system_tables / "soil_mlw_class.csv")
        with pytest.raises(CodeTableException):
            check_unique(df, "soil_group")

    @pytest.mark.parametrize("inner",
                             [True, False])
    def test_codetables_acidity(self, inner, path_system_tables):
        """Validation of code tables works for inner check with False & True."""
        ct_acidity = pd.read_csv(path_system_tables / "acidity.csv")
        ct_soil_mlw_class = pd.read_csv(path_system_tables / "soil_mlw_class.csv")
        ct_soil_codes = pd.read_csv(path_system_tables / "soil_codes.csv")
        lnk_acidity = pd.read_csv(path_system_tables / "lnk_acidity.csv")
        ct_seepage = pd.read_csv(path_system_tables / "seepage.csv")

        validate_tables_acidity(ct_acidity=ct_acidity,
                                ct_soil_mlw_class=ct_soil_mlw_class,
                                ct_soil_codes=ct_soil_codes,
                                lnk_acidity=lnk_acidity,
                                ct_seepage=ct_seepage,
                                inner=inner)

    def test_vegetation(self, path_testdata):
        # should not raise
        niche_vlaanderen.Vegetation()
        badveg = path_testdata / "bad_ct" / "bad_vegetation.csv"
        with pytest.warns(UserWarning):
            with pytest.raises(CodeTableException):
                niche_vlaanderen.Vegetation(ct_vegetation=badveg)

    def test_inner_join(self, path_system_tables):
        df1 = pd.read_csv(path_system_tables / "soil_codes.csv")
        print(df1)
        with pytest.raises(CodeTableException):
            check_join(df1, df1, "soil_code", "soil_group")

    def test_inner_join2(self, path_system_tables, path_testdata):
        '''

        The previous test only check whether two completely separate
        codes raise - this test checks for partly overlapping sets.
        '''
        df1 = pd.read_csv(path_testdata / "bad_ct" / "one_vegetation.csv")
        df2 = pd.read_csv(path_system_tables / "niche_vegetation.csv")

        with pytest.raises(CodeTableException):
            check_join(df2, df1, "veg_code", "veg_code", inner=False)
        with pytest.warns(UserWarning):
            check_join(df1, df2, "veg_code", "veg_code", inner=False)


    def test_unique_mlw(self, path_testdata):
        badveg = path_testdata / "bad_ct" / "differentmlw.csv"
        with pytest.raises(CodeTableException):
            niche_vlaanderen.Vegetation(ct_vegetation=badveg)
