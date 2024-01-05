from .log import logger
import typer
from rekx.typer_parameters import OrderCommands
from pathlib import Path
import fsspec
from fsspec.implementations.reference import LazyReferenceMapper
from kerchunk.hdf import SingleHdf5ToZarr
import traceback
import multiprocessing
from functools import partial
from kerchunk.combine import MultiZarrToZarr
from typing import Optional
from typing_extensions import Annotated
from .typer_parameters import typer_option_verbose
from rekx.constants import REPETITIONS_DEFAULT
from .constants import VERBOSE_LEVEL_DEFAULT
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_option_filename_pattern
from .typer_parameters import typer_option_dry_run
from .typer_parameters import typer_argument_kerchunk_combined_reference
from .progress import DisplayMode
from .progress import display_context
import kerchunk
import xarray as xr
from .rich_help_panel_names import rich_help_panel_combine
from .rich_help_panel_names import rich_help_panel_reference
from .rich_help_panel_names import rich_help_panel_select
from .typer_parameters import typer_argument_longitude_in_degrees
from .typer_parameters import typer_argument_latitude_in_degrees
from .typer_parameters import typer_argument_timestamps
from .typer_parameters import typer_option_start_time
from .typer_parameters import typer_option_end_time
from .typer_parameters import typer_option_mask_and_scale
from .models import MethodForInexactMatches
from .typer_parameters import typer_option_neighbor_lookup
from .typer_parameters import typer_option_tolerance
from .typer_parameters import typer_option_repetitions
from .typer_parameters import typer_option_in_memory
from .typer_parameters import typer_option_statistics
from .typer_parameters import typer_option_csv
from .typer_parameters import typer_option_variable_name_as_suffix
from .typer_parameters import typer_option_rounding_places
from .constants import ROUNDING_PLACES_DEFAULT
from .constants import DEFAULT_RECORD_SIZE
import time as timer
from .utilities import set_location_indexers
from .messages import ERROR_IN_SELECTING_DATA
from rekx.hardcodings import exclamation_mark
from rekx.statistics import print_series_statistics
from .csv import to_csv
from typing import Any
from datetime import datetime
from rich import print


def create_parquet_store(
    input_file: Path,
    output_parquet_store: Path,
    record_size: int = DEFAULT_RECORD_SIZE,
):
    """ """
    log_messages = []
    log_messages.append('Logging execution of create_parquet_store()')
    output_parquet_store.mkdir(parents=True, exist_ok=True)

    try:
        log_messages.append(f'Creating a filesystem mapper for {output_parquet_store}')
        filesystem = fsspec.filesystem("file")
        output = LazyReferenceMapper.create(
            root=str(output_parquet_store),  # does not handle Path
            fs=filesystem,
            record_size=record_size,
        )
        log_messages.append(f'Created the filesystem mapper {output}')

        log_messages.append(f'Kerchunking the file {input_file}')
        single_zarr = SingleHdf5ToZarr(str(input_file), out=output)
        single_zarr.translate()
        log_messages.append(f'Kerchunked the file {input_file}')

    except Exception as e:
        print(f"Failed processing file [code]{input_file}[/code] : {e}")
        log_messages.append(f"Exception occurred: {e}")
        log_messages.append("Traceback (most recent call last):")
        
        tb_lines = traceback.format_exc().splitlines()
        for line in tb_lines:
            log_messages.append(line)

        raise

    finally:
        logger.info("\n".join(log_messages))

    logger.info(f'Returning a Parquet store : {output_parquet_store}')
    return output_parquet_store


def create_single_parquet_store(
    input_file_path,
    output_directory,
    record_size: int = DEFAULT_RECORD_SIZE,
    verbose: int = 0,
):
    """Helper function for create_multiple_parquet_stores()"""
    filename = input_file_path.stem
    single_parquet_store = output_directory / f"{filename}.parquet"
    create_parquet_store(
        input_file_path,
        output_parquet_store=single_parquet_store,
        record_size=record_size,
    )
    if verbose > 0:
        print(f'  [code]{single_parquet_store}[/code]')

    if verbose > 1:
        dataset = xr.open_dataset(
            str(single_parquet_store),
            engine='kerchunk',
            storage_options=dict(remote_protocol='file')
        )
        print(dataset)


