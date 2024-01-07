# import xarray as xr
# import csv
# from rekx.conversions import round_float_values
# from rekx.constants import ROUNDING_PLACES_DEFAULT


def calculate_series_statistics(data_array, timestamps):
    import xarray as xr
    data_xarray = xr.DataArray(
        data_array,
        coords=[('time', timestamps)],
    )
    data_xarray.load()
    import numpy as np
    from scipy.stats import mode
    statistics = {
        'Start': data_xarray.time.values[0],
        'End': data_xarray.time.values[-1],
        'Count': data_xarray.count().values,
        'Min': data_xarray.min().values,
        '25th Percentile': np.percentile(data_xarray, 25),
        'Mean': data_xarray.mean().values,
        'Median': data_xarray.median().values,
        'Mode': mode(data_xarray.values.flatten())[0],
        'Max': data_xarray.max().values,
        'Sum': data_xarray.sum().values,
        'Variance': data_xarray.var().values,
        'Standard deviation': data_xarray.std().values,
        'Time of Min': data_xarray.idxmin('time').values,
        'Index of Min': data_xarray.argmin().values,
        'Time of Max': data_xarray.idxmax('time').values,
        'Index of Max': data_xarray.argmax().values,
        # 'Longitude of Max': data_xarray.argmax('lon').values,
        # 'Latitude of Max': data_xarray.argmax('lat').values,
    }
    return statistics


def print_series_statistics(
    data_array,
    timestamps,
    title='Time series',
    rounding_places: int = None,
):
    """
    """
    statistics = calculate_series_statistics(data_array, timestamps)
    from rich.table import Table
    from rich import box
    table = Table(
        title=title,
        caption='Caption text',
        show_header=True,
        header_style="bold magenta",
        row_styles=['none', 'dim'],
        box=box.SIMPLE_HEAD,
        highlight=True,
    )
    table.add_column("Statistic", justify="right", style="magenta", no_wrap=True)
    table.add_column("Value", style="cyan")

    # Basic metadata
    basic_metadata = ["Start", "End", "Count"]
    for key in basic_metadata:
        if key in statistics:
            table.add_row(key, str(statistics[key]))

    # Separate!
    table.add_row("", "")

    # Index of items
    index_metadata = [
        'Time of Min',
        'Index of Min',
        'Time of Max',
        'Index of Max', 
        ]

    # Add statistics
    for key, value in statistics.items():
        if key not in basic_metadata and key not in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    # Separate!
    table.add_row("", "")

    # Index of
    for key, value in statistics.items():
        if key in index_metadata:
            # table.add_row(key, str(round_float_values(value, rounding_places)))
            table.add_row(key, str(value))

    from rich.console import Console
    console = Console()
    console.print(table)


# def export_statistics_to_csv(data_array, filename):
#     statistics = calculate_series_statistics(data_array)
#     with open(f'{filename}.csv', 'w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow(["Statistic", "Value"])
#         for statistic, value in statistics.items():
#             writer.writerow([statistic, value])
