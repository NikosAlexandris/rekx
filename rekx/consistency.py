import json
from pathlib import Path
from typing import List

import typer
import xarray as xr
from rich import print
from typing_extensions import Annotated

from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.hardcodings import check_mark
from rekx.messages import NOT_IMPLEMENTED_CLI
from rekx.typer_parameters import (
    OrderCommands,
    typer_argument_source_directory,
    typer_option_filename_pattern,
    typer_option_verbose,
)

from .log import logger
from .models import XarrayVariableSet
from .progress import DisplayMode, display_context


def get_chunk_sizes_from_json(file_path, variable):
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            json_string = data["refs"].get(f"{variable}/.zarray")
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
    mismatched_vars = [
        (variable, size)
        for variable, size in current_chunk_sizes.items()
        if initial_chunk_sizes.get(variable) != size
    ]
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
    variable: Annotated[str, typer.Argument(help="Variable name to select from")],
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
        logger.error(
            f"Cannot read chunk sizes from initial file {files[0]}. Exiting..."
        )
        print(f"Cannot read chunk sizes from initial file {files[0]}. Exiting...")
        return

    all_match = True
    mode = DisplayMode(verbose)
    with display_context[mode]:
        for file in files[1:]:
            if not compare_chunk_sizes_json(file, variable, initial_chunk_sizes):
                all_match = False

    if all_match:
        logger.info(
            f"[green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks"
        )
        print(
            f"{check_mark} [green]All files are consistently shaped in[/green] {initial_chunk_sizes[variable]} chunks"
        )

    else:
        logger.warning(
            "Not all files are chunked identically! Check the logs for details."
        )
        print(
            f"[red]Not all files are chunked identically![/red] [bold]Check the logs for details.[/bold]"
        )
