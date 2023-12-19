from devtools import debug
from rich import print
# import warnings
# import typer
# import netCDF4
# from .log import logger
# import xarray as xr
from pathlib import Path
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.models import MethodForInexactMatches
from rekx.hardcodings import exclamation_mark
from rekx.hardcodings import check_mark
# from rekx.hardcodings import x_mark
from rekx.messages import ERROR_IN_SELECTING_DATA


# def load_or_open_dataarray(function, filename_or_object, mask_and_scale):
#     try:
#         dataarray = function(
#             filename_or_obj=filename_or_object,
#             mask_and_scale=mask_and_scale,
#         )
#         return dataarray

#     except Exception as exc:
#         typer.echo(f"Could not load or open the data: {str(exc)}")
#         raise typer.Exit(code=33)


# def open_data_array(
#     netcdf: str,
#     mask_and_scale: bool = False,
#     in_memory: bool = False,
#     verbose: int = VERBOSE_LEVEL_DEFAULT,
# ):
#     """
#     """
#     # try:
#     #     if in_memory:
#     #         dataarray = xr.load_dataarray(
#     #                 filename_or_object=netcdf,
#     #                 mask_and_scale=mask_and_scale,
#     #                 )
#     #         return dataarray
#     # except Exception as exc:
#     #     typer.echo(f"Could not load the data in memory: {str(exc)}")
#     #     try:
#     #         dataarray = xr.open_dataarray(
#     #                 filename_or_object=netcdf,
#     #                 mask_and_scale=mask_and_scale,
#     #                 )
#     #         return dataarray
#     #     except Exception as exc:
#     #         typer.echo(f"Could not open the data: {str(exc)}")
#     #         raise typer.Exit(code=33)
#     if in_memory:
#         if verbose > 0:
#             print("Reading data in memory...")
#         return load_or_open_dataarray(
#             function=xr.load_dataarray,
#             filename_or_object=netcdf,
#             mask_and_scale=mask_and_scale,
#         )
#     else:
#         if verbose > 0:
#             print("Open file")
#         return load_or_open_dataarray(
#             function=xr.open_dataarray,
#             filename_or_object=netcdf,
#             mask_and_scale=mask_and_scale,
#         )


def get_scale_and_offset(netcdf):
    """Get scale and offset values from a netCDF file"""
    dataset = netCDF4.Dataset(netcdf)
    netcdf_dimensions = set(dataset.dimensions)
    netcdf_dimensions.update({'lon', 'longitude', 'lat', 'latitude'})  # all space dimensions?
    netcdf_variables = set(dataset.variables)
    variable = str(list(netcdf_variables.difference(netcdf_dimensions))[0])  # single variable name!

    if 'scale_factor' in dataset[variable].ncattrs():
        scale_factor = dataset[variable].scale_factor
    else:
        scale_factor = None

    if 'add_offset' in dataset[variable].ncattrs():
        add_offset = dataset[variable].add_offset
    else:
        add_offset = None

    return (scale_factor, add_offset)


def set_location_indexers(
    data_array,
    longitude: float = None,  # Longitude = None,
    latitude: float = None,  # Latitude = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Select single pair of coordinates from a data array
    
    Will select center coordinates if none of (longitude, latitude) are
    provided.
    """
    # ----------------------------------------------------------- Deduplicate me
    # Ugly hack for when dimensions 'longitude', 'latitude' are not spelled out!
    # Use `coords` : a time series of a single pair of coordinates has only a `time` dimension!
    indexers = {}
    dimensions = [dimension for dimension in data_array.coords if isinstance(dimension, str)]
    if set(['lon', 'lat']) & set(dimensions):
        x = 'lon'
        y = 'lat'
    elif set(['longitude', 'latitude']) & set(dimensions):
        x = 'longitude'
        y = 'latitude'

    if (x and y):
        logger.info(f'Dimensions  : {x}, {y}')

    if not (longitude and latitude):
        warning = f'{exclamation_mark} Coordinates (longitude, latitude) not provided. Selecting center coordinates.'
        logger.warning(warning)
        print(warning)

        center_longitude = float(data_array[x][len(data_array[x])//2])
        center_latitude = float(data_array[y][len(data_array[y])//2])
        indexers[x] = center_longitude
        indexers[y] = center_latitude

        text_coordinates = f'{check_mark} Center coordinates (longitude, latitude) : {center_longitude}, {center_latitude}.'

    else:
        indexers[x] = longitude
        indexers[y] = latitude
        text_coordinates = f'{check_mark} Coordinates : {longitude}, {latitude}.'

    logger.info(text_coordinates)
    
    if verbose > 0:
        print(text_coordinates)

    if verbose == 3:
        debug(locals())
    
    return indexers


# def select_coordinates(
#     data_array,
#     longitude: float = None,  # Longitude = None,
#     latitude: float = None,  # Latitude = None,
#     time: str = None,
#     method: str ='nearest',
#     tolerance: float = 0.1,
#     verbose: int = VERBOSE_LEVEL_DEFAULT,
# ):
#     """Select single pair of coordinates from a data array
    
#     Will select center coordinates if none of (longitude, latitude) are
#     provided.
#     """
#     indexers = set_location_indexers(
#         data_array=data_array,
#         longitude=longitude,
#         latitude=latitude,
#         verbose=verbose,
#     )

#     try:
#         if not time:
#             data_array = data_array.sel(
#                     **indexers,
#                     method=method,
#                     )
#         else:
#             # Review-Me ------------------------------------------------------
#             data_array = data_array.sel(
#                     time=time, method=method).sel(
#                         **indexers,
#                         method=method,
#                         tolerance=tolerance,
#                     )
#             # Review-Me ------------------------------------------------------

#     except Exception as exception:
#         print(f"{x_mark} {ERROR_IN_SELECTING_DATA} : {exception}")
#         raise SystemExit(33)

#     return data_array


def select_location_time_series(
    time_series: Path = None,
    longitude: float = None,  # Longitude = None,
    latitude: float = None,  # Latitude = None,
    mask_and_scale: bool = False,
    neighbor_lookup: MethodForInexactMatches = MethodForInexactMatches.nearest,
    tolerance: float = 0.1,
    in_memory: bool = False,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """Select a location from a time series dataset format supported by
    xarray"""
    data_array = open_data_array(
        time_series,
        mask_and_scale,
        in_memory,
    )
    indexers = set_location_indexers(
        data_array=data_array,
        longitude=longitude,
        latitude=latitude,
        verbose=verbose,
    )
    try:
        location_time_series = data_array.sel(
            **indexers,
            method=neighbor_lookup,
            tolerance=tolerance,
        )
        location_time_series.load()  # load into memory for fast processing

    except Exception as exception:
        print(f"{ERROR_IN_SELECTING_DATA} : {exception}")
        raise SystemExit(33)

    if verbose == 3:
        debug(locals())

    return location_time_series
