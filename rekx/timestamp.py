from datetime import datetime
from typing import List, Optional, Union

import numpy as np
import typer
from rich import print

from rekx.constants import TIMESTAMPS_FREQUENCY_DEFAULT

# Time series


def parse_timestamp_series(
    timestamps: Union[str, datetime, List[datetime]],
):
    if isinstance(timestamps, str):
        datetime_strings = timestamps.strip().split(",")
        return [
            datetime.fromisoformat(timestamp.strip()) for timestamp in datetime_strings
        ]

    elif isinstance(timestamps, datetime):
        return [timestamps]  # return a single datetime as a list

    elif isinstance(timestamps, list):
        datetime_strings = [
            string.strip() for string in timestamps
        ]  # convert strings to naive datetime
        return [datetime.fromisoformat(timestamp) for timestamp in datetime_strings]

    else:
        raise ValueError(
            "Timestamps input must be a string, datetime, or list of datetimes"
        )


def generate_datetime_series(
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    frequency: Optional[str] = TIMESTAMPS_FREQUENCY_DEFAULT,
):
    """
    Example
    -------
    >>> start_time = '2010-06-01 06:00:00'
    >>> end_time = '2010-06-01 08:00:00'
    >>> frequency = 'h'  # 'h' for hourly
    >>> generate_datetime_series(start_time, end_time, frequency)
    array(['2010-06-01T06:00:00', '2010-06-01T07:00:00', '2010-06-01T08:00:00'],
          dtype='datetime64[s]')
    """
    start = np.datetime64(start_time)
    end = np.datetime64(end_time)
    freq = np.timedelta64(1, frequency)
    timestamps = np.arange(start, end + freq, freq)  # +freq to include the end time

    from pandas import DatetimeIndex

    timestamps = DatetimeIndex(timestamps.astype("datetime64[ns]"))
    return timestamps.astype("datetime64[ns]")


def callback_generate_datetime_series(
    ctx: typer.Context,
    timestamps: str,
    # param: typer.CallbackParam,
):
    # print(f'[yellow]i[/yellow] Context: {ctx.params}')
    # print(f'[yellow]i[/yellow] typer.CallbackParam: {param}')
    # print("[yellow]i[/yellow] Executing callback_generate_datetime_series()")
    # print(f'  Input [yellow]timestamps[/yellow] : {timestamps}')
    start_time = ctx.params.get("start_time")
    end_time = ctx.params.get("end_time")
    frequency = ctx.params.get("frequency", "h")
    timezone = ctx.params.get("timezone")

    if start_time is not None and end_time is not None:
        timestamps = generate_datetime_series(start_time, end_time, frequency)

    from pandas import to_datetime

    return to_datetime(timestamps, format="mixed")
    return timestamps
