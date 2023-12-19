# from loguru import logger
import os
from netCDF4 import Dataset
import pandas as pd
import numpy as np
import xarray as xr
from typing_extensions import Annotated
from typing import List
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import as_completed
from rich import print
import typer
from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_option_filename_pattern
from .models import XarrayVariableSet
from .models import select_xarray_variable_set_from_dataset
from .models import select_netcdf_variable_set_from_dataset
from .typer_parameters import typer_option_csv
from .typer_parameters import typer_option_verbose
from .constants import VERBOSE_LEVEL_DEFAULT
from .progress import DisplayMode
from .progress import display_context
from .print import print_chunk_shapes_table
from .csv import write_nested_dictionary_to_csv
from .rich_help_panel_names import rich_help_panel_diagnose
from .print import print_common_chunk_layouts


def format_compression(compression_dict):
    if isinstance(compression_dict, dict):
        # Keep only keys with True values
        return ', '.join([key for key, value in compression_dict.items() if value])
    return compression_dict


def get_netcdf_metadata(
    input_netcdf_path: Path,
    variable: str = None,
    variable_set: Annotated[XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")] = XarrayVariableSet.all,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    if not os.path.exists(input_netcdf_path):
        return "File not found: " + input_netcdf_path

    with Dataset(input_netcdf_path, 'r') as dataset:
        metadata = {
            "File name": input_netcdf_path.name,
            "File size": os.path.getsize(input_netcdf_path),  # in Bytes
            "Dimensions": {
                dim: len(dataset.dimensions[dim]) for dim in dataset.dimensions
            },
        }
        variable_metadata = {}
        selected_variables = select_netcdf_variable_set_from_dataset(
            XarrayVariableSet, variable_set, dataset
        )
        for variable_name in selected_variables:
            variable = dataset[variable_name]  # variable is not a simple string anymore!
            data_retrieval_time = select_fast(
                    time_series=input_netcdf_path,
                    variable=variable_name,
                    longitude=8,
                    latitude=45,
                    )
            variable_metadata[variable_name] = {
                'Shape': ' x '.join(map(str, variable.shape)),
                'Chunks': ' x '.join(map(str, variable.chunking())),
                'Cache*': ' x '.join(map(str, variable.get_var_chunk_cache())),
                'Type': str(variable.dtype),
                'Scale': getattr(variable, 'scale_factor', '-'),
                'Offset': getattr(variable, 'add_offset', '-'),
                'Compression': variable.filters() if 'filters' in dir(variable) else '-',
                'Shuffling': getattr(variable, 'shuffle', '-'),
                'Read time': data_retrieval_time
            }
        metadata['Variables'] = variable_metadata

    if verbose:
        from .print import print_metadata_table
        print_metadata_table(metadata)

    return metadata, input_netcdf_path


def get_multiple_netcdf_metadata(
    file_paths: List[Path],
    variable: str = None,
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
    csv: Path = None,
    verbose: int = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    metadata_series = {}
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(
                get_netcdf_metadata,
                file_path,
                variable,
                variable_set.value,
            )
            for file_path in file_paths
        ]
        for future in as_completed(futures):
            try:
                metadata, input_netcdf_path = future.result()
                # logger.info(f"Scanned file: {input_netcdf_path}")
                metadata_series[input_netcdf_path.name] = metadata
            except Exception as e:
                logger.error(f"Error processing file: {e}")

    return metadata_series


from typing import Optional
def collect_netcdf_metadata(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable_set: Annotated[XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")] = XarrayVariableSet.all,
    group_metadata: Annotated[Optional[bool], 'Visually cluster rows of metadata per input NetCDF file and variable'] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Scan files in the source directory that match the pattern and diagnose the chunking shapes for each variable."""
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    mode = DisplayMode(verbose)
    with display_context[mode]:
        try:
            metadata_series = get_multiple_netcdf_metadata(
                    file_paths=file_paths,
                    variable_set=variable_set,
            )
            # print(f'Metadata series : {metadata_series}')
        except TypeError as e:
            raise ValueError("Error occurred:", e)

    # from .print import print_metadata_table
    # for metadata in metadata_series:
        # print_metadata_table(metadata_series)
    from .print import print_metadata_series_table
    print_metadata_series_table(
            metadata_series=metadata_series,
            group_metadata=group_metadata,
    )

    if csv:
        write_nested_dictionary_to_csv(
            nested_dictionary=metadata_series,
            output_filename=csv,
        )


def detect_chunking_shapes(
    file_path: Path,
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
):
    """Scan a single NetCDF file for chunking shapes per variable"""
    chunking_shapes = {}
    with xr.open_dataset(file_path, engine="netcdf4") as dataset:
        selected_variables = select_xarray_variable_set_from_dataset(
            XarrayVariableSet, variable_set, dataset
        )
        for variable in selected_variables:
            chunking_shape = dataset[variable].encoding.get("chunksizes")
            if chunking_shape and chunking_shape != "contiguous":
                chunking_shapes[variable] = chunking_shape

    return chunking_shapes, file_path.name


def detect_chunking_shapes_parallel(
    file_paths: List[Path],
    variable_set: XarrayVariableSet = XarrayVariableSet.all,
):
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
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(detect_chunking_shapes, file_path, variable_set.value)
            for file_path in file_paths
        ]

        for future in as_completed(futures):
            try:
                chunking_shapes, file_name = future.result()
                # logger.info(f"Scanned file: {file_name}")

                for variable, chunking_shape in chunking_shapes.items():
                    if variable not in aggregated_chunking_shapes:
                        aggregated_chunking_shapes[variable] = {}
                        # logger.info(
                        #     f"Initial chunk sizes set for {variable} in {file_name}"
                        # )
                    if chunking_shape not in aggregated_chunking_shapes[variable]:
                        aggregated_chunking_shapes[variable][chunking_shape] = set()
                        # logger.info(
                        #     f"New chunking shape {chunking_shape} found for variable {variable} in {file_name}"
                        # )
                    aggregated_chunking_shapes[variable][chunking_shape].add(file_name)

            except Exception as e:
                logger.error(f"Error processing file: {e}")

    return aggregated_chunking_shapes


# app = typer.Typer(
#     cls=OrderCommands,
#     add_completion=True,
#     add_help_option=True,
#     rich_markup_mode="rich",
#     help=f'Create kerchunk reference',
# )


# @app.command(
#     'shapes',
#     no_args_is_help=True,
#     help='Diagnose chunking shapes along series of files in a format supported by Xarray',
#     rich_help_panel=rich_help_panel_diagnose,
# )
def diagnose_chunking_shapes(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable_set: Annotated[XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")] = XarrayVariableSet.all,
    csv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Scan files in the source directory that match the pattern and diagnose the chunking shapes for each variable."""
    source_directory = Path(source_directory)
    file_paths = list(source_directory.glob(pattern))
    mode = DisplayMode(verbose)
    with display_context[mode]:
        try:
            chunking_shapes = detect_chunking_shapes_parallel(
                    file_paths=file_paths,
                    variable_set=variable_set,
            )
        except TypeError as e:
            raise ValueError("Error occurred:", e)
    print_chunk_shapes_table(chunking_shapes)#, highlight_variables)  : Idea

    if csv:
        write_nested_dictionary_to_csv(
            nested_dictionary=chunking_shapes,
            output_filename=csv,
        )


# @app.command(
#     'common-shape',
#     no_args_is_help=True,
#     help='Determine common chunking shape in multiple NetCDF files',
#     rich_help_panel=rich_help_panel_diagnose,
# )
def determine_common_chunking_layout(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    variable_set: Annotated[XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")] = XarrayVariableSet.all,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    source_directory = Path(source_directory)
    if not source_directory.exists() or not any(source_directory.iterdir()):
        print(f"[red]The directory [code]{source_directory}[/code] does not exist or is empty[/red].")
        return
    file_paths = list(source_directory.glob(pattern))
    if not file_paths:
        print(f"No files matching the pattern [code]{pattern}[/code] found in [code]{source_directory}[/code]!")
        return

    mode = DisplayMode(verbose)
    with display_context[mode]:
        chunking_shapes = detect_chunking_shapes_parallel(
                file_paths=file_paths,
                variable_set=variable_set,
                )
        common_chunking_shapes = {}
        for variable, shapes in chunking_shapes.items():
            import numpy as np
            max_shape = np.array(next(iter(shapes)), dtype=int)
            for shape in shapes:
                current_shape = np.array(shape, dtype=int)
                max_shape = np.maximum(max_shape, current_shape)
            common_chunking_shapes[variable] = tuple(max_shape)

        print_common_chunk_layouts(common_chunking_shapes)
        return common_chunking_shapes
