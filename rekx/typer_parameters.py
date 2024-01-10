import typer
from click import Context
from typer.core import TyperGroup

from rekx.constants import (
    LATITUDE_MAXIMUM,
    LATITUDE_MINIMUM,
    LONGITUDE_MAXIMUM,
    LONGITUDE_MINIMUM,
)
from rekx.rich_help_panel_names import (
    rich_help_panel_advanced_options,
    rich_help_panel_output,
    rich_help_panel_select,
    rich_help_panel_time_series,
)
from rekx.timestamp import callback_generate_datetime_series, parse_timestamp_series


class OrderCommands(TyperGroup):
    def list_commands(self, ctx: Context):
        """Return list of commands in the order they appear.

        See also
        --------
        - https://github.com/tiangolo/typer/issues/428#issuecomment-1238866548

        """
        return list(self.commands)


# Generic


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"Rekx prototype version: {version('rekx')}")
        raise typer.Exit(code=0)


typer_option_dry_run = typer.Option(
    # "--dry-run",
    help=f"Run the command without making any changes. [yellow bold reverse] Try Me! [/yellow bold reverse]",
    # default_factory = False,
)

typer_option_humanize = typer.Option(
    "--humanize",
    "-h",
    help="Convert byte sizes into human-readable formats",
    # default = False,
)

# Where?

longitude_typer_help = f"Longitude in decimal degrees ranging in [-180, 360]. [yellow]If ranging in [0, 360], consider the `--convert-longitude-360` option.[/yellow]"
typer_argument_longitude_in_degrees = typer.Argument(
    help=longitude_typer_help,
    min=LONGITUDE_MINIMUM,
    max=LONGITUDE_MAXIMUM,
)
latitude_typer_help = "Latitude in decimal degrees ranging in [-90, 90]"
typer_argument_latitude_in_degrees = typer.Argument(
    help=latitude_typer_help,
    min=LATITUDE_MINIMUM,
    max=LATITUDE_MAXIMUM,
)

# # When?

# timestamp_typer_help = "Quoted date-time string of data to extract from series, example: [yellow]'2112-12-21 21:12:12'[/yellow]'"
# typer_argument_timestamp = typer.Argument(
#     help=timestamp_typer_help,
#     callback=ctx_attach_requested_timezone,
#     # rich_help_panel=rich_help_panel_time_series,
#     default_factory=now_utc_datetimezone,
# )
timestamps_typer_help = "Quoted date-time strings of data to extract from series, example: [yellow]'2112-12-21, 2112-12-21 12:21:21, 2112-12-21 21:12:12'[/yellow]'"
typer_argument_timestamps = typer.Argument(
    help=timestamps_typer_help,
    parser=parse_timestamp_series,
    callback=callback_generate_datetime_series,
    #     default_factory=now_utc_datetimezone_series,
)
# typer_option_timestamps = typer.Option(
#     help='Timestamps',
#     parser=parse_timestamp_series,
#     callback=callback_generate_datetime_series,
# #     default_factory=now_utc_datetimezone_series,
# )
typer_option_start_time = typer.Option(
    help=f"Start timestamp of the period. [yellow]Overrides the `timestamps` paramter![/yellow]",
    rich_help_panel=rich_help_panel_time_series,
    default_factory=None,
)
# typer_option_frequency = typer.Option(
#     help=f'Frequency for the timestamp generation function',
#     rich_help_panel=rich_help_panel_time_series,
#     # default_factory='h'
# )
typer_option_end_time = typer.Option(
    help="End timestamp of the period. [yellow]Overrides the `timestamps` paramter![/yellow]",
    rich_help_panel=rich_help_panel_time_series,
    default_factory=None,
)

# Paths

from pathlib import Path


def callback_input_path(input_path: Path):
    """ """
    from rich import print

    if not input_path.exists():
        print(f"[red]The path [code]{input_path}[/code] does not exist[/red].")
        raise typer.Exit()

    if not input_path.is_file() and not input_path.is_dir():
        print(f"[red]The path: [code]{input_path}[/code] is not valid[/red].")
        raise typer.Exit()

    return input_path


def callback_source_directory(directory: Path):
    """ """
    if not directory.exists() or not any(directory.iterdir()):
        print(
            f"[red]The directory [code]{directory}[/code] does not exist or is empty[/red]."
        )
    return directory


