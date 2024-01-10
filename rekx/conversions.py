from math import degrees, pi, radians
from typing import Any, List

import numpy as np
import typer
from rich import box
from rich.progress import track
from rich.table import Table


def convert_to_radians(
    ctx: typer.Context, param: typer.CallbackParam, angle: float
) -> float:
    """Convert floating point angular measurement from degrees to radians."""
    if ctx.resilient_parsing:
        return
    if type(angle) != float:
        raise typer.BadParameter("Input should be a float!")

    return np.radians(angle)
