# from loguru import logger
# logger.remove()
# logger.add("kerchunking_{time}.log")#, compression="tar.gz")
from typing_extensions import Annotated
from typing import Any
from typing import Optional
from datetime import datetime
# from devtools import debug
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
from rekx.constants import ROUNDING_PLACES_DEFAULT
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.utilities import set_location_indexers
from rekx.models import MethodsForInexactMatches
from rekx.statistics import print_series_statistics
from rekx.print import print_chunk_shapes_table
from rekx.print import print_common_chunk_layouts

import kerchunk
import fsspec
import multiprocessing
import json
import ujson

from kerchunk.hdf import SingleHdf5ToZarr
from rich import print
from rekx.hardcodings import exclamation_mark
from rekx.hardcodings import check_mark
from rekx.hardcodings import x_mark
from rekx.messages import ERROR_IN_SELECTING_DATA
from rekx.messages import NOT_IMPLEMENTED_CLI
from rekx.messages import TO_MERGE_WITH_SINGLE_VALUE_COMMAND
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


from concurrent.futures import ProcessPoolExecutor, as_completed
import xarray as xr


def detect_chunking_shapes(file_path):
    """Scan a single NetCDF file for chunking shapes per variable"""
    chunking_shapes = {}
    with xr.open_dataset(file_path, engine="netcdf4") as dataset:
        for variable in dataset.variables:
            chunking_shape = dataset[variable].encoding.get("chunksizes")
            if chunking_shape and chunking_shape != "contiguous":
                chunking_shapes[variable] = chunking_shape

    return chunking_shapes, file_path.name


def detect_chunking_shapes_parallel(file_paths):
    """
    Detect and aggregate the chunking shapes of variables within a set of NetCDF files in parallel.

    Parameters
    ----------
    file_paths : list of Path
        A list of file paths pointing to the NetCDF files to be scanned.

    Returns
    -------
    dict
        A nested dictionary where the first level keys are variable names, and the
        second level keys are the chunking shapes encountered, with the associated
        values being sets of file names where those chunking shapes are found.
    """
    aggregated_chunking_shapes = {}

    # Use a ProcessPoolExecutor to parallelize file processing
    with ProcessPoolExecutor() as executor:
        futures = [executor.submit(detect_chunking_shapes, file_path) for file_path in file_paths]

        for future in as_completed(futures):
            try:
                chunking_shapes, file_name = future.result()
                # logger.info(f"Scanned file: {file_name}")

                for variable, chunking_shape in chunking_shapes.items():
                    if variable not in aggregated_chunking_shapes:
                        aggregated_chunking_shapes[variable] = {}
                        # logger.info(
                            # f"Initial chunk sizes set for {variable} in {file_name}"
                        # )
                    if chunking_shape not in aggregated_chunking_shapes[variable]:
                        aggregated_chunking_shapes[variable][chunking_shape] = set()
                        # logger.info(
                            # f"New chunking shape {chunking_shape} found for variable {variable} in {file_name}"
                        # )
                    aggregated_chunking_shapes[variable][chunking_shape].add(file_name)

            except Exception as e:
                # logger.error(f"Error processing file: {e}")
                print(f"Error processing file: {e}")

    return aggregated_chunking_shapes

                    


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
    if not files: 
        print(f'[red]No files matching[/red] [code]{pattern}[/code] [red]found in[/red] [code]{source_directory}[/code]')
        return

    mode = DisplayMode(verbose)
    with display_context[mode]:
        chunk_sizes = {}  # dictionary to store chunk sizes of first file
        for file in files:
            with xr.open_dataset(file, engine="netcdf4") as dataset:
                if not chunk_sizes:  # populate with chunk sizes
                    for variable in dataset.variables:
                        if dataset[variable].encoding.get("chunksizes"):
                            chunk_sizes[variable] = dataset[variable].encoding["chunksizes"]
                        # logger.debug(f'File : {file}, Chunks : {chunk_sizes}')
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
                            # logger.debug(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')
                            print(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')

        # logger.info(f"{check_mark} [green]All files are consistently shaped in[/green] {chunk_sizes} chunks")
        print(f"{check_mark} [green]All files are consistently shaped[/green] :")


def get_chunk_sizes_from_json(file_path, variable):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            json_string = data['refs'].get(f'{variable}/.zarray')
            if not json_string:
                # logger.warning(f"'{variable}/.zarray' not found in file {file_path}. Skipping...")
                return {}
            chunks_string = json.loads(json_string)
            chunk_sizes = {variable: chunks_string.get("chunks")}
            # logger.info(f'File : {file_path}, Variable: {variable}, Chunk sizes: {chunk_sizes}')
            return chunk_sizes

    except Exception as e:
        # logger.error(f"Error processing file {file_path}: {e}")
        return {}


def compare_chunk_sizes_json(
    file,
    variable,
    initial_chunk_sizes,
):
    # logger.info(f'Comparing file {file}')
    current_chunk_sizes = get_chunk_sizes_from_json(file, variable)
    mismatched_vars = [(variable, size) for variable, size in current_chunk_sizes.items() if initial_chunk_sizes.get(variable) != size]
    if mismatched_vars:
        var, size = mismatched_vars[0]
        expected_size = initial_chunk_sizes[var]
        # logger.error(f"Chunk size mismatch in file {file} for variable {var}. Expected {expected_size} but got {size}")
        return False
    else:
        # logger.info('Chunk sizes match!')
        return True


@app.command(
    'consistency-json',
    no_args_is_help=True,
    help='Check for chunk size consistency along series of kerchunk reference files',
)
def check_chunk_sizes_json(
    source_directory: Annotated[Path, typer_argument_source_directory],
    variable: Annotated[str, typer.Argument(help='Variable name to select from')],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    files = list(map(str, file_paths))
    # logger.info(f"Files found in {source_directory}: {files}")

    # Use as a comparison reference the chunk sizes from the first file
    initial_chunk_sizes = get_chunk_sizes_from_json(files[0], variable)
    if not initial_chunk_sizes:
        # logger.error(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        print(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        return

    all_match = True
    mode = DisplayMode(verbose)
    with display_context[mode]:
        for file in files[1:]:
            if not compare_chunk_sizes_json(file, variable, initial_chunk_sizes):
                all_match = False

    if all_match:
        # logger.info(f"[green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks")
        print(f"{check_mark} [green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks")

    else:
        # logger.warning("Not all files are chunked identically! Check the logs for details.")
        print(f"[red]Not all files are chunked identically![/red] [bold]Check the logs for details.[/bold]")


@app.command(
    'modify-chunk-size',
    no_args_is_help=True,
    help=f'Modify chunk size in NetCDF files {NOT_IMPLEMENTED_CLI}',
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
