import netCDF4
import pytest

# import xarray
print(netCDF4.__version__)


def test_minimal_netcdf_file(path_to_data, create_minimal_netcdf):
    netcdf_file_path = path_to_data / create_minimal_netcdf
    with netCDF4.Dataset(netcdf_file_path, "r") as dataset:
        expected_variable = "SIS"
        expected_time_size = 48
        expected_lat_size = 9
        expected_lon_size = 9
        expected_shape = (
            expected_time_size,
            expected_lat_size,
            expected_lon_size,
        )
        expected_chunksize = (48, 3, 3)

        assert expected_variable in dataset.variables
        assert expected_shape == dataset[expected_variable].shape
        assert expected_chunksize == (48, 3, 3)

        assert expected_time_size == dataset.dimensions["time"].size
        assert expected_lat_size == dataset.dimensions["lon"].size
        assert expected_lon_size == dataset.dimensions["lat"].size

        # xarray.open_dataset('minimal_netcdf.nc')['SIS'].encoding['chunksizes']
