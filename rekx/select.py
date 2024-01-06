from devtools import debug
from .log import logger
from .log import print_log_messages
from typing import Any
from typing import Optional
from datetime import datetime
from pathlib import Path
from rekx.constants import DATASET_SELECT_TOLERANCE_DEFAULT
from rekx.constants import REPETITIONS_DEFAULT
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.utilities import select_location_time_series
from rekx.models import MethodForInexactMatches
from rekx.utilities import get_scale_and_offset
from rekx.hardcodings import exclamation_mark
from rekx.hardcodings import check_mark
from rekx.hardcodings import x_mark
import typer
from typing import Any
from typing import Optional
from datetime import datetime
from threading import Lock
import typer
from pathlib import Path
from typing_extensions import Annotated
from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_argument_output_directory
from .typer_parameters import typer_argument_kerchunk_combined_reference
from .typer_parameters import typer_option_filename_pattern
from .typer_parameters import typer_option_number_of_workers
from .typer_parameters import typer_argument_longitude_in_degrees
from .typer_parameters import typer_argument_latitude_in_degrees
from .typer_parameters import typer_option_time_series
from .typer_parameters import typer_option_list_variables
from .typer_parameters import typer_argument_time_series
from .typer_parameters import typer_argument_timestamps
from .typer_parameters import typer_option_start_time
from .typer_parameters import typer_option_end_time
from .typer_parameters import typer_option_convert_longitude_360
from .typer_parameters import typer_option_mask_and_scale
from .typer_parameters import typer_option_neighbor_lookup
from .typer_parameters import typer_option_tolerance
from .typer_parameters import typer_option_repetitions
from .typer_parameters import typer_option_in_memory
from .typer_parameters import typer_option_statistics
from .typer_parameters import typer_option_rounding_places
from .typer_parameters import typer_option_csv
from .typer_parameters import typer_option_variable_name_as_suffix
from .typer_parameters import typer_option_verbose
from .constants import ROUNDING_PLACES_DEFAULT
from .constants import VERBOSE_LEVEL_DEFAULT
from .utilities import set_location_indexers
from .statistics import print_series_statistics
from .csv import to_csv
import kerchunk
import fsspec
import multiprocessing
import ujson
from kerchunk.hdf import SingleHdf5ToZarr
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)
from rich import print
from .hardcodings import exclamation_mark
from .hardcodings import check_mark
from .hardcodings import x_mark
from .messages import ERROR_IN_SELECTING_DATA
import xarray as xr
from .progress import DisplayMode
from .progress import display_context
import time as timer


