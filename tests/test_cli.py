from click.testing import CliRunner
import niche_vlaanderen.cli as nv_cli
import os
import rasterio
import numpy.testing
import numpy as np


def test_cli_no_param():
    expected = "No config file added. Use --help for more info\n"
    runner = CliRunner()
    result = runner.invoke(nv_cli.cli)
    assert result.output == expected


def test_cli_floodplain():
    runner = CliRunner()
    runner.invoke(nv_cli.cli, ['tests/flooding-codetables.yml'])

    import os
    print(os.getcwd())
    dir = os.listdir("_output")
    result_eerste = [f.startswith("eerste") for f in dir]
    assert sum(result_eerste) == 25

    with rasterio.open('_output/eerste-F20-T25-P1-winter.tif') as f:
        band = f.read(1)
        numpy.testing.assert_equal([-99, -1, 2, 3], np.unique(band))


def test_example_yml():
    runner = CliRunner()
    # the following returns the example yaml file, which we will test in the
    # next step
    result = runner.invoke(nv_cli.cli, ["--example"])
    # this is written to a file
    with open("tests/_example.yml", "w") as text_file:
        text_file.write(result.output)
    # which we run again
    result2 = runner.invoke(nv_cli.cli, ["tests/_example.yml"])
    assert "files_written:" in result2.output
    assert "mhw_25: " in result2.output


def test_get_version():
    runner = CliRunner()
    result = runner.invoke(nv_cli.cli, ["--version"])
    assert "niche_vlaanderen version: " in result.output
