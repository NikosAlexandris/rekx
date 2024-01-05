from .log import logger
from .log import print_log_messages
from typing_extensions import Annotated
from pathlib import Path
from .rich_help_panel_names import rich_help_panel_reference
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_argument_output_directory
from .typer_parameters import typer_option_filename_pattern
from .typer_parameters import typer_option_dry_run
from .typer_parameters import typer_option_number_of_workers
from .typer_parameters import typer_option_verbose
from .constants import VERBOSE_LEVEL_DEFAULT
from .progress import DisplayMode
from .progress import display_context
import multiprocessing
import kerchunk
import fsspec
import ujson
from kerchunk.hdf import SingleHdf5ToZarr
from rich import print
import hashlib


def generate_file_md5(file_path):
    if not file_path.exists():
        # logger.debug(f"File {file_path} does not exist!")
        # print(f"File {file_path} does not exist!")
        return None
    
    with open(file_path, 'rb') as f:
        file_content = f.read()
        
        if not file_content:
            # logger.debug(f"File {file_path} is empty!")
            # print(f"File {file_path} is empty!")
            return None

        hash_value = hashlib.md5(file_content).hexdigest()
        # logger.debug(f'Hash for {file_path}: {hash_value}')
        # print(f'Hash for {file_path}: {hash_value}')
        return hash_value


def create_single_reference(
    file_path: Path,
    output_directory: Path,
    # md5: bool = True,
    verbose: int = 0
):
    """Helper function for create_kerchunk_reference()

    Notes

    Will create an MD5 Hash for each new reference file in order to avoid
    regenerating the same file in case of a renewed attempt to reference the
    same file.  This is useful in the context or epxlorative massive
    processing.

    """
    filename = file_path.stem
    output_file = f"{output_directory}/{filename}.json"
    hash_file = output_file + '.hash'
    generated_hash = generate_file_md5(file_path)
    local_fs = fsspec.filesystem('file')
    if local_fs.exists(output_file) and local_fs.exists(hash_file):
        logger.debug(f'Found a reference file \'{output_file}\' and a hash \'{hash_file}\'')
        with local_fs.open(hash_file, 'r') as hf:
            existing_hash = hf.read().strip()
        
        if existing_hash == generated_hash:
            pass
    else:
        logger.debug(f'Creating reference file \'{output_file}\' with hash \'{generated_hash}\'')
        file_url = f"file://{file_path}"
        with fsspec.open(file_url, mode='rb') as input_file:
            h5chunks = SingleHdf5ToZarr(input_file, file_url, inline_threshold=0)
            json = ujson.dumps(h5chunks.translate()).encode()
            with local_fs.open(output_file, 'wb') as f:
                f.write(json)
            with local_fs.open(hash_file, 'w') as hf:
                hf.write(generated_hash)


def create_kerchunk_reference(
    source_directory: Annotated[Path, typer_argument_source_directory],
    output_directory: Annotated[Path, typer_argument_output_directory],
    pattern: Annotated[str, typer_option_filename_pattern] = '*.nc',
    workers: Annotated[int, typer_option_number_of_workers] = 4,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """Reference local NetCDF files using Kerchunk"""
    # import cProfile
    # import pstats
    # profiler = cProfile.Profile()
    # profiler.enable()

    file_paths = list(source_directory.glob(pattern))
    if not file_paths:
        logger.info(
            "No files found in the source directory matching the pattern."
        )
        return
    if dry_run:
        print(f"[bold]Dry run[/bold] of [bold]operations that would be performed[/bold]:")
        print(f"> Reading files in [code]{source_directory}[/code] matching the pattern [code]{pattern}[/code]")
        print(f"> Number of files matched: {len(file_paths)}")
        print(f"> Creating single reference files to [code]{output_directory}[/code]")
        return  # Exit for a dry run
    output_directory.mkdir(parents=True, exist_ok=True)
    
    # Map verbosity level to display mode
    mode = DisplayMode(verbose)
    with display_context[mode]:
        with multiprocessing.Pool(processes=workers) as pool:
            from functools import partial

            partial_create_single_reference = partial(
                create_single_reference, output_directory=output_directory
            )
            results = pool.map(partial_create_single_reference, file_paths)
        
    # profiler.disable()
    # stats = pstats.Stats(profiler).sort_stats('cumulative')
    # stats.print_stats(10)  # Print the top 10 time-consuming functions
