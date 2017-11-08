class CodeTableException(Exception):
    """
    Exception while validating the code tables
    """


codetables = ["ct_acidity", "ct_soil_mlw_class", "ct_soil_codes",
                "lnk_acidity", "ct_seepage", "ct_vegetation", "ct_management",
                "ct_nutrient_level", "ct_mineralisation"]


class CodeTableValidator(object):

    @staticmethod
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
                    if(min_values[index] != max_values[prev_index]):
                        raise CodeTableException(
                            "Min and max values in table do not correspond"
                        )
                prev_index = index
