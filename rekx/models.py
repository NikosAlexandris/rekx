import enum
# from enum import Enum
from typing import Type
from typing import List
import xarray as xr
import netCDF4


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


def select_xarray_variable_set_from_dataset(
    xarray_variable_set: Type[enum.Enum],
    variable_set: List[enum.Enum],
    dataset: xr.Dataset,
):
    # Hardcoded ! ---------------------------------------------
    metadata_attributes = {'record_status'}
    coordinates_data_attributes = {'lat_bnds', 'lon_bnds'}
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

    else:
        raise ValueError("Invalid category")
