import pytest

from rekx._version import __version__
from rekx.cli import app

from .conftest import cli_runner

# def test_help_command(capfd):
#     app(['--help'])
#     out, err = capfd.readouterr()
#     assert "Usage:" in out
#     assert err == ""


def test_version(cli_runner):
    runner_result = cli_runner.invoke(app, ["--version"])
    print(f"CLI output {runner_result.output}")
    expected_output = f"rekx version {__version__}\n"  # Assuming standard output format
    assert runner_result.exit_code == 0
    assert expected_output == runner_result.output
