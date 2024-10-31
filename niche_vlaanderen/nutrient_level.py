import numpy as np
import pandas as pd

from niche_vlaanderen.codetables import (validate_tables_nutrient_level,
                                         check_codes_used, package_resource)


class NutrientLevel(object):
    """Calculate the NutrientLevel

    The used codetables can be overwritten by using the corresponding ct_*
    arguments.
    """

    dtype = "uint8"
    nodata = 255  # unsigned 8 bit integer for nutrient level

    def __init__(
        self,
        ct_lnk_soil_nutrient_level=None,
        ct_management=None,
        ct_mineralisation=None,
        ct_soil_code=None,
        ct_nutrient_level=None,
    ):
        """Create a nutrient level calculator

        Parameters
        ----------
        ct_lnk_soil_nutrient_level : str, Optional
            Path to the lnk_soil_nutrient_level system table to overwrite the default.
        ct_management : str, Optional
            Path to the management system table to overwrite the default.
        ct_mineralisation : str, Optional
            Path to the nitrogen_mineralisation system table to overwrite the default.
        ct_soil_code : str, Optional
            Path to the soil_codes system table to overwrite the default.
        ct_nutrient_level : str, Optional
            Path to the nutrient_level system table to overwrite the default.
        """
        if ct_lnk_soil_nutrient_level is None:
            ct_lnk_soil_nutrient_level = package_resource(
                ["system_tables"], "lnk_soil_nutrient_level.csv")
        if ct_management is None:
            ct_management = package_resource(
                ["system_tables"], "management.csv")
        if ct_mineralisation is None:
            ct_mineralisation = package_resource(
                ["system_tables"], "nitrogen_mineralisation.csv")
        if ct_soil_code is None:
            ct_soil_code = package_resource(
                ["system_tables"], "soil_codes.csv")
        if ct_nutrient_level is None:
            ct_nutrient_level = package_resource(
                ["system_tables"], "nutrient_level.csv")

        self.ct_lnk_soil_nutrient_level = pd.read_csv(ct_lnk_soil_nutrient_level)
        self._ct_management = pd.read_csv(ct_management)
        self._ct_mineralisation = pd.read_csv(ct_mineralisation)
        self._ct_nutrient_level = pd.read_csv(ct_nutrient_level)
        self._ct_soil_code = pd.read_csv(ct_soil_code)

        # convert the mineralisation system table to float to use np.nan for nodata
        self._ct_mineralisation["nitrogen_mineralisation"] = self._ct_mineralisation[
            "nitrogen_mineralisation"
        ].astype("float32")

        inner = all(v is None for v in self.__init__.__code__.co_varnames[1:])
        validate_tables_nutrient_level(
            self.ct_lnk_soil_nutrient_level,
            self._ct_management,
            self._ct_mineralisation,
            self._ct_soil_code,
            self._ct_nutrient_level,
            inner=inner,
        )

        # join soil_code to soil_name where needed
        self._ct_soil_code = pd.read_csv(ct_soil_code).set_index("soil_name")
        self._ct_mineralisation["soil_code"] = (
            self._ct_soil_code.soil_code[self._ct_mineralisation["soil_name"]]
            .reset_index()
            .soil_code
        )
        self.ct_lnk_soil_nutrient_level["soil_code"] = (
            self._ct_soil_code.soil_code[self.ct_lnk_soil_nutrient_level["soil_name"]]
            .reset_index()
            .soil_code
        )

    def _calculate_mineralisation(self, soil_code, msw):
        """Calculate nitrogen mineralisation based on soil and water arrays

        Parameters
        ----------
        soil_code : numpy.ndarray, np.uint8
            Array containing the soil codes. Values must be present
            in the soil_code system table.
        msw : numpy.ndarray, np.float32
            Array containing the mean spring waterlevel ("gemiddeld
            voorjaarsgrondwaterstand").

        Returns
        -------
        numpy.ndarray, numpy.float32
            mineralisation
        """
        nodata = (soil_code == 255) | np.isnan(msw)

        orig_shape = soil_code.shape
        soil_code_array = soil_code.flatten()
        msw_array = msw.flatten()
        result = np.ones(soil_code_array.shape, dtype="float32") * np.nan

        for code in self._ct_mineralisation.soil_code.unique():
            # We must reset the index because digitize will give indexes
            # compared to the new table.
            select = self._ct_mineralisation.soil_code == code
            table_sel = self._ct_mineralisation[select].copy()
            table_sel = table_sel.reset_index(drop=True)
            soil_sel = soil_code_array == code
            ix = np.digitize(msw_array[soil_sel], table_sel.msw_max, right=False)
            result[soil_sel] = table_sel["nitrogen_mineralisation"].reindex(ix).values

        # The intermediate mineralisation array is a float32 array with np.nan as nodata
        result = result.reshape(orig_shape).astype(np.float32)
        result[nodata] = np.nan # Apply the nodata mask
        return result

    def _calculate(self, management, soil_code, nitrogen, inundation):
        """Calculate the nutrient level based on calculated nitrogen

        Parameters
        ----------
        management : numpy.ndarray, np.uint8
            Array containing the management codes. Values must be present
            in the management system table.
        soil_code : numpy.ndarray, np.uint8
            Array containing the soil codes. Values must be present
            in the soil_code system table.
        nitrogen : numpy.ndarray, np.float32
            Array containing the calculated nitrogen levels.
        inundation : numpy.ndarray, np.uint8
            Array containing the inundation values.

        Returns
        -------
         numpy.ndarray, np.uint8
            nutrient level
        """
        check_codes_used("management", management, self._ct_management["management"])
        check_codes_used("soil_code", soil_code, self._ct_soil_code["soil_code"])

        nodata = ((management == 255) | (soil_code == 255) |
                  np.isnan(nitrogen) | (inundation == 255))

        # calculate management influence
        influence = np.ones(management.shape, dtype=self.dtype) * self.nodata
        for i in self._ct_management.management.unique():
            sel_grid = management == i
            sel_ct = self._ct_management.management == i
            influence[sel_grid] = self._ct_management[sel_ct].influence.values[0]

        # flatten all input layers
        orig_shape = soil_code.shape
        soil_code = soil_code.flatten()
        nitrogen = nitrogen.flatten()

        inundation = inundation.flatten()
        influence = influence.flatten()

        result = influence
        # search for classification values in nutrient level codetable
        for name, subtable in self.ct_lnk_soil_nutrient_level.groupby(
            ["soil_code", "influence"]
        ):

            soil_selected, influence_selected = name
            table_sel = subtable.copy(deep=True).reset_index(drop=True)

            index = np.digitize(nitrogen, table_sel.total_nitrogen_max, right=True)
            index[nodata.flatten()] = self.nodata
            selection = (soil_code == soil_selected) & (influence == influence_selected)
            # Add the no-data value to the mapping
            table_sel.loc[self.nodata, "nutrient_level"] = self.nodata
            result[selection] = table_sel.nutrient_level[index].iloc[selection].values

        # Note that niche_vlaanderen is different from the original (Dutch)
        # model here:
        # only if nutrient_level < 4 the inundation rule is applied.
        result[result < 4] = (result + (inundation > 0))[result < 4]

        result = result.reshape(orig_shape).astype(self.dtype)
        result[nodata] = self.nodata  # Apply the nodata mask
        return result

    def calculate(
        self,
        soil_code,
        msw,
        nitrogen_atmospheric,
        nitrogen_animal,
        nitrogen_fertilizer,
        management,
        inundation,
    ):
        """Calculates the nutrient level based on the input arrays provided

        Parameters
        ----------
        soil_code :  numpy.ndarray, np.uint8
            Array containing the soil codes. Values must be present
            in the soil_code table.
        msw : numpy.ndarray, np.float32
            Array containing the mean spring waterlevel.
        nitrogen_atmospheric : numpy.ndarray, np.float32
            Array containing the atmospheric deposition of Nitrogen.
        nitrogen_animal : numpy.ndarray, np.float32
            Array containing the animal contribution of Nitrogen.
        nitrogen_fertilizer : numpy.ndarray, np.float32
            Array containing the fertilizer contribution of Nitrogen.
        management :  numpy.ndarray, np.uint8
            Array containing the management.
        inundation :  numpy.ndarray, np.uint8
            Array containing the inundation values.

        Returns
        -------
        numpy.ndarray, np.uint8
            nutrient level
        """

        nitrogen_mineralisation = self._calculate_mineralisation(soil_code, msw)
        total_nitrogen = (
            nitrogen_mineralisation
            + nitrogen_atmospheric
            + nitrogen_animal
            + nitrogen_fertilizer
        )
        nutrient_level = self._calculate(
            management, soil_code, total_nitrogen, inundation
        )
        return nutrient_level
