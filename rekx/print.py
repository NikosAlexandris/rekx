from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE_HEAD


def print_chunk_shapes_table(chunk_shapes):
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    table.add_column("Variable", style="dim", no_wrap=True)
    table.add_column("Shapes", no_wrap=True)
    table.add_column("Files", no_wrap=True)
    table.add_column("Count", no_wrap=True)

    for variable, shapes in chunk_shapes.items():
        for shape, files in shapes.items():
            shapes_string = ' x '.join(map(str, shape))
            files = list(files)  # make subscriptable
            files_string = Path(files[0]).name if len(files) == 1 else f"{Path(files[0]).name} .."
            count_string = str(len(files))
            table.add_row(variable, shapes_string, files_string, count_string)

    console = Console()
    console.print(table)


def print_chunking_shapes(chunking_shapes):
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    table.add_column("Variable", style="dim", no_wrap=True)
    table.add_column("Shape", no_wrap=True)

    # populate the table
    for variable, shape in chunking_shapes.items():
        shape_string = ' x '.join(map(str, shape))
        table.add_row(variable, shape_string)

    console = Console()
    console.print(table)


def print_common_chunk_layouts(common_chunk_layouts):
    # Create a table for 'variable' and the 'common shape'
    table = Table(show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
    table.add_column("Variable", style="dim", no_wrap=True)
    table.add_column("Common Shape", no_wrap=True)

    # populate the table
    for variable, shape in common_chunk_layouts.items():
        shape_string = ' x '.join(map(str, shape))
        table.add_row(variable, shape_string)

    console = Console()
    console.print(table)
