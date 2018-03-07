import numpy as np
from .exception import NicheException
import warnings


class CodeTableException(Exception):
    """
    Exception while validating the code tables
    """


def check_lower_upper_boundaries(df, min_col, max_col, value):
    """Checks whether there are no overlaps between min_col and max_col

    Parameters
    ==========
    df: dataframe to check, must contain min_col and max_col
    min_col, max_col: columns containing the mni and max value
    value: the column containing the reclassified value

    This function will check if there are no overlapping values when
    classifying the dataframe (df).
    """

    group_cols = set(df.columns.tolist()) - {min_col, max_col, value}
    for sel_group, subtable in df.groupby(list(group_cols)):
        min_values = subtable[min_col]
        max_values = subtable[max_col]
        for (i, index) in enumerate(min_values.index):
            if i > 0:
                if(min_values[index] != max_values[prev_index]):  # noqa: flake8
                    raise CodeTableException(
                        "Min and max values in table do not correspond"
                    )
            prev_index = index  # noqa: flake8


def check_join(df1, df2, f1, f2=None, inner=True):
    """
    Checks if keys for columns in two dataframes are present.
    If 'inner' is specified values of both columns must be the same.
    If 'inner' is false all keys of df1 have to be present in df2.

    Parameters
    ==========
    df1: first dataframe
    df2: second dataframe
    f1: field in first dataframe
    f2: field in second dataframe
    inner: boolean


    Returns
    =======
    None on succesful usage - will raise a CodeTableException on Failure
    """
    if f2 is None:
        f2 = f1

    u2 = np.unique(df2[f2])
    u1 = np.unique(df1[f1])

    if not np.array_equal(u1, u2):
        if inner:
            raise CodeTableException(
                "Different keys exist in tables.")
        else:
            if not np.all(np.isin(u1, u2)):
                raise CodeTableException(
                    "Not all codes from table 1 are in table 2")
            else:
                warnings.warn("Warning, different keys exist in tables")
        print(u1)
        print(u2)


def check_unique(df, col):
    u = df[col].unique()
    if u.size != df[col].size:
        raise CodeTableException(
            "Non unique fields in column {}".format(col))


def validate_tables_acidity(ct_acidity, ct_soil_mlw_class,
                            ct_soil_codes, lnk_acidity, ct_seepage, inner):

    # check tables
    check_unique(ct_soil_codes, "soil_code")
    check_unique(ct_soil_codes, "soil_name")

    check_unique(ct_acidity, "acidity")

    check_unique(ct_seepage, "seepage")
    check_lower_upper_boundaries(ct_seepage, "seepage_min", "seepage_max",
                                 "seepage")

    # check links between tables
    check_join(lnk_acidity, ct_acidity, "acidity", inner=inner)
    check_join(ct_soil_mlw_class, ct_soil_codes, "soil_group", inner=inner)
    check_join(lnk_acidity, ct_soil_mlw_class, "soil_mlw_class", inner=inner)
    check_join(lnk_acidity, ct_seepage, "seepage", inner=inner)


def validate_tables_nutrient_level(ct_lnk_soil_nutrient_level, ct_management,
                                   ct_mineralisation, ct_soil_code,
                                   ct_nutrient_level, inner):
    # check tables
    check_unique(ct_soil_code, "soil_code")
    check_unique(ct_soil_code, "soil_name")
    check_unique(ct_management, "code")

    check_lower_upper_boundaries(ct_mineralisation, "msw_min", "msw_max",
                                 "nitrogen_mineralisation")
    check_join(ct_mineralisation, ct_soil_code, "soil_name", inner=inner)

    check_join(ct_lnk_soil_nutrient_level, ct_management,
               "management_influence", "influence", inner=inner)

    check_lower_upper_boundaries(ct_lnk_soil_nutrient_level,
                                 "total_nitrogen_min", "total_nitrogen_max",
                                 "nutrient_level")

    check_join(ct_lnk_soil_nutrient_level, ct_soil_code, "soil_name",
               inner=inner)
    check_join(ct_lnk_soil_nutrient_level, ct_nutrient_level,
               "nutrient_level", "code", inner=inner)


def validate_tables_vegetation(ct_vegetation, ct_soil_code, ct_inundation,
                               ct_management, ct_acidity, ct_nutrient_level,
                               inner):

    check_join(ct_vegetation, ct_inundation, "inundation", inner=inner)
    check_join(ct_vegetation, ct_acidity, "acidity", inner=inner)
    check_join(ct_vegetation, ct_nutrient_level, "nutrient_level", "code",
               inner=inner)
    check_join(ct_vegetation, ct_management, "management", "code", inner=inner)

    # extra check: per vegetation type, soil_code only one mhw, mlw combination
    #  is allowed. Otherwise the simple model may give unexpected results.
    cols = ["veg_code", "soil_name"]
    grouped = ct_vegetation[["veg_code", "soil_name", "mhw_min", "mhw_max",
                             "mlw_min", "mlw_max"]].groupby(cols)

    for (veg_code, soil_name), subtable in grouped:
        st_unique = subtable.drop_duplicates()

        if st_unique.shape[0] != 1:
            print(st_unique)
            raise CodeTableException("Non unique mhw/mlw combinations")


def validate_tables_floodplains(depths, duration, frequency, lnk_potential,
                                potential, inner):
    # test disabled as we have a 0 code which is not in lnk_potential
    # check_join(lnk_potential, depths, "depth","code")
    check_join(lnk_potential, duration, "duration", "code", inner)
    check_join(lnk_potential, frequency, "frequency", "code", inner)
    # test disabled as we have a code 4 which is not in lnk_potential
    # check_join(lnk_potential, potential, "potential", "code")


def check_codes_used(name, used, allowed):
    """

    """
    if isinstance(used, str) or isinstance(used, int):
        used = np.array(used)

    if used.dtype.kind == 'f':
        used_codes = set(np.unique(used[~np.isnan(used)]))
    else:
        used_codes = set(np.unique(used))

    allowed_codes = set(allowed)
    allowed_codes.add(-99)  # no data when loaded from grid
    if name in ["acidity", "nutrient_level"]:  # no data value when calculated
        allowed_codes.add(255)

    if not used_codes.issubset(allowed_codes):
        msg = "Invalid %s code used\n" % name
        msg += "used: %s\n" % str(used_codes)
        msg += "possible: %s" % str(allowed_codes)
        raise NicheException(msg)
