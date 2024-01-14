from pathlib import Path
from typing import Annotated, Dict, List, Optional, Tuple

import typer
from rich import print

from rekx.hardcodings import check_mark, x_mark

from .constants import NOT_AVAILABLE, REPETITIONS_DEFAULT, VERBOSE_LEVEL_DEFAULT
from .csv import write_nested_dictionary_to_csv
from .diagnose import detect_chunking_shapes_parallel
from .models import (
    XarrayVariableSet,
    select_netcdf_variable_set_from_dataset,
    select_xarray_variable_set_from_dataset,
)
from .print import (
    print_chunk_shapes_table,
    print_chunking_shapes_consistency_validation_long_table,
    print_common_chunk_layouts,
)
from .progress import DisplayMode, display_context
from .typer_parameters import (
    OrderCommands,
    typer_argument_input_path,
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
    typer_argument_source_directory,
    typer_option_csv,
    typer_option_filename_pattern,
    typer_option_humanize,
    typer_option_repetitions,
    typer_option_verbose,
)


def diagnose_chunking_shapes(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable_set: Annotated[
        XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")
    ] = XarrayVariableSet.all,
    validate_consistency: Annotated[bool, typer.Option(help="")] = False,
    common_shapes: Annotated[
        bool, typer.Option(help="Report common maximum chunking shape")
    ] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Diagnose the chunking shapes of multiple Xarray-supported files.

    Scan the `source_directory` for Xarray-supported files that match
    the given `pattern` and diagnose the chunking shapes for each variable
    or determine the maximum common chunking shape across the input data.

    Parameters
    ----------
    source_directory: Path
        The source directory to scan for files matching the `pattern`
    pattern: str
        The filename pattern to match files
    variable_set: XarrayVariableSet
        Name of the set of variables to query. See also docstring of
        XarrayVariableSet
    verbose: int
        Verbosity level

    Returns
    -------
    # common_chunking_shapes: dict
    #     A dictionary with the common maximum chunking shapes for each variable
    #     identified in the input data.

    """
    source_directory = Path(source_directory)
    if not source_directory.exists() or not any(source_directory.iterdir()):
        print(
            f"[red]The directory [code]{source_directory}[/code] does not exist or is empty[/red]."
        )
        return
    file_paths = list(source_directory.glob(pattern))
    if not file_paths:
        print(
            f"No files matching the pattern [code]{pattern}[/code] found in [code]{source_directory}[/code]!"
        )
        return

    mode = DisplayMode(verbose)
    with display_context[mode]:
        try:
            chunking_shapes = detect_chunking_shapes_parallel(
                file_paths=file_paths,
                variable_set=variable_set,
            )
        except TypeError as e:
            raise ValueError("Error occurred:", e)

    if validate_consistency:
        inconsistent_variables = {}
        for variable, shapes in chunking_shapes.items():
            if len(shapes) > 1:
                inconsistent_variables[variable] = {
                    shape: list(files) for shape, files in shapes.items()
                }

        if inconsistent_variables:
            validation_message = f"{x_mark} [bold red]Variables are not consistently shaped across all files![/bold red]"
        else:
            validation_message = f"{check_mark} [green]Variables are consistently shaped across all files![/green]"
        if not verbose:
            print(validation_message)
            return
        else:
            print(validation_message)
            print_chunking_shapes_consistency_validation_long_table(
                inconsistent_variables
            )
            return

    if common_shapes:
        common_chunking_shapes = {}
        for variable, shapes in chunking_shapes.items():
            import numpy as np

            max_shape = np.array(next(iter(shapes)), dtype=int)
            for shape in shapes:
                current_shape = np.array(shape, dtype=int)
                max_shape = np.maximum(max_shape, current_shape)
            common_chunking_shapes[variable] = tuple(max_shape)

        print_common_chunk_layouts(common_chunking_shapes)
        # return common_chunking_shapes

    print_chunk_shapes_table(chunking_shapes)  # , highlight_variables)  : Idea
    if csv:
        write_nested_dictionary_to_csv(
            # nested_dictionary=chunking_shapes,
            nested_dictionary=chunking_shapes
            if not common_shapes
            else common_chunking_shapes,
            output_filename=csv,
        )


# Previous code for what `shapes --validate` is doing now ! ------------------

# def check_chunk_consistency(
#     source_directory: Annotated[Path, typer_argument_source_directory],
#     pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
#     variable_set: Annotated[
#         XarrayVariableSet, typer.Option(help=f"{NOT_IMPLEMENTED_CLI}")
#     ] = XarrayVariableSet.all,
#     verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
# ):
#     """ """
#     source_directory = Path(source_directory)
#     file_paths = list(source_directory.glob(pattern))
#     files = list(map(str, file_paths))
#     if not files:
#         print(
#             f"[red]No files matching[/red] [code]{pattern}[/code] [red]found in[/red] [code]{source_directory}[/code]"
#         )
#         return

#     mode = DisplayMode(verbose)
#     with display_context[mode]:
#         chunk_sizes = {}  # dictionary to store chunk sizes of first file
#         for file in files:
#             with xr.open_dataset(file, engine="netcdf4") as dataset:
#                 if not chunk_sizes:  # populate with chunk sizes
#                     for variable in dataset.variables:
#                         if dataset[variable].encoding.get("chunksizes"):
#                             chunk_sizes[variable] = dataset[variable].encoding[
#                                 "chunksizes"
#                             ]
#                         # logger.debug(f'File : {file}, Chunks : {chunk_sizes}')
#                 else:
#                     # For subsequent files, check if chunk sizes match the initial ones
#                     for variable in dataset.variables:
#                         if (
#                             dataset[variable].encoding.get("chunksizes")
#                             and chunk_sizes.get(variable)
#                             != dataset[variable].encoding["chunksizes"]
#                         ):
#                             raise ValueError(
#                                 f"Chunk size mismatch in file '{file}' for variable '{variable}'. Expected {chunk_sizes[variable]} but got {dataset[variable].encoding['chunksizes']}"
#                             )
#                         else:
#                             logger.debug(
#                                 f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}'
#                             )
#                             # print(f'Variable : {variable}, Chunks : {dataset[variable].encoding["chunksizes"]}')

#         # logger.info(f"{check_mark} [green]All files are consistently shaped in[/green] {chunk_sizes} chunks")
#         # print(f"{check_mark} [green]All files are consistently shaped :[/green] {chunk_sizes} chunks")
#         print(f"{check_mark} [green]All files are consistently shaped![/green]")
#         if verbose:
#             from .print import print_chunking_shapes

#             print_chunking_shapes(chunking_shapes=chunk_sizes)

# ------------------ Previous code for what `shapes --validate` is doing now !
