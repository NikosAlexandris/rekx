from .log import logger
import typer
from rekx.typer_parameters import OrderCommands
from typing_extensions import Annotated
from pathlib import Path
from rekx.typer_parameters import typer_argument_source_directory
from rekx.typer_parameters import typer_option_filename_pattern
from typing import List
from .models import XarrayVariableSet
from rekx.typer_parameters import typer_option_verbose
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from .progress import DisplayMode
from .progress import display_context
from rekx.hardcodings import check_mark
import json
import xarray as xr
from rich import print
from rekx.messages import NOT_IMPLEMENTED_CLI


# app = typer.Typer(
#     cls=OrderCommands,
#     add_completion=True,
#     add_help_option=True,
#     rich_markup_mode="rich",
#     help=f'Check for chunking shape consistency',
# )


# ReviewMe -- Reuse eventually detect_chunking_shapes_parallel() ?
# @app.command(
#     'consistency',
#     no_args_is_help=True,
#     help='Check for chunk size consistency along series of files in a format supported by Xarray',
# )
def check_chunk_consistency(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable_set: Annotated[XarrayVariableSet, typer.Option(help=f"{NOT_IMPLEMENTED_CLI}")] = XarrayVariableSet.all,
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
                            logger.debug(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')
                            # print(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')

        # logger.info(f"{check_mark} [green]All files are consistently shaped in[/green] {chunk_sizes} chunks")
        # print(f"{check_mark} [green]All files are consistently shaped :[/green] {chunk_sizes} chunks")
        print(f"{check_mark} [green]All files are consistently shaped![/green]")
        if verbose:
            from .print import print_chunking_shapes
            print_chunking_shapes(chunking_shapes=chunk_sizes)


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


# @app.command(
#     'consistency-json',
#     no_args_is_help=True,
#     help='Check for chunk size consistency along series of kerchunk reference files',
# )
def check_chunk_consistency_json(
    source_directory: Annotated[Path, typer_argument_source_directory],
    variable: Annotated[str, typer.Argument(help='Variable name to select from')],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    files = list(map(str, file_paths))
    logger.info(f"Files found in {source_directory}: {files}")

    # Use as a comparison reference the chunk sizes from the first file
    initial_chunk_sizes = get_chunk_sizes_from_json(files[0], variable)
    if not initial_chunk_sizes:
        logger.error(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        print(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        return

    all_match = True
    mode = DisplayMode(verbose)
    with display_context[mode]:
        for file in files[1:]:
            if not compare_chunk_sizes_json(file, variable, initial_chunk_sizes):
                all_match = False

    if all_match:
        logger.info(f"[green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks")
        print(f"{check_mark} [green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks")

    else:
        logger.warning("Not all files are chunked identically! Check the logs for details.")
        print(f"[red]Not all files are chunked identically![/red] [bold]Check the logs for details.[/bold]")
