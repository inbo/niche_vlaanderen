from __future__ import division
from collections import Counter
import distutils.spawn
import os
import shutil
import subprocess
from functools import partial
import yaml

import pytest
from matplotlib.testing.decorators import image_comparison
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from rasterio.errors import RasterioIOError

import niche_vlaanderen
from niche_vlaanderen.exception import NicheException


class TestNiche:
    def test_invalidfile(self):
        n = niche_vlaanderen.Niche()
        with pytest.raises(RasterioIOError):
            n.set_input("msw", "nonexistingfile")

    def test_invalid_input_type(self, path_testcase):
        n = niche_vlaanderen.Niche()
        with pytest.raises(NicheException):
            n.set_input("bla",
                        path_testcase / "zwarte_beek" / "input" / "soil_code.asc")


    @pytest.mark.parametrize("variable,unique_data,nodata", [
        ("soil_code",
         np.array([ 8, 11, 13,  255], dtype="uint8"),
         partial(np.isin, test_elements=[255])),
        ("mlw",
         np.array([-148., -129., -123., -117., -113.], dtype="float32"), np.isnan)
    ])
    def test_read_rasterio_to_grid(self, path_testcase, variable, unique_data, nodata):
        """Read function returns masked numpy array with correct datatype for inputs."""
        n = niche_vlaanderen.Niche()
        file_path = path_testcase / "zwarte_beek" / "input" / f"{variable}.asc"
        n.set_input(variable, file_path)
        band = n.read_rasterio_to_grid(file_path, variable_name=variable)

        # Read grids as masked array with correct datatype
        np.testing.assert_array_equal(np.unique(band)[:5], unique_data)
        assert band.dtype == unique_data.dtype


    def test_zwarte_beek(self, tmp_path, path_testcase, zwarte_beek_niche):
        """Check if the model runs succesfully with data from the testcase/zwarte_beek.

        No data validation itself is done as part of this test
        """
        myniche = zwarte_beek_niche()
        myniche.run()

        o1 = myniche.occurrence
        o1 = pd.DataFrame(o1, index=[0])

        input_dir = path_testcase / "zwarte_beek" / "input"

        myniche.set_input("management_vegetation", input_dir / "management.asc")
        myniche.run()
        o2 = myniche.occurrence
        o2 = pd.DataFrame(o2, index=[0])

        myniche.set_input("inundation_vegetation", input_dir / "inundation.asc")
        myniche.run()
        o3 = myniche.occurrence
        o3 = pd.DataFrame(o3, index=[0])

        assert np.all(o1 >= o2)
        assert np.all(o2 >= o3)

        # if a subdir does not exist - it should be created
        tmpdir = tmp_path / "subdir"
        myniche.write(tmpdir)
        # check tempdir contains the vegetation and the abiotic files
        expected_files = [
            "nutrient_level.tif",
            "acidity.tif",
            "V01.tif",
            "V02.tif",
            "V03.tif",
            "V04.tif",
            "V05.tif",
            "V06.tif",
            "V07.tif",
            "V08.tif",
            "V09.tif",
            "V10.tif",
            "V11.tif",
            "V12.tif",
            "V13.tif",
            "V14.tif",
            "V15.tif",
            "V16.tif",
            "V17.tif",
            "V18.tif",
            "V19.tif",
            "V20.tif",
            "V21.tif",
            "V22.tif",
            "V23.tif",
            "V24.tif",
            "V25.tif",
            "V26.tif",
            "V27.tif",
            "V28.tif",
            "log.txt",
            "summary.csv",
        ]

        dir_listing = os.listdir(tmpdir)
        assert set(expected_files) == set(dir_listing)

        # run check after predefined acidity
        myniche = zwarte_beek_niche()
        myniche.set_input("acidity", tmpdir / "acidity.tif")
        myniche.run()

        tmpdir_acidity = tmp_path / "acidity"
        myniche.write(tmpdir_acidity)

        dir_listing = os.listdir(tmpdir_acidity)
        expected_files.remove("acidity.tif")
        assert set(expected_files) == set(dir_listing)

    def test_zwarte_beek_constant_values(self, zwarte_beek_niche):
        """Check if the model runs succesfully with constant values."""
        myniche = zwarte_beek_niche()
        myniche.set_input("rainwater", 0)
        assert "rainwater" not in myniche._inputfiles
        myniche.set_input("nitrogen_fertilizer", 0)
        myniche.run()

        myniche2 = zwarte_beek_niche()
        myniche2.run()
        assert myniche.occurrence == myniche2.occurrence

    def test_testcase_simple(self, tmp_path, path_testcase):
        """Check if the simple model runs succesfully with data from the
        testcase/zwarte_beek.

        No data validation itself is done as part of this test (see vegetation module
        tests)
        """
        myniche = niche_vlaanderen.Niche()
        input_dir = path_testcase / "zwarte_beek" / "input"

        myniche.set_input("soil_code", input_dir / "soil_code.asc")
        myniche.set_input("mhw", input_dir / "mhw.asc")
        myniche.set_input("mlw", input_dir / "mlw.asc")
        myniche.name = "simple"
        myniche.run(full_model=False)
        myniche.write(tmp_path)
        # check tempdir contains the vegetation files
        expected_files = [
            "V01.tif",
            "V02.tif",
            "V03.tif",
            "V04.tif",
            "V05.tif",
            "V06.tif",
            "V07.tif",
            "V08.tif",
            "V09.tif",
            "V10.tif",
            "V11.tif",
            "V12.tif",
            "V13.tif",
            "V14.tif",
            "V15.tif",
            "V16.tif",
            "V17.tif",
            "V18.tif",
            "V19.tif",
            "V20.tif",
            "V21.tif",
            "V22.tif",
            "V23.tif",
            "V24.tif",
            "V25.tif",
            "V26.tif",
            "V27.tif",
            "V28.tif",
            "log.txt",
            "summary.csv",
        ]

        expected_files = ["simple_" + i for i in expected_files]

        dir_listing = os.listdir(tmp_path)
        assert Counter(list(expected_files)) == Counter(list(dir_listing))

    def test_soil_tif_float32(self, zwarte_beek_niche, path_tests):
        """Test that float32 soil code files are parsed correctly
        cfr bug report #334
        """
        myniche = zwarte_beek_niche()
        input_dir = path_tests / "data" / "tif"

        myniche.set_input("soil_code", input_dir / "soil_smallerextent_float.tif")
        myniche.run(full_model=False)
        # check a position which is nan in soil code and not in mhw
        # this should be nan in output
        coords = ~myniche._context.transform*(216796,198172)
        coords = (int(coords[0]), int(coords[1]))

        # Nan-values in tiff propagate to Masked Values
        assert myniche._inputarray["soil_code"][coords] == 255
        assert myniche._inputarray["mhw"][coords] == 3.0
        assert myniche._vegetation[14][coords] == 255

    @pytest.mark.skipif(
        shutil.which("gdalinfo") is None,
        reason="gdalinfo not available in the environment.",
    )
    def test_zwarte_beek_validate(self, tmp_path, zwarte_beek_niche):
        """Verify gdalinfo correct write of data and metadata on the output files."""
        myniche = zwarte_beek_niche()
        myniche.run()
        myniche.write(tmp_path)

        info = subprocess.check_output(
            ["gdalinfo", "-stats", os.path.join(tmp_path, "V01.tif")]
        ).decode("utf-8")
        print(info)
        assert "(216580.000000000000000,198580.000000000000000)" in info
        assert "STATISTICS_MAXIMUM=1" in info
        assert "STATISTICS_MINIMUM=0" in info

    def test_windowed_read(self, zwarte_beek_niche, path_testdata):
        """Spatial context is adjusted to the smaller grid"""
        myniche = zwarte_beek_niche()
        myniche.set_input("mlw", path_testdata / "part_zwarte_beek_mlw.asc")
        myniche.run(full_model=True)
        assert 37 == myniche._context.width
        assert 37 == myniche._context.height

    def test_deviation(self, zwarte_beek_niche):
        myniche = zwarte_beek_niche()
        myniche.run(deviation=True)
        # check dict exists and contains enough nan values: the original mask AND
        # the nan values from the deviation calculation
        assert 14400 == np.isnan(myniche._deviation["mhw_04"]).sum()

    @pytest.mark.skipif(
        shutil.which("gdalinfo") is None,
        reason="gdalinfo not available in the environment.",
    )
    def test_write_deviation(self, tmp_path, small_niche):
        """Verify gdalinfo correct write of data and metadata on the deviation files."""
        myniche = small_niche
        myniche.run(deviation=True, full_model=False)

        myniche.write(tmp_path)
        info = subprocess.check_output(
            ["gdalinfo", "-stats", os.path.join(tmp_path, "mhw_04.tif")]
        ).decode("utf-8")
        print(info)
        assert "Origin = (172762.500000000000000,210637.500000000000000)" in info
        assert "STATISTICS_MAXIMUM=9" in info
        assert "STATISTICS_MINIMUM=0" in info

    def test_read_configuration(self, path_tests):
        config = path_tests / "small_simple.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.read_config_file(config)
        myniche.run(full_model=False)

    def test_run_configuration(self, path_tests):
        config = path_tests / "small_simple.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def test_run_configuration_numeric(self, path_tests):
        config = path_tests / "small_ct.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

    def test_incomplete_model(self, path_testdata):
        myniche = niche_vlaanderen.Niche()
        myniche.set_input("mhw", path_testdata / "small" / "msw.asc")
        with pytest.raises(NicheException):
            myniche.run()  # incomplete, keys are missing
        with pytest.raises(NicheException):
            myniche.write("_temp")  # should raise, no calculation done

    def test_mxw_validation(self, small_niche):
        myniche = small_niche
        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 0)

        with pytest.raises(NicheException):
            myniche.run(full_model=False)

        myniche.set_input("mhw", 5)
        myniche.set_input("mlw", 10)
        myniche.set_input("msw", 3)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

        myniche.set_input("mhw", 3)
        myniche.set_input("mlw", 5)
        myniche.set_input("msw", 10)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

        myniche.set_input("mhw", 3)
        myniche.set_input("mlw", 5)
        myniche.set_input("msw", 10)
        myniche.run(full_model=True, strict_checks=False)
        # should not raise

    def test_mxw_validation_yml(self, path_tests):
        myniche = niche_vlaanderen.Niche()
        # should not raise
        myniche.run_config_file(path_tests / "small_nostrict.yml")

        n2 = niche_vlaanderen.Niche()
        n2.read_config_file(path_tests / "small_nostrict.yml")
        with pytest.raises(NicheException):
            n2.run()

    def test_nitrogen_validation(self, small_niche):
        myniche = small_niche
        myniche.set_input("nitrogen_animal", 10001)
        with pytest.raises(NicheException):
            myniche.run(full_model=True)

    def test_run_configuration_abiotic(self, path_tests):
        config = path_tests / "small_abiotic.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

        config = path_tests / "small_abiotic_extra.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)

        # rerun with a file with missing abiotic values
        config = path_tests / "small_abiotic_invalid.yaml"
        myniche = niche_vlaanderen.Niche()
        with pytest.raises(NicheException):
            myniche.run_config_file(config)

    def test_rereadoutput(self, path_tests):
        """
        This tests checks if the output written by the model is a valid input
        for a new run
        """
        config = path_tests / "small_simple.yaml"
        myniche = niche_vlaanderen.Niche()
        myniche.run_config_file(config)
        myniche = niche_vlaanderen.Niche()

        shutil.copy("_output/log.txt", "log.txt")

        config = "log.txt"
        myniche2 = niche_vlaanderen.Niche()
        myniche2.run_config_file(config)

    def test_overwrite_code_table(self, path_testdata):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation=path_testdata / "bad_ct" / "one_vegetation.csv"
        )

        myniche.set_input("mhw", path_testdata / "small" / "mhw.asc")
        myniche.set_input("mlw", path_testdata / "small"/ "mlw.asc")
        myniche.set_input("soil_code",
                          path_testdata / "small" / "soil_code.asc")
        myniche.run(full_model=False)

        # we expect only one vegetation type, as the codetable has only one
        assert len(myniche.occurrence) == 1

        # we try to overwrite using a non existing key
        with pytest.raises(NicheException):
            myniche._set_ct("bla",
                            path_testdata / "bad_ct" / "one_vegetation.csv")

        # we try to overwrite using a non existing codetable
        with pytest.raises(NicheException):
            myniche._set_ct("ct_vegetation", "nonexisting")

        assert myniche._vegcode2name(1) == "Sphagno-Betuletum"

    def test_repr(self, small_niche):
        myniche = small_niche
        str_repr = myniche.__repr__()
        assert "# No model run completed." in str_repr
        myniche.run()
        str_repr = myniche.__repr__()
        assert "# No model run completed." not in str_repr

    def test_plot(self, small_niche):
        """
        Tests the plot method. Note that this only tests whether a plot is
        constructed. The actual content is not tested.
        """
        import matplotlib as mpl

        mpl.use("agg")

        import matplotlib.pyplot as plt

        plt.show = lambda: None

        myniche = small_niche

        # try plotting before running
        myniche.plot("mhw")
        myniche.run(deviation=True)
        myniche.plot("mhw")
        myniche.plot(1)
        myniche.name = "name"
        myniche.plot(1)
        myniche.plot("mhw_01")
        myniche.plot("nutrient_level")
        with pytest.raises(NicheException):
            myniche.plot("sinterklaas")

    def test_table(self, small_niche):
        myniche = small_niche

        with pytest.raises(NicheException):
            myniche.table

        myniche.run(full_model=False)
        res = myniche.table
        
        assert res.shape == (36, 3)

        area_expected = 7 * 6 * 25 * 25 * 28 / 10000
        area = np.sum(res["area_ha"])

        assert area == area_expected

        detailed = myniche._table(detail=True)

        # area in detailed table should equal normal table
        assert np.sum(res["area_ha"]) == np.sum(detailed["area_ha"])
        # area where vegetation is present must be soil+mxw suitable
        assert np.sum(res[res["presence"] == "present"]["area_ha"]) == np.sum(
            detailed[detailed["presence"] == "soil+mxw suitable"]["area_ha"]
        )

    def test_zonal_stats(self, path_testcase, zwarte_beek_niche):
        myniche = zwarte_beek_niche()
        myniche.run(full_model=False)
        vector = path_testcase / "zwarte_beek" / "input" / "study_area_l72.geojson"

        # there is only one polygon
        stats = myniche.zonal_stats(str(vector), outside=False)

        # we expect no data to be absent as the shape is a mask
        np.testing.assert_equal(np.all(stats.presence == "no data"), False)

        # which also means that present /not present should be equal to the
        # normal table
        table = myniche.table
        stats_sum = np.sum(stats.area_ha[(stats.presence == "present")])
        table_sum = np.sum(table.area_ha[(table.presence == "present")])
        assert table_sum == stats_sum

        stats = myniche.zonal_stats(str(vector))
        # we should have nodata areas now
        assert np.any(stats.presence == "no data")

        # these should have shapeid -1 and have area approx 15.16 ha
        subset = (
            (stats.presence == "no data")
            & (stats.vegetation == 7)
            & (stats.shape_id == -1)
        )
        result = np.sum(stats[(subset)]["area_ha"])
        result = np.round(result, 2)
        assert 15.16 == result

    def test_zonal_attribute(self, path_testcase, zwarte_beek_niche):
        myniche = zwarte_beek_niche()
        myniche.run(full_model=False)
        vector = path_testcase / "zwarte_beek" / "input" / "study_area_l72.geojson"

        # there is only one polygon
        stats = myniche.zonal_stats(str(vector), outside=False, attribute="OID")
        # we expect no data to be absent as the shape is a mask
        np.testing.assert_equal(np.all(stats.presence == "no data"), False)
        assert np.all(stats.OID == 0)

        # check what happens if we supply an unexisting attribute
        with pytest.raises(KeyError):
            myniche.zonal_stats(str(vector), outside=False, attribute="xyz")

        stats = myniche.zonal_stats(str(vector), outside=True, attribute="OID")
        print(stats.OID.unique())
        np.testing.assert_equal([0, -1], stats.OID.unique())

    def test_uint(self, path_testdata):
        myniche = niche_vlaanderen.Niche()

        myniche.set_input("mhw", path_testdata / "small" / "mhw.asc")
        myniche.set_input("mlw", path_testdata / "small" / "mlw.asc")
        myniche.set_input("soil_code",
                          path_testdata / "tif" / "soil_code.tif")
        myniche.run(full_model=False)

        # this dataset should contain one nodata cell
        df = myniche.table
        assert np.all(df[df.presence == "no data"]["area_ha"] == 0.0625)

    def test_overwrite_file(self, tmp_path, small_niche):
        myniche = small_niche
        myniche.run()
        myniche.write(tmp_path, detailed_files=True)
        # should raise: file already exists
        with pytest.raises(NicheException):
            myniche.write(tmp_path)

        # check that all necessary files are created
        with open(tmp_path / "log.txt") as log:
            res = yaml.safe_load(log)
        files_written = res["files_written"]
        # assert all files written actually exist

        for index in files_written:
            assert os.path.exists(files_written[index])

        shutil.rmtree(tmp_path)

    def test_overwrite_codetable_nonexisting(self):
        # assume error - file does not exist
        with pytest.raises(NicheException):
            niche_vlaanderen.Niche(ct_vegetation="nonexisting file")

    def test_overwrite_codetable(self, path_tests, path_testdata):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation=path_testdata / "bad_ct" / "one_vegetation_limited.csv",
            ct_acidity=path_testdata / "bad_ct" / "acidity_limited.csv",
            lnk_acidity=path_testdata / "bad_ct" / "lnk_acidity_limited.csv",
            ct_nutrient_level=path_testdata / "bad_ct" / "nutrient_level.csv",
        )
        myniche.read_config_file(path_tests / "small.yaml")
        myniche.run()

    def test_overwrite_codetable_nojoin(self, path_tests, path_testdata):
        # test should generate a warning
        myniche = niche_vlaanderen.Niche(
            ct_vegetation=path_testdata / "bad_ct" / "vegetation_noinnerjoin.csv"
        )
        myniche.read_config_file(path_tests / "small.yaml")
        with pytest.warns(UserWarning):
            myniche.run()


