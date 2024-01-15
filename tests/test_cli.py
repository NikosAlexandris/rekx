import pytest
from typer.testing import CliRunner

from rekx.cli import app

runner = CliRunner()


# def test_help_command(capfd):
#     app(['--help'])
#     out, err = capfd.readouterr()
#     assert "Usage:" in out
#     assert err == ""


hardcoded_version = "rekx version 0.0.10.dev8+g005852e.d20240115"


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert hardcoded_version in result.output
