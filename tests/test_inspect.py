from typer.testing import CliRunner

from rekx.cli import app

runner = CliRunner()


def test_app():
    print(app)
    result = runner.invoke(app, ["inspect", "netcdf4_file.nc"])
    assert result.exit_code == 0
