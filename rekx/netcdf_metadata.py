import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Annotated, Dict, List, Optional, Tuple

from humanize import naturalsize
from netCDF4 import Dataset

from .constants import NOT_AVAILABLE, REPETITIONS_DEFAULT, VERBOSE_LEVEL_DEFAULT
from .log import logger
from .models import (
    XarrayVariableSet,
    select_netcdf_variable_set_from_dataset,
    select_xarray_variable_set_from_dataset,
)
from .select import read_performance
from .typer_parameters import (
    humanize_help,
    latitude_in_degrees_help,
    longitude_in_degrees_help,
    repetitions_help,
)


def get_netcdf_metadata(
    input_netcdf_path: Annotated[Path, "Path to the NetCDF file"],
    variable: Annotated[
        None | str, "Name of the variable to inspect, defaults to None"
    ] = None,
    variable_set: Annotated[
        XarrayVariableSet, "Set of variables to diagnose"
    ] = XarrayVariableSet.all,
    longitude: Annotated[float, "Longitude in degrees"] = 8,
    latitude: Annotated[float, "Latitude in degrees"] = 45,
    repetitions: Annotated[
        int, "Number of repetitions for read operation"
    ] = REPETITIONS_DEFAULT,
    humanize: Annotated[bool, "Flag to humanize file size"] = False,
) -> Tuple[dict, Path]:
    """
    Get the metadata of a single NetCDF file.

    Retrieve and report the metadata of a single NetCDF file, including :
    file name, file size, dimensions, shape, chunks, cache, data type, scale
    factor, offset, compression filter, compression level, shuffling
    and lastly the read time (required to retrieve data and load them in memory)
    for data variables.

    Parameters
    ----------
    input_netcdf_path: Path
        Path to the input NetCDF file
    variable: str
    variable : None | str, optional
        Name of the variable to query, by default None.
    variable_set : XarrayVariableSet, optional
        Set of variables to diagnose, by default XarrayVariableSet.all. See
        also docstring of XarrayVariableSet.
    longitude : float, optional
        The longitude of the location to read data
    latitude : float, optional
        The latitude of the location to read data
    repetitions : int, optional
        Number of repetitions for read operation, by default
        REPETITIONS_DEFAULT.
    humanize : bool, optional
        Flag to humanize file size nominally measured in bytes, by default
        False.

    Returns
    -------
    Tuple[dict, Path]
        A tuple containing a dictionary with the file metadata and the Path
        object of the NetCDF file.

    Raises
    ------
    FileNotFoundError
        If the specified NetCDF file does not exist.

    Examples
    --------
    Suppose we have a NetCDF file 'data.nc' in the current directory. To get its metadata, use:

    >>> from pathlib import Path
    >>> metadata, path = get_netcdf_metadata(Path('data.nc'))
    >>> print(metadata)
    { ...metadata output... }
    >>> print(path)
    Path('data.nc')

    This will output the metadata of the 'data.nc' file and the Path object.

    """
    if not input_netcdf_path.exists():
        raise FileNotFoundError(f"File not found: {input_netcdf_path}")

    with Dataset(input_netcdf_path, "r") as dataset:
        filesize = os.path.getsize(input_netcdf_path)  # in Bytes
        filesize = naturalsize(filesize, binary=True) if humanize else filesize
        metadata = {
            "File name": input_netcdf_path.name,
            "File size": filesize,
            "Dimensions": {
                dim: len(dataset.dimensions[dim]) for dim in dataset.dimensions
            },
            "Repetitions": repetitions,
        }
        selected_variables = select_netcdf_variable_set_from_dataset(
            XarrayVariableSet, variable_set, dataset
        )
        data_variables = select_netcdf_variable_set_from_dataset(
            XarrayVariableSet, "data", dataset
        )
        variables_metadata = {}
        for variable_name in selected_variables:
            variable = dataset[
                variable_name
            ]  # variable is not a simple string anymore!
            cache_metadata = variable.get_var_chunk_cache()
            variable_metadata = {
                "Shape": " x ".join(map(str, variable.shape)),
                "Chunks": " x ".join(map(str, variable.chunking()))
                if variable.chunking() != "contiguous"
                else "contiguous",
                "Cache": cache_metadata[0] if cache_metadata[0] else NOT_AVAILABLE,
                "Elements": cache_metadata[1] if cache_metadata[1] else NOT_AVAILABLE,
                "Preemption": cache_metadata[2] if cache_metadata[2] else NOT_AVAILABLE,
                "Type": str(variable.dtype),
                "Scale": getattr(variable, "scale_factor", NOT_AVAILABLE),
                "Offset": getattr(variable, "add_offset", NOT_AVAILABLE),
                "Compression": variable.filters()
                if "filters" in dir(variable)
                else NOT_AVAILABLE,
                "Level": NOT_AVAILABLE,
                "Shuffling": variable.filters().get("shuffle", NOT_AVAILABLE),
                "Read time": NOT_AVAILABLE,
            }
            variables_metadata[
                variable_name
            ] = variable_metadata  # Add info to variable_metadata
            if variable_name in data_variables:
                data_retrieval_time = read_performance(
                    time_series=input_netcdf_path,
                    variable=variable_name,
                    longitude=longitude,
                    latitude=latitude,
                    repetitions=repetitions,
                )
            else:
                data_retrieval_time = NOT_AVAILABLE
            variables_metadata[variable_name]["Read time"] = data_retrieval_time

    metadata["Variables"] = variables_metadata
    return metadata, input_netcdf_path


def get_multiple_netcdf_metadata(
    file_paths: List[Path],
    variable: str = None,
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
    longitude: Annotated[float, longitude_in_degrees_help] = 8,
    latitude: Annotated[float, latitude_in_degrees_help] = 45,
    repetitions: Annotated[int, repetitions_help] = REPETITIONS_DEFAULT,
    humanize: Annotated[bool, humanize_help] = False,
):
    """Get the metadata of multiple NetCDF files.

    Get and report the metadata of multiple NetCDF files, including :
    file name, file size, dimensions, shape, chunks, cache, type, scale,
    offset, compression, shuffling and lastly the read time (required to
    retrieve data) for data variables.

    Parameters
    ----------
    file_paths: List[Path]
        List of paths to the input NetCDF files
    variable: str
        Name of the variable to query
    variable_set: XarrayVariableSet
        Name of the set of variables to query. See also docstring of
        XarrayVariableSet
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    repetitions: int
        Number of repetitions for read operation
    humanize: bool
        Humanize measured quantities of bytes

    Returns
    -------
    metadata_series: dict
        A nested dictionary

    """
    metadata_series = {}
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                get_netcdf_metadata,
                file_path,
                variable,
                variable_set.value,
                longitude,
                latitude,
                repetitions,
                humanize,
            )
            for file_path in file_paths
        ]
        for future in as_completed(futures):
            try:
                metadata, input_netcdf_path = future.result()
                logger.info(f"Metadata : {metadata}")
                metadata_series[input_netcdf_path.name] = metadata
            except Exception as e:
                logger.error(f"Error processing file: {e}")

    return metadata_series