def create_multiple_parquet_stores(
    source_directory: Path,
    output_directory: Path,
    pattern: str = "*.nc",
    record_size: int = DEFAULT_RECORD_SIZE,
    workers: int = 4,
    verbose: int = 0,
):
    """ """
    input_file_paths = list(source_directory.glob(pattern))
    # if verbose:
    #     print(f'Input file paths : {input_file_paths}')
    if not input_file_paths:
        print("No files found in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]!"
        )
        return
    output_directory.mkdir(parents=True, exist_ok=True)
    with multiprocessing.Pool(processes=workers) as pool:
        print(f'Creating the following Parquet stores in [code]{output_directory}[/code] : ')
        partial_create_parquet_references = partial(
            create_single_parquet_store,
            output_directory=output_directory,
            record_size=record_size,
            verbose=verbose,
        )
        pool.map(partial_create_parquet_references, input_file_paths)
    if verbose:
        print(f'Done!')


def combine_multiple_parquet_stores(
    source_directory: Path,
    output_parquet_store: Path,
    pattern: str = '*.parquet',
    record_size: Optional[int] = DEFAULT_RECORD_SIZE,
):
    output_parquet_store = output_parquet_store.parent / (output_parquet_store.name + '.parquet')
    output_parquet_store.mkdir(parents=True, exist_ok=True)
    filesystem = fsspec.filesystem("file")
    try:
        output = LazyReferenceMapper.create(
            root=str(output_parquet_store),
            fs=filesystem,
            record_size=record_size,
        )
        input_references = list(source_directory.glob(pattern))
        input_references = list(map(str, input_references))
        input_references.sort()
        multi_zarr = MultiZarrToZarr(
            input_references,
            remote_protocol="file",
            concat_dims=["time"],
            identical_dims= ["lat", "lon"],
            # coo_map={"time": "cf:time"},
            out=output,
        )
        multi_zarr.translate()
        output.flush()

    except Exception as e:
        print(f"Failed creating the [code]{output_parquet_store}[/code] : {e}!")
        import traceback
        traceback.print_exc()
        # return


# commands

def parquet_reference(
    input_file: Path,
    output_directory: Optional[Path] = '.',
    record_size: int = DEFAULT_RECORD_SIZE,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Create Parquet references from an HDF5/NetCDF file"""
    filename = input_file.stem
    output_parquet_store = output_directory / f'{filename}.parquet'

    if dry_run:
        print(f"[bold]Dry running operations that would be performed[/bold]:")
        print(
            f"> Creating Parquet references to [code]{input_file}[/code] in [code]{output_parquet_store}[/code]"
        )
        return  # Exit for a dry run

    create_parquet_store(
        input_file_path=input_file,
        output_directory=output_directory,
        record_size=record_size,
        verbose=verbose,
    )


def parquet_multi_reference(
    source_directory: Path,
    output_directory: Optional[Path] = '.',
    pattern: str = "*.nc",
    record_size: int = DEFAULT_RECORD_SIZE,
    workers: int = 4,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Create Parquet references from an HDF5/NetCDF file"""
    input_file_paths = list(source_directory.glob(pattern))

    if not input_file_paths:
        print("No files found in the source directory matching the pattern.")
        return

    if dry_run:
        print(
            f"[bold]Dry running operations that would be performed[/bold]:"
        )
        print(
            f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]"
        )
        print(f"> Number of files matched : {len(input_file_paths)}")
        print(f"> Creating Parquet stores in [code]{output_directory}[/code]")
        return  # Exit for a dry run

    create_multiple_parquet_stores(
        source_directory=source_directory,
        output_directory=output_directory,
        pattern=pattern,
        record_size=record_size,
        workers=workers,
        verbose=verbose,
    )