typer_argument_input_path = typer.Argument(
    show_default=True,
    help="Input filename or directory path",
    rich_help_panel=rich_help_panel_time_series,
    callback=callback_input_path,
    # default_factory = None
)
typer_argument_source_directory = typer.Argument(
    show_default=True,
    help="Source directory path",
    rich_help_panel=rich_help_panel_time_series,
    callback=callback_source_directory,
    # default_factory = None
)
typer_argument_output_directory = typer.Argument(
    show_default=True,
    help="Output directory path for reference files. Will create if inexistent.",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory = None
)
typer_argument_kerchunk_combined_reference = typer.Argument(
    show_default=True,
    help="Combined kerchunk reference file name",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory = None
)
typer_option_filename_pattern = typer.Option(
    help="Filename pattern to match",
    # rich_help_panel=
)
typer_option_number_of_workers = typer.Option(
    help="Number of workers for parallel processing using `concurrent.futures`",
    rich_help_panel=rich_help_panel_advanced_options,
)


# # Time series

time_series_typer_help = "A time series dataset (any format supported by Xarray)"
typer_argument_time_series = typer.Argument(
    show_default=True,
    help=time_series_typer_help,
    # rich_help_panel=rich_help_panel_time_series,
)
typer_option_time_series = typer.Option(
    show_default=True,
    help=time_series_typer_help,
    rich_help_panel=rich_help_panel_time_series,
)
typer_option_list_variables = typer.Option(
    show_default=True,
    help=f"List variables in the Kerchunk reference set",
    default_factory=False,
)
typer_option_mask_and_scale = typer.Option(
    help="Mask and scale the series",
    rich_help_panel=rich_help_panel_time_series,
    # default_factory=False,
)
typer_option_neighbor_lookup = typer.Option(
    help="Enable nearest neighbor (inexact) lookups. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]",
    show_default=True,
    show_choices=True,
    case_sensitive=False,
    rich_help_panel=rich_help_panel_select,
    # default_factory=None, # default_factory=MethodsForInexactMatches.nearest,
)
typer_option_tolerance = typer.Option(
    help=f"Maximum distance between original & new labels for inexact matches. Read Xarray manual on [underline]nearest-neighbor-lookups[/underline]",
    #  https://docs.xarray.dev/en/stable/user-guide/indexing.html#nearest-neighbor-lookups',
    rich_help_panel=rich_help_panel_select,
    # default_factory=0.1,
)
typer_option_repetitions = typer.Option(
    help=f"Times to repeat the reading operation and calculate the average read time.",
    rich_help_panel=rich_help_panel_select,
    # default = 10,
)


# Arrays & Chunks


def parse_variable_shape(variable_shape: str):
    if isinstance(variable_shape, str):
        return [int(dimension) for dimension in variable_shape.split(",")]


typer_argument_variable_shape = typer.Argument(
    help="Variable shape",
    parser=parse_variable_shape,
    # default=None,
)

# Output options

typer_option_verbose = typer.Option(
    "--verbose",
    "-v",
    count=True,
    is_flag=False,
    help="Show details while executing commands",
    rich_help_panel=rich_help_panel_output,
    # default_factory=0,
)
typer_option_rounding_places = typer.Option(
    "--rounding-places",
    "-r",
    help="Number of digits to round results to",
    show_default=True,
    rich_help_panel=rich_help_panel_output,
    # default_factory=5,
)

typer_option_statistics = typer.Option(
    help="Calculate and display summary statistics",
    rich_help_panel=rich_help_panel_output,
    # default=False
)
typer_option_variable_name_as_suffix = typer.Option(
    help="Suffix the output filename with the variable name",
    rich_help_panel=rich_help_panel_output,
    # default=False
)
typer_option_csv = typer.Option(
    help="CSV output filename",
    rich_help_panel=rich_help_panel_output,
    # default_factory='series_in',
)

# Helpers

typer_option_convert_longitude_360 = typer.Option(
    help="Convert range of longitude values to [0, 360]",
    rich_help_panel="Helpers",
    # default_factory=False
)
typer_option_in_memory = typer.Option(
    help="Use in-memory processing",  # You may need to customize the help text
    # default_factory=False
)
