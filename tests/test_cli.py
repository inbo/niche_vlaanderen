from click.testing import CliRunner
import niche_vlaanderen.cli as nv_cli
import os

def test_cli_no_param():
    expected = "No config file added. Use --help for more info\n"
    runner = CliRunner()
    result = runner.invoke(nv_cli.cli)
    assert result.output == expected
