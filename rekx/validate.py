from devtools import debug
from .log import logger
from typing_extensions import Annotated
from typing import Any
from typing import Optional
from datetime import datetime
from threading import Lock
import typer
from pathlib import Path
from typing_extensions import Annotated
from rekx.typer_parameters import OrderCommands
from rekx.typer_parameters import typer_argument_source_directory
from rekx.typer_parameters import typer_argument_output_directory
from rekx.typer_parameters import typer_argument_kerchunk_combined_reference
from rekx.typer_parameters import typer_option_filename_pattern
from rekx.typer_parameters import typer_option_number_of_workers
# from rekx.typer_parameters import typer_argument_longitude_in_degrees
# from rekx.typer_parameters import typer_argument_latitude_in_degrees
from rekx.typer_parameters import typer_option_time_series
from rekx.typer_parameters import typer_argument_timestamps
from rekx.typer_parameters import typer_option_start_time
from rekx.typer_parameters import typer_option_end_time
from rekx.typer_parameters import typer_option_convert_longitude_360
from rekx.typer_parameters import typer_option_mask_and_scale
from rekx.typer_parameters import typer_option_tolerance
from rekx.typer_parameters import typer_option_in_memory
from rekx.typer_parameters import typer_option_statistics
from rekx.typer_parameters import typer_option_rounding_places
from rekx.typer_parameters import typer_option_csv
from rekx.typer_parameters import typer_option_variable_name_as_suffix
from rekx.typer_parameters import typer_option_verbose
from rekx.select import select_time_series
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.utilities import set_location_indexers
from rekx.models import MethodsForInexactMatches
from rekx.statistics import print_series_statistics

import kerchunk
import fsspec
import multiprocessing
import json
import ujson

from kerchunk.hdf import SingleHdf5ToZarr
from rich import print
from colorama import Fore
from colorama import Style
from rekx.hardcodings import exclamation_mark
from rekx.hardcodings import check_mark
from rekx.hardcodings import x_mark
from rekx.messages import ERROR_IN_SELECTING_DATA
from rekx.progress import DisplayMode
from rekx.progress import display_context
import hashlib
import xarray as xr
import netCDF4 as nc

import timeit
import dask  # type: ignore
import xarray as xr
from pathlib import Path
from typing import Dict, Union
import typer


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f'Create kerchunk reference',
)


