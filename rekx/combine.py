import typer
from typing_extensions import Annotated
from .typer_parameters import OrderCommands
from .progress import DisplayMode
from .progress import display_context
from pathlib import Path
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_option_filename_pattern
from .typer_parameters import typer_option_dry_run
from .typer_parameters import typer_argument_kerchunk_combined_reference
from .rich_help_panel_names import rich_help_panel_combine
from rekx.typer_parameters import typer_option_verbose
from rekx.constants import VERBOSE_LEVEL_DEFAULT
import fsspec
import ujson
import kerchunk


# app = typer.Typer(
#     cls=OrderCommands,
#     add_completion=True,
#     add_help_option=True,
#     rich_markup_mode="rich",
#     help=f'Create kerchunk reference',
# )


# @app.command(
#     'combine',
#     no_args_is_help=True,
#     help='Combine Kerchunk reference sets',
#     rich_help_panel=rich_help_panel_combine,
# )
def combine_kerchunk_references(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    combined_reference: Annotated[Path, typer_argument_kerchunk_combined_reference] = "combined_kerchunk.json",
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Combine multiple JSON references into a single logical aggregate
    dataset using Kerchunk's `MultiZarrToZarr` function"""

    mode = DisplayMode(verbose)
    with display_context[mode]:

        source_directory = Path(source_directory)
        reference_file_paths = list(source_directory.glob(pattern))
        reference_file_paths = list(map(str, reference_file_paths))

        if dry_run:
            print(f"[bold]Dry run[/bold] of [bold]operations that would be performed[/bold]:")
            print(f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]")
            print(f"> Number of files matched: {len(reference_file_paths)}")
            print(f"> Writing combined reference file to [code]{combined_reference}[/code]")
            return  # Exit for a dry run

        from kerchunk.combine import MultiZarrToZarr
        mzz = MultiZarrToZarr(
            reference_file_paths,
            concat_dims=['time'],
            identical_dims=['lat', 'lon'],
        )
        multifile_kerchunk = mzz.translate()

        combined_reference_filename = Path(combined_reference)
        local_fs = fsspec.filesystem('file')
        with local_fs.open(combined_reference_filename, 'wb') as f:
            f.write(ujson.dumps(multifile_kerchunk).encode())


# @app.command(
#     'combine-parquet',
#     no_args_is_help=True,
#     help='Combine multiple Parquet stores',
#     rich_help_panel='Combine reference sets',
# )
def combine_kerchunk_references_to_parquet(
    source_directory: Annotated[Path, typer_argument_source_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = "*.json",
    combined_reference: Annotated[Path, typer_argument_kerchunk_combined_reference] = "combined_kerchunk.parq",
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Combine multiple JSON references into a single Parquet store using Kerchunk's `MultiZarrToZarr` function"""

    mode = DisplayMode(verbose)
    with display_context[mode]:

        source_directory = Path(source_directory)
        reference_file_paths = list(source_directory.glob(pattern))
        reference_file_paths = list(map(str, reference_file_paths))

        if dry_run:
            print(f"[bold]Dry run[/bold] of [bold]operations that would be performed[/bold]:")
            print(f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]")
            print(f"> Number of files matched: {len(reference_file_paths)}")
            print(f"> Writing combined reference file to [code]{combined_reference}[/code]")
            return  # Exit for a dry run

        # Create LazyReferenceMapper to pass to MultiZarrToZarr
        filesystem = fsspec.filesystem("file")
        import os

        combined_reference.mkdir(parents=True, exist_ok=True)
        from fsspec.implementations.reference import LazyReferenceMapper
        output_lazy = LazyReferenceMapper(
                root=str(combined_reference),
                fs=filesystem,
                cache_size=1000,
        )

        from kerchunk.combine import MultiZarrToZarr

        # Combine single references
        mzz = MultiZarrToZarr(
            reference_file_paths,
            remote_protocol="file",
            concat_dims=["time"],
            identical_dims=["lat", "lon"],
            out=output_lazy,
        )
        multifile_kerchunk = mzz.translate()

        output_lazy.flush()  # Write all non-full reference batches

        # Read from the Parquet storage
        kerchunk.df.refs_to_dataframe(multifile_kerchunk, str(combined_reference))

        filesystem = fsspec.implementations.reference.ReferenceFileSystem(
            fo=str(combined_reference),
            target_protocol='file',
            remote_protocol='file',
            lazy=True
        )
        ds = xr.open_dataset(
            filesystem.get_mapper(''),
            engine="zarr",
            chunks={},
            backend_kwargs={"consolidated": False},
        )
        print(ds)
