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

    dir = os.listdir("_output")
    result_eerste = [f.startswith("eerste") for f in dir]
    assert sum(result_eerste) == 24
