from functools import partial
import multiprocessing
from .log import logger
from rich import print
from pathlib import Path
import xarray as xr
import typer
from .utilities import set_location_indexers
from typing_extensions import Annotated
from .typer_parameters import (
    typer_argument_time_series,
    typer_argument_source_directory,
    typer_option_filename_pattern,
    typer_option_output_filename,
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
    typer_option_mask_and_scale,
    typer_option_dry_run,
    typer_option_verbose,
)
from rekx.constants import (
    MASK_AND_SCALE_FLAG_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from .messages import ERROR_IN_SELECTING_DATA


def clip_netcdf_file(
    input_file: Annotated[Path, typer_argument_time_series],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    max_longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    max_latitude: Annotated[float, typer_argument_latitude_in_degrees],
    output_filename: Annotated[
        Path|None, typer_option_output_filename
    ] = None,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    Clip a NetCDF file to a specified geographic region.

    Parameters
    ----------
    input_file : Path
        Path to the input NetCDF file.
    longitude : float
        Minimum longitude of the region to clip.
    max_longitude : float
        Maximum longitude of the region to clip.
    latitude : float
        Minimum latitude of the region to clip.
    max_latitude : float
        Maximum latitude of the region to clip.
    output_filename : Path, optional
        Path to the output NetCDF file. If None, no file will be saved.
        Defaults to None.
    mask_and_scale : bool, optional
        Whether to mask and scale the data. Defaults to MASK_AND_SCALE_FLAG_DEFAULT.
    verbose : int, optional
        Verbosity level. Defaults to VERBOSE_LEVEL_DEFAULT.

    Raises
    ------
    SystemExit
        If an error occurs during the clipping process.
    ValueError
        If the output file extension is not supported.

    Notes
    -----
    The clipped data will be saved to the specified output file if provided.

    """
    try:
        with xr.open_dataset(
                input_file,
                mask_and_scale=mask_and_scale,
                ) as netcdf:
            indexers = set_location_indexers(
                data_array=netcdf,
                longitude=slice(longitude, max_longitude),
                latitude=slice(latitude, max_latitude),
                verbose=verbose,
            )
            area_time_series = netcdf.sel(
                **indexers,
                # tolerance=tolerance,
            )
            output_handlers = {
                ".nc": lambda area_time_series, output_filename: 
                    area_time_series.to_netcdf(
                        output_filename,
                        # engine="h5netcdf",
                    ),
            }
            if output_filename:
                if output_filename.exists():
                    if not overwrite:
                        warnings.warn(f"The output file '{output_filename}' already exists. It will not be overwritten.")
                        logger.warning(f"The output file '{output_filename}' already exists. It will not be overwritten.")
                        return  # Exit the function without writing the file
                    else:
                        logger.info(f"Overwriting the existing file '{output_filename}'.")
                extension = output_filename.suffix.lower()
                if extension in output_handlers:
                    output_handlers[extension](area_time_series, output_filename)
                else:
                    raise ValueError(f"Unsupported file extension: {extension}")
    
        logger.debug(f"Clipped data saved to {output_filename}")

    except Exception as exception:
        logger.error(f"{ERROR_IN_SELECTING_DATA} : {exception}")
        print(f"{ERROR_IN_SELECTING_DATA} : {exception}")
        # return "-"
        raise SystemExit(33)


def clip_netcdf_file_cli(
    source_directory: Annotated[Path, typer_argument_source_directory],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    max_longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    max_latitude: Annotated[float, typer_argument_latitude_in_degrees],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    output_directory: Annotated[Path|None,  typer.Option(help="Directory to save the clipped NetCDF files.")] = ".",
    output_filename_suffix: Annotated[str, typer.Option(help="Suffix to append to the output filename.")] = "",
    workers: Annotated[int, typer.Option(help="Number of worker processes.")] = 4,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    mask_and_scale: Annotated[
        bool, typer_option_mask_and_scale
    ] = MASK_AND_SCALE_FLAG_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    """
    input_file_paths = list(source_directory.glob(pattern))
    if not input_file_paths:
        logger.error(
            "No files found in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]!"
        )
        return

    if dry_run:
        print(f"[bold]Dry running operations that would be performed[/bold]:")
        print(
            f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]"
        )
        print(f"> Number of files matched : {len(input_file_paths)}")
        print(f"> Writing clipped NetCDF files in [code]{output_directory}[/code]")
        return  # Exit for a dry run

    output_directory.mkdir(parents=True, exist_ok=True)
    with multiprocessing.Pool(processes=workers) as pool:
        print(
            f"Clipping the following NetCDF files in [code]{output_directory}[/code] : "
        )
        args_list = [
            (
                input_file_path, 
                longitude, 
                max_longitude, 
                latitude, 
                max_latitude, 
                output_directory / f"{input_file_path.stem}_{output_filename_suffix}.nc", 
                mask_and_scale, 
                verbose
            ) 
            for input_file_path in input_file_paths
        ]
        pool.starmap(clip_netcdf_file, args_list)


    if verbose:
        print(f"Done!")
