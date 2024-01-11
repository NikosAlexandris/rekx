from pathlib import Path

import pytest

from rekx.diagnose import get_netcdf_metadata


def test_file_not_found():
    """Test if FileNotFoundError is raised for a non-existent file"""
    non_existent_file = Path("/path/to/non/existent/file.nc")
    with pytest.raises(FileNotFoundError):
        get_netcdf_metadata(non_existent_file)
