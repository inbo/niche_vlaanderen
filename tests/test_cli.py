from click.testing import CliRunner
import niche_vlaanderen.cli as nv_cli
import os
import pytest


def test_cli_no_param():
    expected = "No config file added. Use --help for more info\n"
    runner = CliRunner()
    result = runner.invoke(nv_cli.cli)
    assert result.output == expected


@pytest.mark.skipwindows27
def test_cli_floodplain():
    runner = CliRunner()

    result = runner.invoke(nv_cli.cli, ['tests/floodplain-codetables.yml'])

    expected_files = [
        'D1.tif', 'D2.tif', 'D3.tif', 'D4.tif', 'D5.tif', 'D6.tif',
        'D7.tif', 'D8.tif', 'D9.tif', 'D10.tif', 'D11.tif', 'D12.tif',
        'D13.tif', 'D14.tif', 'D15.tif', 'D16.tif', 'D17.tif', 'D18.tif',
        'D19.tif', 'D20.tif', 'D21.tif', 'D22.tif', 'D23.tif', 'D24.tif',
        'D25.tif', 'D26.tif', 'D27.tif', 'D28.tif']

    dir = os.listdir("_output")
    result_eerste = [f.startswith("eerste") for f in dir]
    assert sum(result_eerste) == 24