class TestNicheDelta:
    def test_simplevsfull_plot(self, path_tests):
        config = path_tests / "small_simple.yaml"
        simple = niche_vlaanderen.Niche()
        simple.run_config_file(config)

        config_full = path_tests / "small.yaml"
        full = niche_vlaanderen.Niche()
        full.run_config_file(config_full)

        delta = niche_vlaanderen.NicheDelta(simple, full)

        # as the full model always contains less than the simple model,
        # we can use this in a test
        df = delta.table
        assert 0 == df[df.presence == "only in model 2"].area_ha.sum()

        import matplotlib as mpl

        mpl.use("agg")

        import matplotlib.pyplot as plt

        plt.show = lambda: None

        delta.plot(5)
        delta.name = "vergelijking"
        delta.plot(5)

    def test_simplevsfull_write(self, tmp_path, path_tests):
        config = path_tests / "small_simple.yaml"
        simple = niche_vlaanderen.Niche()
        simple.run_config_file(config)

        config_full = path_tests / "small.yaml"
        full = niche_vlaanderen.Niche()
        full.run_config_file(config_full)

        delta = niche_vlaanderen.NicheDelta(simple, full)

        tmpsubdir = tmp_path / "new"
        delta.write(tmpsubdir)
        # check tempdir contains the vegetation and the abiotic files
        expected_files = [
            "D1.tif",
            "D2.tif",
            "D3.tif",
            "D4.tif",
            "D5.tif",
            "D6.tif",
            "D7.tif",
            "D8.tif",
            "D9.tif",
            "D10.tif",
            "D11.tif",
            "D12.tif",
            "D13.tif",
            "D14.tif",
            "D15.tif",
            "D16.tif",
            "D17.tif",
            "D18.tif",
            "D19.tif",
            "D20.tif",
            "D21.tif",
            "D22.tif",
            "D23.tif",
            "D24.tif",
            "D25.tif",
            "D26.tif",
            "D27.tif",
            "D28.tif",
            "legend_delta.csv",
            "delta_summary.csv",
        ]

        dir_listing = os.listdir(tmpsubdir)
        assert Counter(list(expected_files)) == Counter(list(dir_listing))

        delta.name = "vgl"
        delta.write(tmpsubdir)

        dir = os.listdir(tmpsubdir)
        assert 60 == len(dir)
        assert 30 == sum(f.startswith("vgl_") for f in dir)

    def test_differentvegsize(self, path_tests, path_testdata):
        myniche = niche_vlaanderen.Niche(
            ct_vegetation=path_testdata / "bad_ct" / "one_vegetation.csv"
        )

        myniche.set_input("mhw", path_testdata / "small" / "mhw.asc")
        myniche.set_input("mlw", path_testdata / "small" / "mlw.asc")
        myniche.set_input("soil_code",
                          path_testdata / "small" / "soil_code.asc")
        myniche.run(full_model=False)

        small = niche_vlaanderen.Niche()
        small.run_config_file(path_tests / "small.yaml")

        # we try to compare but both elements have different vegetations
        with pytest.raises(NicheException):
            niche_vlaanderen.NicheDelta(small, myniche)

    def testinvalidDelta(self, path_tests, zwarte_beek_niche):
        small = niche_vlaanderen.Niche()
        with pytest.raises(NicheException):
            # should fail as there is no extent yet
            niche_vlaanderen.NicheDelta(small, small)

        small.read_config_file(path_tests / "small_simple.yaml")
        with pytest.raises(NicheException):
            # should fail as the model has not yet been run
            niche_vlaanderen.NicheDelta(small, small)

        zwb = zwarte_beek_niche()
        zwb.run()
        small.run(full_model=False)
        # should fail due to different extent
        with pytest.raises(NicheException):
            niche_vlaanderen.NicheDelta(zwb, small)

    def test_overwrite_delta_file(self, tmp_path, small_niche):
        myniche = small_niche
        myniche.run(full_model=False)
        delta = niche_vlaanderen.NicheDelta(myniche, myniche)
        delta.write(tmp_path)
        # should raise: file already exists
        with pytest.raises(NicheException):
            delta.write(tmp_path)
        # should just warn
        delta.write(tmp_path, overwrite_files=True)
        # check that all files in log.txt actually exist