def combine_parquet_stores_to_parquet(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.parquet",
    combined_reference: Annotated[Path, typer_argument_kerchunk_combined_reference] = "combined_kerchunk.parquet",
    record_size: int = DEFAULT_RECORD_SIZE,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Run the command without making any changes.")] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Combine multiple Parquet stores into a single aggregate dataset using Kerchunk's `MultiZarrToZarr` function"""

    mode = DisplayMode(verbose)
    with display_context[mode]:

        source_directory = Path(source_directory)
        reference_file_paths = list(source_directory.glob(pattern))
        reference_file_paths = list(map(str, reference_file_paths))
        reference_file_paths.sort()

        if dry_run:
            print(f"[bold]Dry run[/bold] of [bold]operations that would be performed[/bold]:")
            print(f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]")
            print(f"> Number of files matched: {len(reference_file_paths)}")
            print(f"> Writing combined reference file to [code]{combined_reference}[/code]")
            return  # Exit for a dry run

        try:
            # Create LazyReferenceMapper to pass to MultiZarrToZarr
            combined_reference.mkdir(parents=True, exist_ok=True)
            print(f'Combined reference name : {combined_reference}')
            filesystem = fsspec.filesystem("file")
            from fsspec.implementations.reference import LazyReferenceMapper
            output_lazy = LazyReferenceMapper.create(
                    root=str(combined_reference),
                    fs=filesystem,
                    record_size=record_size,
            )

            # Combine single references
            from kerchunk.combine import MultiZarrToZarr
            mzz = MultiZarrToZarr(
                reference_file_paths,
                remote_protocol="file",
                concat_dims=["time"],
                identical_dims=["lat", "lon"],
                coo_map={"time": "cf:time"},
                out=output_lazy,
            )
            multifile_kerchunk = mzz.translate()
            output_lazy.flush()  # Write all non-full reference batches

        except Exception as e:
            print(f"Failed creating the [code]{combined_reference}[/code] : {e}!")
            import traceback
            traceback.print_exc()

        if verbose > 1:
            # Read from the Parquet storage
            # kerchunk.df.refs_to_dataframe(multifile_kerchunk, str(combined_reference))

            # filesystem = fsspec.implementations.reference.ReferenceFileSystem(
            #     fo=str(combined_reference),
            #     target_protocol='file',
            #     remote_protocol='file',
            #     lazy=True
            # )
            # ds = xr.open_dataset(
            #     filesystem.get_mapper(''),
            #     engine="zarr",
            #     chunks={},
            #     backend_kwargs={"consolidated": False},
            # )
            # print(ds)
            dataset = xr.open_dataset(
                str(combined_reference),  # does not handle Path
                engine="kerchunk",
                storage_options=dict(remote_protocol='file')
                # storage_options=dict(skip_instance_cache=True, remote_protocol="file"),
            )
            print(dataset)


def select_from_parquet(
    parquet_store: Annotated[Path, typer.Argument(..., help="Path to Parquet store")],
    variable: Annotated[str, typer.Argument(..., help='Variable name to select from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[Any], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    time: Annotated[Optional[int], typer.Option(help="New chunk size for the 'time' dimension")] = None,
    lat: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lat' dimension")] = None,
    lon: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lon' dimension")]= None,
    # convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    # output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """Select data from a Parquet store"""

    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    logger.debug(f'Command context : {print(typer.Context)}')

    data_retrieval_start_time = timer.time()
    logger.debug(f'Starting data retrieval... {data_retrieval_start_time}')

    # timer_start = timer.time()
    # mapper = fsspec.get_mapper(
    #     "reference://",
    #     fo=str(reference_file),
    #     remote_protocol="file",
    #     remote_options={"skip_instance_cache": True},
    # )
    # timer_end = timer.time()
    # logger.debug(f"Mapper creation took {timer_end - timer_start:.2f} seconds")
    timer_start = timer.time()
    dataset = xr.open_dataset(
        str(parquet_store),  # does not handle Path
        engine="kerchunk",
        storage_options=dict(skip_instance_cache=True, remote_protocol="file"),
        # backend_kwargs={"consolidated": False},
        # chunks=None,
        # mask_and_scale=mask_and_scale,
    )
    timer_end = timer.time()
    logger.debug(f"Dataset opening via Xarray took {timer_end - timer_start:.2f} seconds")

    available_variables = list(dataset.data_vars)
    if not variable in available_variables:
        print(f'The requested variable `{variable}` does not exist! Plese select one among the available variables : {available_variables}.')
        raise typer.Exit(code=0)
    else:
        timer_start = timer.time()
        time_series = dataset[variable]
        timer_end = timer.time()
        logger.debug(f"Data array variable selection took {timer_end - timer_start:.2f} seconds")

        timer_start = timer.time()
        chunks = {'time': time, 'lat': lat, 'lon': lon}
        time_series.chunk(chunks=chunks)
        timer_end = timer.time()
        logger.debug(f"Data array rechunking took {timer_end - timer_start:.2f} seconds")

    timer_start = timer.time()
    indexers = set_location_indexers(
        data_array=time_series,
        longitude=longitude,
        latitude=latitude,
        verbose=verbose,
    )
    timer_end = timer.time()
    logger.debug(f"Data array indexers setting took {timer_end - timer_start:.2f} seconds")
    
    try:
        timer_start = timer.time()
        location_time_series = time_series.sel(
            **indexers,
            method=neighbor_lookup,
            tolerance=tolerance,
        )
        timer_end = timer.time()
        logger.debug(f"Location selection took {timer_end - timer_start:.2f} seconds")

        if in_memory:
            timer_start = timer.time()
            location_time_series.load()  # load into memory for faster ... ?
            timer_end = timer.time()
            logger.debug(f"Location selection loading in memory took {timer_end - timer_start:.2f} seconds")

    except Exception as exception:
        print(f"{ERROR_IN_SELECTING_DATA} : {exception}")
        raise SystemExit(33)
    # ------------------------------------------------------------------------

    if start_time or end_time:
        timestamps = None  # we don't need a timestamp anymore!

        if start_time and not end_time:  # set `end_time` to end of series
            end_time = location_time_series.time.values[-1]

        elif end_time and not start_time:  # set `start_time` to beginning of series
            start_time = location_time_series.time.values[0]

        else:  # Convert `start_time` & `end_time` to the correct string format
            start_time = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_time = end_time.strftime('%Y-%m-%d %H:%M:%S')
    
        timer_start = timer.time()
        location_time_series = (
            location_time_series.sel(time=slice(start_time, end_time))
        )
        timer_end = timer.time()
        logger.debug(f"Time slicing with `start_time` and `end_time` took {timer_end - timer_start:.2f} seconds")

    if timestamps is not None and not start_time and not end_time:
        if len(timestamps) == 1:
            start_time = end_time = timestamps[0]
        
        try:
            timer_start = timer.time()
            location_time_series = (
                location_time_series.sel(time=timestamps, method=neighbor_lookup)
            )
            timer_end = timer.time()
            logger.debug(f"Time selection with `timestamps` took {timer_end - timer_start:.2f} seconds")

        except KeyError:
            print(f"No data found for one or more of the given {timestamps}.")

    if location_time_series.size == 1:
        timer_start = timer.time()
        single_value = float(location_time_series.values)
        warning = (
            f"{exclamation_mark} The selected timestamp "
            + f"{location_time_series.time.values}"
            + f" matches the single value "
            + f'{single_value}'
        )
        timer_end = timer.time()
        logger.debug(f"Single value conversion to float took {timer_end - timer_start:.2f} seconds")
        logger.warning(warning)
        if verbose > 0:
            print(warning)

    data_retrieval_end_time = timer.time()
    logger.debug(f"Data retrieval took {data_retrieval_end_time - data_retrieval_start_time:.2f} seconds")

    timer_start = timer.time()
    results = {
        location_time_series.name: location_time_series.to_numpy(),
    }
    timer_end = timer.time()
    logger.debug(f"Data series conversion to NumPy took {timer_end - timer_start:.2f} seconds")

    title = 'Location time series'
    
    # special case!
    if location_time_series is not None and timestamps is None:
        timer_start = timer.time()
        timestamps = location_time_series.time.to_numpy()
        timer_end = timer.time()
        logger.debug(f"Timestamps conversion to NumPy from Xarray's _time_ coordinate took {timer_end - timer_start:.2f} seconds")

    if statistics:  # after echoing series which might be Long!
        timer_start = timer.time()
        print_series_statistics(
            data_array=location_time_series,
            title='Selected series',
        )
        timer_end = timer.time()
        logger.debug(f"Printing statistics in the console took {timer_end - timer_start:.2f} seconds")

    if csv:
        timer_start = timer.time()
        to_csv(
            x=location_time_series,
            path=csv,
        )
        timer_end = timer.time()
        logger.debug(f"Exporting to CSV took {timer_end - timer_start:.2f} seconds")

    # return location_time_series


def read_from_parquet(
    parquet_store: Annotated[Path, typer.Argument(..., help="Path to Parquet store")],
    variable: Annotated[str, typer.Argument(..., help='Variable name to select from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """Time reading data over a location."""
    try:
        timings = []
        for _ in range(repetitions):
            data_retrieval_start_time = timer.perf_counter()
            with xr.open_dataset(
                str(parquet_store),  # does not handle Path
                engine="kerchunk",
                storage_options=dict(skip_instance_cache=True, remote_protocol="file"),
                # mask_and_scale=False,
            ) as dataset:
                _ = (
                    dataset[variable]
                    .sel(lon=longitude, lat=latitude, method="nearest", tolerance=tolerance)
                    .load()  # ensure reading data values !
                )
            timings.append(timer.perf_counter() - data_retrieval_start_time)
            # print(f'{dataset}')
        average_data_retrieval_time = sum(timings) / len(timings)
        if not verbose:
            print(f'{average_data_retrieval_time:.3f} seconds')
            # return average_data_retrieval_time
        else:
            print(f'[bold green]Data read in memory in[/bold green] : {average_data_retrieval_time:.3f} seconds :high_voltage::high_voltage:')
            print(f'{_}')

    except Exception as exception:
        print(f"{ERROR_IN_SELECTING_DATA} : {exception}")
        raise SystemExit(33)
