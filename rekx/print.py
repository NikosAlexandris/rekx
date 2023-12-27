from pathlib import Path
from rich import print
from rich.console import Console
from rich.table import Table
from rich.box import SIMPLE_HEAD
from .constants import NOT_AVAILABLE


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


from rich.console import Console
from rich.table import Table


def format_compression(compression_dictionary):
    if isinstance(compression_dictionary, dict):
        filters = [key for key, value in compression_dictionary.items() if value and key != 'complevel']
        compression_level = compression_dictionary.get('complevel', None)  # old naming habits!
        return {'Filters':', '.join(filters), 'Level': compression_level}
    return compression_dictionary


def print_metadata_table(metadata):
    """
    """
    filename = metadata.get('File name', 'N/A')
    file_size = metadata.get('File size', 'N/A')
    dimensions = metadata.get('Dimensions', {})
    dimensions_string = ', '.join([f"{dimension}: {size}" for dimension, size in dimensions.items()])
    caption = f"File size: {file_size} bytes, Dimensions: {dimensions_string}"
    caption += f"\n* Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]"

    variables_metadata = metadata.get('Variables')
    if variables_metadata:
        table = Table(title=filename, caption=caption, show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
        table.add_column("Variable", style="dim", no_wrap=True)

        # Dynamically add columns based on the keys of the nested dictionaries
        # Assuming all variables have the same set of keys
        for key in next(iter(variables_metadata.values())).keys():
            table.add_column(key.replace('_', ' ').title(), no_wrap=True)

        for variable, details in variables_metadata.items():
            # Format compression dictionary into a readable string
            if 'Compression' in details:
                compression_details = format_compression(details['Compression'])
                details['Compression'] = compression_details['Filters']
                details['Level'] = compression_details['Level']

            row = [variable] + [str(details.get(key, '')) for key in next(iter(variables_metadata.values())).keys()]
            table.add_row(*row)

        console = Console()
        console.print(table)


def print_metadata_series_table(
    metadata_series: dict,
    group_metadata=False,
):
    """
    """
    for filename, metadata in metadata_series.items():
        filename = metadata.get('File name', 'N/A')
        file_size = metadata.get('File size', 'N/A')
        dimensions = metadata.get('Dimensions', {})
        dimensions_string = ', '.join([f"{dimension}: {size}" for dimension, size in dimensions.items()])
        caption = f"File size: {file_size} bytes, Dimensions: {dimensions_string}"
        caption += f"\n* Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]"
        variables_metadata = metadata.get('Variables')
        if variables_metadata:
            table = Table(title=f"[bold]{filename}[/bold]", caption=caption, show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
            # table = Table(caption=caption, show_header=True, header_style="bold magenta", box=SIMPLE_HEAD)
            table.add_column("Variable", style="dim", no_wrap=True)

            # Expectedly all variables feature the same keys
            for key in next(iter(variables_metadata.values())).keys():
                table.add_column(key.replace('_', ' ').title(), no_wrap=True)

            for variable, details in variables_metadata.items():
                if 'Compression' in details:
                    compression_details = format_compression(details['Compression'])
                    details['Compression'] = compression_details['Filters']
                    details['Level'] = compression_details['Level']

                row = [variable] + [str(details.get(key, '')) for key in next(iter(variables_metadata.values())).keys()]
                table.add_row(*row)

            console = Console()
            console.print(table)
            if group_metadata:
                console.print("\n")  # Add an empty line between groups for clarity


def print_metadata_series_long_table(
    metadata_series: dict,
    group_metadata=False,
):
    """
    """
    console = Console()
    columns = []
    columns.append("Name")
    columns.append("Size")
    columns.append("Dimensions")
    metadata_series_level_one = next(iter(metadata_series.values()))
    variables_metadata = metadata_series_level_one.get("Variables", {})
    columns.append("Variable")
    # Add columns from the first variable's metadata dictionary
    for key in next(iter(variables_metadata.values())).keys():
        columns.append(key.replace("_", " ").title())
    dimensions = metadata_series_level_one.get("Dimensions", {})
    dimensions_sort_order = ["bnds", "time", "lon", "lat"]
    dimension_attributes_sorted = {
        key for key in dimensions_sort_order if key in dimensions
    }
    dimension_attributes = " x ".join(
        [f"[bold]{dimension}[/bold]" for dimension in dimension_attributes_sorted]
    )
    caption = f"^ Dimensions: {dimension_attributes} "
    caption += (
        f"* Cache: [bold]Size[/bold] in bytes, [bold]Number of elements[/bold], [bold]Preemption strategy[/bold] ranging in [0, 1]"
    )
    table = Table(
        *columns,
        caption=caption,
        show_header=True,
        header_style="bold magenta",
        box=SIMPLE_HEAD,
    )

    # Process each file's metadata
    for filename, metadata in metadata_series.items():
        filename = metadata.get('File name', NOT_AVAILABLE)
        file_size = metadata.get('File size', NOT_AVAILABLE)

        dimensions = metadata.get('Dimensions', {})
        dimensions_sorted = {key: dimensions[key] for key in dimensions_sort_order if key in dimensions}
        dimension_shape = ' x '.join([f"{size}" for dimension, size in dimensions_sorted.items()])

        variables_metadata = metadata.get('Variables', {})
        # row = []
        for variable, details in variables_metadata.items():
            if 'Compression' in details:
                compression_details = format_compression(details['Compression'])
                details['Compression'] = compression_details['Filters']
                details['Level'] = compression_details['Level']

            row = [filename, str(file_size), dimension_shape, variable]
            row += [str(details.get(key, NOT_AVAILABLE)) for key in details.keys()]
            table.add_row(*row)

        if group_metadata:
            table.add_row("")  # Add an empty line between 'files' for clarity

    console.print(table)
