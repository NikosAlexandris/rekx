from rich import print
import time as timer
from pathlib import Path
from rekx.constants import (
    DATASET_SELECT_TOLERANCE_DEFAULT,
    REPETITIONS_DEFAULT,
    VERBOSE_LEVEL_DEFAULT,
)
from .typer_parameters import (
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
    typer_argument_time_series,
    typer_argument_variable,
    typer_option_repetitions,
    typer_option_tolerance,
    typer_option_verbose,
)
from typing import Optional
from typing_extensions import Annotated
import xarray as xr


def read_performance(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer_argument_variable],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # window: Annotated[int, typer_option_spatial_window_in_degrees] = None,
    tolerance: Annotated[
        Optional[float], typer_option_tolerance
    ] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
) -> str:
    """
    Count the median time of repeated read and load operations of the time
    series data over a geographic location from an Xarray-supported file
    format.

    Parameters
    ----------
    time_series:
        Path to Xarray-supported input file
    variable: str
        Name of the variable to query
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    # window:
    tolerance: float
        Maximum distance between original and new labels for inexact matches.
        Read Xarray manual on nearest-neighbor-lookups
    repetitions: int
        Number of times to repeat read operation

    Returns
    -------
    data_retrieval_time : str
        The median time of repeated operations it took to retrieve data over
        the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps. See also ...

    """
    from .models import get_file_format

    file_format = get_file_format(time_series)
    open_dataset_options = file_format.open_dataset_options()
    dataset_select_options = file_format.dataset_select_options(tolerance)

    # indexers = set_location_indexers(
    #     data_array=time_series,
    #     longitude=longitude,
    #     latitude=latitude,
    #     verbose=verbose,
    # )
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
        print(
            f"Cannot open [code]{variable}[/code] from [code]{time_series}[/code] via Xarray: {exception}"
        )
        # raise SystemExit(33)
        return "-"


def read_performance_area(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer_argument_variable],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    max_longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    max_latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[
        Optional[float], typer_option_tolerance
    ] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
):
    """
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
                        lon=slice(longitude, max_longitude),
                        lat=slice(latitude, max_latitude),
                        **dataset_select_options,
                    )
                    .load()
                )
            timings.append(timer.perf_counter() - data_retrieval_start_time)

        average_data_retrieval_time = sum(timings) / len(timings)
        return f"{average_data_retrieval_time:.3f}"

    except Exception as exception:
        print(
            f"Cannot open [code]{variable}[/code] from [code]{time_series}[/code] via Xarray: {exception}"
        )
        # raise SystemExit(33)
        return "-"


def read_performance_cli(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer_argument_variable],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[
        Optional[float], typer_option_tolerance
    ] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """
    Command line interface to `read_performance()` to count the time to read
    and load data over a geographic location from an Xarray-supported file
    format.

    Parameters
    ----------
    time_series:
        Path to Xarray-supported input file
    variable: str
        Name of the variable to query
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    tolerance: float
        Maximum distance between original and new labels for inexact matches.
        Read Xarray manual on nearest-neighbor-lookups
    repetitions: int
        Number of times to repeat read operation
    verbose: int
        Verbosity level

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
            f"[bold green]Data read in memory in[/bold green] : {average_data_retrieval_time} :high_voltage::high_voltage:"
        )


def read_performance_area_cli(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer_argument_variable],
    longitude: Annotated[float, typer_argument_longitude_in_degrees],
    max_longitude: Annotated[float, typer_argument_longitude_in_degrees],
    latitude: Annotated[float, typer_argument_latitude_in_degrees],
    max_latitude: Annotated[float, typer_argument_latitude_in_degrees],
    tolerance: Annotated[
        Optional[float], typer_option_tolerance
    ] = DATASET_SELECT_TOLERANCE_DEFAULT,
    repetitions: Annotated[int, typer_option_repetitions] = REPETITIONS_DEFAULT,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
) -> None:
    """
    Command line interface to `read_performance()` to count the time to read
    and load data over a geographic window from an Xarray-supported file
    format.

    Parameters
    ----------
    time_series:
        Path to Xarray-supported input file
    variable: str
        Name of the variable to query
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    tolerance: float
        Maximum distance between original and new labels for inexact matches.
        Read Xarray manual on nearest-neighbor-lookups
    repetitions: int
        Number of times to repeat read operation
    verbose: int
        Verbosity level

    Returns
    -------
    data_retrieval_time : float or None ?
        The time it took to retrieve data over the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps.

    """
    average_data_retrieval_time = read_performance_area(
        time_series=time_series,
        variable=variable,
        longitude=longitude,
        max_longitude=max_longitude,
        latitude=latitude,
        max_latitude=max_latitude,
        tolerance=tolerance,
        repetitions=repetitions,
    )
    if not verbose:
        print(average_data_retrieval_time)
    else:
        print(
            f"[bold green]Data read in memory in[/bold green] : {average_data_retrieval_time} :high_voltage::high_voltage:"
        )
