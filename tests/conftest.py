import math
import os
from datetime import datetime, timedelta
from pathlib import Path

import netCDF4
import numpy as np
import pytest
from typer.testing import CliRunner

# (longitude, latitude)
EU_GEOMETRIC_CENTER_POST_BREXIT = (9.902056, 49.843)
LONGITUDE_LOW = math.floor(EU_GEOMETRIC_CENTER_POST_BREXIT[0])
LONGITUDE_HIGH = math.ceil(EU_GEOMETRIC_CENTER_POST_BREXIT[0])
LATITUDE_LOW = math.floor(EU_GEOMETRIC_CENTER_POST_BREXIT[1])
LATITUDE_HIGH = math.ceil(EU_GEOMETRIC_CENTER_POST_BREXIT[1])


runner = CliRunner()


@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def path_to_data(request):
    """
    Dynamically resolve and return the absolute path to 'tests/data'
    """
    module_directory = Path(os.path.dirname(os.path.abspath(request.module.__file__)))
    return module_directory


@pytest.fixture
def create_minimal_netcdf(
    path_to_data: Path,
    time: int = 48,
    lon: int = 9,
    lat: int = 9,
    time_chunk_size: int = 48,
    lon_chunk_size: int = 3,
    lat_chunk_size: int = 3,
):
    """
    Create a minimal NetCDF4 file for testing purposes
    """
    np.random.seed(43)  # Fix the random seed to ensure reproducibility

    # Create the netCDF file
    filename = path_to_data / "minimal_netcdf.nc"
    dataset = netCDF4.Dataset(filename, "w", format="NETCDF4")

    # Create the dimensions
    dataset.createDimension("time", time)
    dataset.createDimension("lon", lon)
    dataset.createDimension("lat", lat)

    # Additional global attributes
    dataset.institution = "Institution"
    dataset.source = "Source"
    dataset.contributors = "Contributors"
    dataset.contact = "Contact"
    dataset.platform = "Platform"
    dataset.processid = "Process ID"
    dataset.project_id = "Project ID"
    dataset.software = "Software"
    dataset.title = "Title"

    # Create the time variable
    time_var = dataset.createVariable("time", np.float64, ("time",))
    time_var.units = "hours since 1970-01-01 00:00:00"
    time_var.calendar = "standard"
    start_time = datetime(2023, 5, 23, 0, 0, 0)
    time_values = [start_time + timedelta(minutes=30 * h) for h in range(time)]
    time_var[:] = netCDF4.date2num(
        time_values, units=time_var.units, calendar=time_var.calendar
    )

    # Create the longitude and latitude variables
    lon_var = dataset.createVariable("lon", np.float32, ("lon",))
    lon_var.units = "degrees_east"
    # lon_var[:] = [LONGITUDE_LOW, LONGITUDE_HIGH]  # Set the longitude value
    lon_var[:] = np.linspace(LONGITUDE_LOW, LONGITUDE_HIGH, lon)

    lat_var = dataset.createVariable("lat", np.float32, ("lat",))
    lat_var.units = "degrees_north"
    # lat_var[:] = [LATITUDE_LOW, LATITUDE_HIGH]  # Set the latitude value
    lat_var[:] = np.linspace(LATITUDE_LOW, LATITUDE_HIGH, lat)

    # Assuming you want to specify chunk sizes for the temperature variable
    chunk_sizes = (
        time_chunk_size,
        lat_chunk_size,
        lon_chunk_size,
    )  # define your chunk sizes

    # Create the temperature variable with chunking
    temp_var = dataset.createVariable(
        "SIS", np.float32, ("time", "lat", "lon"), chunksizes=chunk_sizes
    )
    temp_var.units = "kWh"
    temp_var.long_name = "kWh"
    # temp_data = np.random.uniform(low=280.0, high=310.0, size=(time, lat, lon))  # Generate random temperature values
    temp_data = np.random.uniform(
        low=280.0, high=310.0, size=(time, lat, lon)
    )  # Generate random temperature values
    temp_var[:] = temp_data

    # Close the netCDF file
    dataset.close()

    return filename