def read_performance(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer.Argument(help='Variable to select data from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[Optional[float], typer_option_tolerance] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
) -> str:
    """
    Count the time to read and load data over a geographic location from an
    Xarray-supported file format.

    Returns
    -------
    data_retrieval_time : float or None ?
        The time it took to retrieve data over the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps.

    """
    from .models import get_file_format
    file_format = get_file_format(time_series)
    open_dataset_options = file_format.open_dataset_options()
    dataset_select_options = file_format.dataset_select_options(tolerance)
    try:
        timings = []
        for _ in range(repetitions):
            data_retrieval_start_time = timer.perf_counter()

            with xr.open_dataset(str(time_series), **open_dataset_options) as dataset:
                _ = (
                    dataset[variable]
                    .sel(
                        lon=longitude,
                        lat=latitude,
                        method="nearest",
                        **dataset_select_options,
                    )
                    .load()
                )
            timings.append(timer.perf_counter() - data_retrieval_start_time)

        average_data_retrieval_time = sum(timings) / len(timings)
        return f"{average_data_retrieval_time:.3f}"

    except Exception as exception:
        print(f"Cannot open [code]{variable}[/code] from [code]{time_series}[/code] via Xarray: {exception}")
        # raise SystemExit(33)
        return '-'


def read_performance_cli(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer.Argument(help='Variable to select data from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[Optional[float], typer_option_tolerance] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> str:
    """
    Count the time to read and load data over a geographic location from an
    Xarray-supported file format.

    Returns
    -------
    data_retrieval_time : float or None ?
        The time it took to retrieve data over the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps.

    """
    average_data_retrieval_time = read_performance(
            time_series=time_series,
            variable=variable,
            longitude=longitude,
            latitude=latitude,
            tolerance=tolerance,
            repetitions=repetitions,
            )
    if not verbose:
        print(average_data_retrieval_time)
    else:
        print(
            f"[bold green]Data read in memory in[/bold green] : {result} :high_voltage::high_voltage:"
        )
        print(f"{_}")


def select_fast(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer.Argument(help='Variable to select data from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    time_series_2: Annotated[Path, typer_option_time_series] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    # in_memory: Annotated[bool, typer_option_in_memory] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    tocsv: Annotated[Path, typer_option_csv] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Bare timing to read data over a location and optionally write
    comma-separated values.

    Returns
    -------
    data_retrieval_time : float
        The time it took to retrieve data over the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps.

    """
    try:
        data_retrieval_start_time = timer.perf_counter()#time()
        series = xr.open_dataset(time_series, mask_and_scale=False)[variable].sel(
            lon=longitude, lat=latitude, method="nearest"
        )
        if time_series_2:
            series_2 = xr.open_dataset(time_series_2, mask_and_scale=False)[variable].sel(
                lon=longitude, lat=latitude, method="nearest"
            )
        if csv:
            series.to_pandas().to_csv(csv)
            if time_series_2:
                series_2.to_pandas().to_csv(csv.name+'2')
        elif tocsv:
            to_csv(
                x=series,
                path=str(tocsv),
            )
            if time_series_2:
                to_csv(x=series_2, path=str(tocsv)+'2')

        data_retrieval_time = f"{timer.perf_counter() - data_retrieval_start_time:.3f}"
        if not verbose:
            return data_retrieval_time
        else:
            print(f'[bold green]It worked[/bold green] and took : {data_retrieval_time}')

    except Exception as e:
        print(f"An error occurred: {e}")


def select_time_series(
    time_series: Path,
    variable: Annotated[str, typer.Argument(..., help='Variable name to select from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    list_variables: Annotated[bool, typer_option_list_variables] = False,
    timestamps: Annotated[Optional[Any], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    time: Annotated[Optional[int], typer.Option(help="New chunk size for the 'time' dimension")] = None,
    lat: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lat' dimension")] = None,
    lon: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lon' dimension")]= None,
    # convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_neighbor_lookup] = MethodForInexactMatches.nearest,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    in_memory: Annotated[bool, typer_option_in_memory] = False,
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    # output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """
    Select data using a Kerchunk reference file
    """
    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    # logger.debug(f'Command context : {print(typer.Context)}')

    data_retrieval_start_time = timer.time()
    logger.debug(f'Starting data retrieval... {data_retrieval_start_time}')

    timer_start = timer.time()
    dataset = xr.open_dataset(
        time_series,
        mask_and_scale=mask_and_scale,
    )  # is a dataset
    timer_end = timer.time()
    logger.debug(f"Dataset opening via Xarray took {timer_end - timer_start:.2f} seconds")

    available_variables = list(dataset.data_vars)  # Is there a faster way ?
    if list_variables:
        print(f'The dataset contains the following variables : `{available_variables}`.')
        return

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

    if verbose:
        print(location_time_series)
        print_log_messages(
            data_retrieval_start_time,
            data_retrieval_end_time,
           # "kerchunking_{time}.log",
           "debug.log",
        )

    # results = {
    #     location_time_series.name: location_time_series.to_numpy(),
    # }
    # title = 'Location time series'
    
    # # special case!
    # if location_time_series is not None and timestamps is None:
    #     timestamps = location_time_series.time.to_numpy()

    # print_irradiance_table_2(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     dictionary=results,
    #     title=title,
    #     rounding_places=rounding_places,
    #     verbose=verbose,
    # )
    if statistics:  # after echoing series which might be Long!
        print_series_statistics(
            data_array=location_time_series,
            title='Selected series',
        )
    if csv:
        to_csv(
            x=location_time_series,
            path=csv,
        )


# @app.command(
#     'select',
#     no_args_is_help=True,
#     help='  Select time series over a location',
#     rich_help_panel='Select data',
# )
def select_time_series_from_json(
    reference_file: Annotated[Path, typer.Argument(..., help="Path to the kerchunk reference file")],
    variable: Annotated[str, typer.Argument(..., help='Variable name to select from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    list_variables: Annotated[bool, typer_option_list_variables] = False,
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
    """
    Select data using a Kerchunk reference file
    """
    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    # logger.debug(f'Command context : {print(typer.Context)}')

    data_retrieval_start_time = timer.time()
    logger.debug(f'Starting data retrieval... {data_retrieval_start_time}')

    timer_start = timer.time()
    mapper = fsspec.get_mapper(
        "reference://",
        fo=str(reference_file),
        remote_protocol="file",
        remote_options={"skip_instance_cache": True},
    )
    timer_end = timer.time()
    logger.debug(f"Mapper creation took {timer_end - timer_start:.2f} seconds")
    # dataset = xr.open_zarr(
    #     mapper, consolidated=False, chunks={"time": 366}
    # )  # is a dataset
    timer_start = timer.time()
    dataset = xr.open_dataset(
        mapper,
        engine="zarr",
        backend_kwargs={"consolidated": False},
        chunks=None,
        mask_and_scale=mask_and_scale,
    )  # is a dataset
    timer_end = timer.time()
    logger.debug(f"Dataset opening via Xarray took {timer_end - timer_start:.2f} seconds")

    available_variables = list(dataset.data_vars)  # Is there a faster way ?
    if list_variables:
        print(f'The dataset contains the following variables : `{available_variables}`.')
        return

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

    if verbose:
        print(location_time_series)
    # results = {
    #     location_time_series.name: location_time_series.to_numpy(),
    # }
    # title = 'Location time series'
    
    # # special case!
    # if location_time_series is not None and timestamps is None:
    #     timestamps = location_time_series.time.to_numpy()

    # print_irradiance_table_2(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     dictionary=results,
    #     title=title,
    #     rounding_places=rounding_places,
    #     verbose=verbose,
    # )
    if statistics:  # after echoing series which might be Long!
        print_series_statistics(
            data_array=location_time_series,
            timestamps=timestamps,
            title='Selected series',
        )
    if csv:
        to_csv(
            x=location_time_series,
            path=csv,
        )

    # return location_time_series


# @app.command(
#     'select-from-memory',
#     no_args_is_help=True,
#     help='  Select time series over a location',
#     rich_help_panel='Select data',
# )
def select_time_series_from_json_in_memory(
    reference_file: Annotated[Path, typer.Argument(..., help="Path to the kerchunk reference file")],
    variable: Annotated[str, typer.Argument(..., help='Variable name to select from')],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    timestamps: Annotated[Optional[Any], typer_argument_timestamps] = None,
    start_time: Annotated[Optional[datetime], typer_option_start_time] = None,
    end_time: Annotated[Optional[datetime], typer_option_end_time] = None,
    list_variables: Annotated[bool, typer_option_list_variables] = False,
    time: Annotated[Optional[int], typer.Option(help="New chunk size for the 'time' dimension")] = None,
    lat: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lat' dimension")] = None,
    lon: Annotated[Optional[int], typer.Option(help="New chunk size for the 'lon' dimension")]= None,
    # convert_longitude_360: Annotated[bool, typer_option_convert_longitude_360] = False,
    mask_and_scale: Annotated[bool, typer_option_mask_and_scale] = False,
    neighbor_lookup: Annotated[MethodForInexactMatches, typer_option_neighbor_lookup] = None,
    tolerance: Annotated[Optional[float], typer_option_tolerance] = 0.1, # Customize default if needed
    statistics: Annotated[bool, typer_option_statistics] = False,
    csv: Annotated[Path, typer_option_csv] = None,
    # output_filename: Annotated[Path, typer_option_output_filename] = 'series_in',  #Path(),
    variable_name_as_suffix: Annotated[bool, typer_option_variable_name_as_suffix] = True,
    rounding_places: Annotated[Optional[int], typer_option_rounding_places] = ROUNDING_PLACES_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """
    Select data using a Kerchunk reference file
    """
    # if convert_longitude_360:
    #     longitude = longitude % 360
    # warn_for_negative_longitude(longitude)

    # logger.debug(f'Command context : {print(typer.Context)}')

    timer_start = timer.time()
    mapper = fsspec.get_mapper(
        "reference://",
        fo=str(reference_file),
        remote_protocol="file",
        remote_options={"skip_instance_cache": True},
    )
    timer_end = timer.time()
    logger.debug(f"Mapper creation took {timer_end - timer_start:.2f} seconds")
    # dataset = xr.open_zarr(
    #     mapper, consolidated=False, chunks={"time": 366}
    # )  # is a dataset
    timer_start = timer.time()
    dataset = xr.open_dataset(
        mapper,
        engine="zarr",
        backend_kwargs={"consolidated": False},
        chunks=None,
        mask_and_scale=mask_and_scale,
    )  # is a dataset
    timer_end = timer.time()
    logger.debug(f"Dataset opening via Xarray took {timer_end - timer_start:.2f} seconds")

    available_variables = list(dataset.data_vars)
    if not variable in available_variables:
        print(f'The requested variable `{variable}` does not exist! Plese select one among the available variables : {available_variables}.')
        raise typer.Exit(code=0)
    else:
        # variable
        timer_start = timer.time()
        time_series = dataset[variable]
        timer_end = timer.time()
        logger.debug(f"Data array variable selection took {timer_end - timer_start:.2f} seconds")

        # chunking
        timer_start = timer.time()
        chunks = {'time': time, 'lat': lat, 'lon': lon}
        time_series.chunk(chunks=chunks)
        timer_end = timer.time()
        logger.debug(f"Data array rechunking took {timer_end - timer_start:.2f} seconds")
        
        # in-memory
        timer_start = timer.time()
        time_series.load()  # load into memory for faster ... ?
        timer_end = timer.time()
        logger.debug(f"Data array variable loading in memory took {timer_end - timer_start:.2f} seconds")

    data_retrieval_start_time = timer.time()
    logger.debug('Starting data retrieval... {data_retrieval_start_time}')

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

    results = {
        location_time_series.name: location_time_series.to_numpy(),
    }

    title = 'Location time series'
    
    # special case!
    if location_time_series is not None and timestamps is None:
        timestamps = location_time_series.time.to_numpy()

    # print_irradiance_table_2(
    #     longitude=longitude,
    #     latitude=latitude,
    #     timestamps=timestamps,
    #     dictionary=results,
    #     title=title,
    #     rounding_places=rounding_places,
    #     verbose=verbose,
    # )
    if statistics:  # after echoing series which might be Long!
        print_series_statistics(
            data_array=location_time_series,
            title='Selected series',
        )
    if csv:
        to_csv(
            x=location_time_series,
            path=csv,
        )

    # return location_time_series