@app.command(
    'consistency',
    no_args_is_help=True,
    help='Check for chunk size consistency along series of files in a format supported by Xarray',
)
def check_chunk_consistency(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    files = list(map(str, file_paths))

    mode = DisplayMode(verbose)
    with display_context[mode]:
        chunk_sizes = {}  # dictionary to store chunk sizes of first file
        for file in files:
            with xr.open_dataset(file, engine="netcdf4") as dataset:
                if not chunk_sizes:  # populate with chunk sizes
                    for variable in dataset.variables:
                        if dataset[variable].encoding.get("chunksizes"):
                            chunk_sizes[variable] = dataset[variable].encoding["chunksizes"]
                        logger.debug(f'File : {file}, Chunks : {chunk_sizes}')
                else:
                    # For subsequent files, check if chunk sizes match the initial ones
                    for variable in dataset.variables:
                        if (
                            dataset[variable].encoding.get("chunksizes")
                            and chunk_sizes.get(variable)
                            != dataset[variable].encoding["chunksizes"]
                        ):
                            raise ValueError(
                                f"Chunk size mismatch in file '{file}' for variable '{variable}'. Expected {chunk_sizes[variable]} but got {dataset[variable].encoding['chunksizes']}"
                            )
                        else:
                            logger.debug(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')

    print("All files have consistent chunk sizes!")


def get_chunk_sizes_from_json(file_path, variable):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            json_string = data['refs'].get(f'{variable}/.zarray')
            if not json_string:
                logger.warning(f"'{variable}/.zarray' not found in file {file_path}. Skipping...")
                return {}
            chunks_string = json.loads(json_string)
            chunk_sizes = {variable: chunks_string.get("chunks")}
            logger.info(f'File : {file_path}, Variable: {variable}, Chunk sizes: {chunk_sizes}')
            return chunk_sizes
    except Exception as e:
        logger.error(f"Error processing file {file_path}: {e}")
        return {}


def compare_chunk_sizes_json(
    file,
    variable,
    initial_chunk_sizes,
):
    logger.info(f'Comparing file {file}')
    current_chunk_sizes = get_chunk_sizes_from_json(file, variable)
    mismatched_vars = [(variable, size) for variable, size in current_chunk_sizes.items() if initial_chunk_sizes.get(variable) != size]
    if mismatched_vars:
        var, size = mismatched_vars[0]
        expected_size = initial_chunk_sizes[var]
        logger.error(f"Chunk size mismatch in file {file} for variable {var}. Expected {expected_size} but got {size}")
        return False
    else:
        # logger.info('Chunk sizes match!')
        return True


@app.command(
    'consistency-json',
    no_args_is_help=True,
    help='Check for chunk size consistency along series of Kerchunk JSON reference files [reverse red]Merge With [code]consistency[/code] command[/reverse red]',
)
def check_chunk_consistency_json(
    source_directory: Annotated[Path, typer_argument_source_directory],
    variable: Annotated[str, typer.Argument(help='Variable name to select from')] = None,
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    files = list(map(str, file_paths))

    # Use as a comparison reference the chunk sizes from the first file
    initial_chunk_sizes = get_chunk_sizes_from_json(files[0], variable)
    if not initial_chunk_sizes:
        logger.error(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        return

    all_match = True
    mode = DisplayMode(verbose)
    with display_context[mode]:
        for file in files[1:]:
            if not compare_chunk_sizes_json(file, variable, initial_chunk_sizes):
                all_match = False

    if all_match:
        logger.info("All files have consistent chunk sizes!")
        print("All files have consistent chunk sizes!")

    else:
        logger.warning("Some files have inconsistent chunk sizes. Check the logs for details.")
        print("Some files have inconsistent chunk sizes. Check the logs for details.")


@app.command(
    'common-layout',
    no_args_is_help=True,
    help='Determine common chunking layout in multiple Xarray-supported files [reverse yellow]Explain-Me Better![/reverse yellow]',
)
def determine_common_chunk_layout(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    source_directory = Path(source_directory)
    netcdf_file_paths = list(source_directory.glob(pattern))
    netcdf_files = list(map(str, netcdf_file_paths))

    mode = DisplayMode(verbose)
    with display_context[mode]:
        chunking_layouts = []
        for netcdf_file in netcdf_files:
            import netCDF4
            with netCDF4.Dataset(netcdf_file) as ncfile:
                for variable_name, variable in ncfile.variables.items():
                    if variable.chunking():
                        chunking_layouts.append(variable.chunking())
    
        import numpy as np
        common_chunking_layout = np.max(np.array(chunking_layouts), axis=0)
    
    return tuple(common_chunking_layout)


@app.command(
    'modify-chunk-size',
    no_args_is_help=True,
    help='Modify metadata on chunk size in NetCDF files [reverse red]Review-Me[/reverse red]',
)
def modify_chunk_size(
    netcdf_file,
    variable,
    chunk_size,
):
    """
    Modify the chunk size of a variable in a NetCDF file.
    
    Parameters:
    - nc_file: path to the NetCDF file
    - variable_name: name of the variable to modify
    - new_chunk_size: tuple specifying the new chunk size, e.g., (2600, 2600)
    """
    with nc.Dataset(netcdf_file, 'r+') as ds:
        var = ds.variables[variable]
        
        if var.chunking() != [None]:
            var.set_auto_chunking(chunk_size)
            print(f"Modified chunk size for variable '{variable}' in file '{netcdf_file}' to {chunk_size}.")

        else:
            print(f"Variable '{variable}' in file '{netcdf_file}' is not chunked. Skipping.")


if __name__ == "__main__":
    app()
