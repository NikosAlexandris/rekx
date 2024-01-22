import pytest
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture
def cli_runner():
    return CliRunner()
