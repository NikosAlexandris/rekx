import enum
# from enum import Enum
from typing import Type
from typing import List
import xarray as xr
import netCDF4
from pathlib import Path


class MethodForInexactMatches(str, enum.Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


class XarrayVariableSet(str, enum.Enum):
    all = 'all'
    coordinates = 'coordinates'
    coordinates_without_data = 'coordinates-without-data'
    data = 'data'
    metadata = 'metadata'
    time = 'time'


def select_xarray_variable_set_from_dataset(
    xarray_variable_set: Type[enum.Enum],
    variable_set: List[enum.Enum],
    dataset: xr.Dataset,
):
    """
    Select user-requested set of variables from an Xarray dataset.

    Parameters
    ----------
    xarray_variable_set: enum.Enum
        The Enum model to use for selection

    variable_set: List[enum.Enum]
        The user-requested sets of variables to select based on the Enum model

    dataset: xr.Dataset
        The input Xarray dataset from which to extract the user-requested
        variables

    Returns
    -------


    Examples
    --------


    Notes
    -----
    Is quasi-identical to the function
    select_netcdf_variable_set_from_dataset() with differences in terms of the
    names of attributes. See also docstring of other function.
    """
    # Hardcoded ! ---------------------------------------------
    metadata_attributes = {'record_status'}
    coordinates_data_attributes = {'lat_bnds', 'lon_bnds'}
    time_coordinate = {'time'}
    variables_attributes = set(dataset.variables)
    coordinates_attributes = set(dataset.coords)
    data_attributes = set(dataset.data_vars) - coordinates_data_attributes - metadata_attributes
    # --------------------------------------------- Hardcoded !

    if variable_set == xarray_variable_set.all:
        return variables_attributes

    elif variable_set == xarray_variable_set.coordinates:
        return coordinates_attributes
    
    elif variable_set == xarray_variable_set.coordinates_without_data:
        return coordinates_attributes - coordinates_data_attributes
    
    elif variable_set == xarray_variable_set.data:
        # return data - coordinates_data - metadata
        return data_attributes - coordinates_data_attributes - metadata_attributes
    
    elif variable_set == xarray_variable_set.metadata:
        return metadata_attributes.intersection(variables_attributes)
    
    elif variable_set == xarray_variable_set.time:
        return time_coordinate
    
    else:
        raise ValueError("Invalid category")


def select_netcdf_variable_set_from_dataset(
    netcdf4_variable_set: Type[enum.Enum],
    variable_set: List[enum.Enum],
    dataset: netCDF4.Dataset,
):
    """
    The same Enum model for both : netcdf4_variable_set and xarray_variable_set
    """
    metadata_attributes = {'record_status', 'bnds'}
    coordinates_data_attributes = {'lat_bnds', 'lon_bnds'}
    time_coordinate = {'time'}
    dimensions_attributes = set(dataset.dimensions)  # no `coordinates` via netCDF4
    variables_attributes = set(dataset.variables)
    data_attributes = variables_attributes - dimensions_attributes - coordinates_data_attributes - metadata_attributes

    if variable_set == netcdf4_variable_set.all:
        return variables_attributes

    elif variable_set == netcdf4_variable_set.coordinates:
        return dimensions_attributes  # Same as next one ?
    
    elif variable_set == netcdf4_variable_set.coordinates_without_data:
        return dimensions_attributes
    
    elif variable_set == netcdf4_variable_set.data:
        return data_attributes
    
    elif variable_set == netcdf4_variable_set.metadata:
        return metadata_attributes.intersection(variables_attributes)
    
    elif variable_set == netcdf4_variable_set.time:
        return time_coordinate

    else:
        raise ValueError("Invalid category")


class FileFormat(enum.Enum):
    NETCDF = '.nc'
    PARQUET = '.parquet'
    JSON = '.json'

    def open_dataset_options(self) -> dict:
        if self == FileFormat.NETCDF:
            # Default options for other formats
            return {"mask_and_scale": False}
        if self == FileFormat.JSON:
            return {
                "engine": "zarr",
                "backend_kwargs": {
                    "consolidated": False,
                },
                "chunks": None,
                "mask_and_scale": False,
            }
        if self == FileFormat.PARQUET:
            return {
                "engine": "kerchunk",
                "storage_options": {
                    "skip_instance_cache": True,
                    "remote_protocol": "file",
                },
            }

    def dataset_select_options(self, tolerance) -> dict:
        if self == FileFormat.PARQUET:
            return {"tolerance": tolerance}
        else:
            # Default or no additional options for other formats
            return {}


def get_file_format(file_path: Path) -> FileFormat:
    """
    Get the format from the filename extension.
    """
    file_extension = file_path.suffix.lower()
    return FileFormat(file_extension)
