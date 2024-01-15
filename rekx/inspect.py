from pathlib import Path
from typing import Annotated, Dict, List, Optional, Tuple

import typer

from .constants import REPETITIONS_DEFAULT, VERBOSE_LEVEL_DEFAULT
from .csv import write_metadata_dictionary_to_csv, write_nested_dictionary_to_csv
from .models import XarrayVariableSet
from .netcdf_metadata import get_multiple_netcdf_metadata, get_netcdf_metadata
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


def inspect_netcdf_data(
    input_path: Annotated[Path, typer_argument_input_path] = ".",
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable: str = None,
    variable_set: Annotated[
        XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")
    ] = XarrayVariableSet.all,
    long_table: Annotated[
        Optional[bool],
        "Group rows of metadata per input NetCDF file and variable in a long table",
    ] = True,
    group_metadata: Annotated[
        Optional[bool],
        "Visually cluster rows of metadata per input NetCDF file and variable",
    ] = False,
    longitude: Annotated[float, typer_argument_longitude_in_degrees] = 8,
    latitude: Annotated[float, typer_argument_latitude_in_degrees] = 45,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
    humanize: Annotated[bool, typer_option_humanize] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """Collect the metadata of a single or multiple NetCDF files.

    Scan the `source_directory` for files that match the given `pattern`,
    and collect their metadata, including : file name, file size, dimensions,
    shape, chunks, cache, type, scale, offset, compression, shuffling and
    lastly measure the time required to retrieve and load data variables (only)
    in memory.

    Parameters
    ----------
    input_path: Path
        A singe path or a list of paths to the input NetCDF data
    variable: str
        Name of the variable to query
    variable_set: XarrayVariableSet
        Name of the set of variables to query. See also docstring of
        XarrayVariableSet.
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    group_metadata: bool
        Visually group metadata records per input file by using empty lines
        in-between
    repetitions: int
        Number of repetitions for read operation
    humanize: bool
        Humanize measured quantities of bytes
    csv: Path
        Output file name for comma-separated values
    verbose: int
        Verbosity level

    Returns
    -------
    None
        This function does not return anything. It either prints out the
        results in the terminal or writes then in a CSV file if requested.

    """
    if input_path.is_file():
        metadata, _ = get_netcdf_metadata(
            input_netcdf_path=input_path,
            variable=variable,
            variable_set=variable_set,
            longitude=longitude,
            latitude=latitude,
            repetitions=repetitions,
            humanize=humanize,
        )
        if not csv:
            from .print import print_metadata_table

            print_metadata_table(metadata)
        if csv:
            write_metadata_dictionary_to_csv(
                dictionary=metadata,
                output_filename=csv,
            )
        return

    if input_path.is_dir():
        source_directory = Path(input_path)
        if not any(source_directory.iterdir()):
            print(f"[red]The directory [code]{source_directory}[/code] is empty[/red].")
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
                metadata_series = get_multiple_netcdf_metadata(
                    file_paths=file_paths,
                    variable_set=variable_set,
                    longitude=longitude,
                    latitude=latitude,
                    repetitions=repetitions,
                    humanize=humanize,
                )
            except TypeError as e:
                raise ValueError("Error occurred:", e)

        if csv:
            write_nested_dictionary_to_csv(
                nested_dictionary=metadata_series,
                output_filename=csv,
            )
            return

        if not long_table:
            from .print import print_metadata_series_table

            print_metadata_series_table(
                metadata_series=metadata_series,
                group_metadata=group_metadata,
            )
        else:
            from .print import print_metadata_series_long_table

            print_metadata_series_long_table(
                metadata_series=metadata_series,
                group_metadata=group_metadata,
            )