@image_comparison(
    baseline_images=["zwb12", "zwb12_full_legend"],
    remove_text=True, extensions=["svg"], tol=5
)
def test_niche_plot(path_testcase):
    """Test with limited legend for detail"""
    full = niche_vlaanderen.Niche()
    path = path_testcase / "zwarte_beek" / "input"
    full.set_input("mhw", path / "mhw.asc")
    full.set_input("mlw", path / "mlw.asc")
    full.set_input("msw", path / "msw.asc")
    full.set_input("soil_code", path / "soil_code.asc")
    full.set_input("nitrogen_animal", 0)
    full.set_input("nitrogen_fertilizer", 0)
    full.set_input("management", path / "management.asc")
    full.set_input("nitrogen_atmospheric", path / "nitrogen_atmospheric.asc")
    full.set_input("inundation_acidity", 0)
    full.set_input("inundation_nutrient", 0)
    full.set_input("rainwater", 0)
    full.set_input("seepage", 0)
    full.set_input("minerality", path / "minerality.asc")

    full.run()
    vegetation = 12

    plt.rcParams["figure.figsize"] = (20, 3)
    full.plot_detail(vegetation, limit_legend=True)

    # with full legend and title
    full.name = "zwb"
    full.plot_detail(vegetation, limit_legend=False)

    # asking something different than a vegetation key should raise
    with pytest.raises(NicheException):
        full.plot_detail("mhw")


@pytest.mark.skipif(
    shutil.which("gdalinfo") is None,
    reason="gdalinfo not available in the environment.",
)
def test_conductivity2minerality(tmp_path, path_testdata):
    niche_vlaanderen.conductivity2minerality(
        path_testdata / "small" / "conductivity.asc",
        str(tmp_path / "minerality.tif")
    )

    info = subprocess.check_output(
        ["gdalinfo", "-stats", str(tmp_path / "minerality.tif")]
    ).decode("utf-8")

    assert "STATISTICS_MAXIMUM=1" in info
    assert "STATISTICS_MINIMUM=0" in info
    assert "STATISTICS_STDDEV=0.5"
    assert "STATISTICS_MEAN=0.5"
