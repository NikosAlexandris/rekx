import typer
from rich.table import Table
from rich.progress import track
from rich import box
from math import degrees
from math import radians
from math import pi
import numpy as np
from typing import List
from typing import Any
from typing import List


def convert_to_radians(ctx: typer.Context, param: typer.CallbackParam, angle: float) -> float:
    """Convert floating point angular measurement from degrees to radians."""
    if ctx.resilient_parsing:
        return
    if type(angle) != float:
        raise typer.BadParameter("Input should be a float!")

    return np.radians(angle)
