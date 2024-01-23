from pathlib import Path

import pytest

from rekx.diagnose import detect_chunking_shapes


def test_detect_chunking_shapes_file_not_found():
    """Test if FileNotFoundError is raised for a non-existent file"""
    with pytest.raises(FileNotFoundError):
        detect_chunking_shapes(Path("/path/to/non/existent/file.nc"))


def test_detect_chunking_shapes(path_to_data, create_minimal_netcdf):
    netcdf_input_file = path_to_data / create_minimal_netcdf
    chunking_shapes, file_name = detect_chunking_shapes(netcdf_input_file)

    assert isinstance(chunking_shapes, dict)
    assert isinstance(file_name, str)
