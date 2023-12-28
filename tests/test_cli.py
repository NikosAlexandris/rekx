import pytest
from typer.testing import CliRunner
from rekx.cli import app


runner = CliRunner()


# def test_help_command(capfd):
#     app(['--help'])
#     out, err = capfd.readouterr()
#     assert "Usage:" in out
#     assert err == ""


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Rekx CLI Version: 1.0.0" in result.output
