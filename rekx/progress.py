from contextlib import nullcontext
from enum import Enum

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskID, TextColumn, TimeRemainingColumn


class DisplayMode(Enum):
    SILENT = 0
    SPINNER = 1
    BARS = 2


console = Console()
display_context = {
    DisplayMode.SILENT: nullcontext(),
    DisplayMode.SPINNER: console.status("[bold green]Processing..."),
    DisplayMode.BARS: Progress(transient=True),
}


progress = Progress(
    TextColumn("[bold blue]{task.description}", justify="right"),
    BarColumn(bar_width=None),
    "[progress.percentage]{task.percentage:>3.1f}%",
    "•",
    TimeRemainingColumn(),
)
