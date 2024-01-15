from pathlib import Path

import pytest

from rekx.netcdf_metadata import get_netcdf_metadata


def test_file_not_found():
    """Test if FileNotFoundError is raised for a non-existent file"""
    with pytest.raises(FileNotFoundError):
        get_netcdf_metadata("/path/to/non/existent/file.nc")


def test_metadata():
    input_file = Path("test_data.nc")
    metadata, path = get_netcdf_metadata(input_file)
    assert isinstance(metadata, dict)
    assert "File name" in metadata
    assert "File size" in metadata
    assert "Dimensions" in metadata
    assert "Repetitions" in metadata
    assert isinstance(path, Path)
    assert path == input_file


def test_specific_variable_metadata(variable):
    input_file = Path("test_data.nc")
    variable_name = variable
    metadata, path = get_netcdf_metadata(input_file, variable=variable_name)
    assert variable_name in metadata["Variables"]
    variable_metadata = metadata["Variables"][variable_name]
    assert "Shape" in variable_metadata
    assert "Chunks" in variable_metadata
    assert "Cache" in variable_metadata
