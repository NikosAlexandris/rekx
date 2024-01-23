from pathlib import Path

import pytest

from rekx.netcdf_metadata import get_netcdf_metadata


def test_file_not_found():
    """Test if FileNotFoundError is raised for a non-existent file"""
    with pytest.raises(FileNotFoundError):
        get_netcdf_metadata(Path("/path/to/non/existent/file.nc"))


def test_metadata(path_to_data, create_minimal_netcdf):
    netcdf_file_path = path_to_data / create_minimal_netcdf
    metadata, path = get_netcdf_metadata(netcdf_file_path)
    assert isinstance(metadata, dict)
    assert "File name" in metadata
    assert "File size" in metadata
    assert "Dimensions" in metadata
    assert "Repetitions" in metadata
    assert isinstance(path, Path)
    # assert netcdf_file_path == path


variable = "SIS"


def test_specific_variable_metadata(
    path_to_data, create_minimal_netcdf, variable=variable
):
    netcdf_file_path = path_to_data / create_minimal_netcdf
    metadata, path = get_netcdf_metadata(netcdf_file_path, variable=variable)
    assert variable in metadata["Variables"]
    variable_metadata = metadata["Variables"][variable]
    assert "Shape" in variable_metadata
    assert "Chunks" in variable_metadata
    assert "Cache" in variable_metadata
