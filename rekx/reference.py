from loguru import logger
logger.remove()
def filter_function(record):
    return verbose
logger.add("kerchunking_{time}.log", filter=filter_function)#, compression="tar.gz")


from typing_extensions import Annotated
from typing import Any
from typing import Optional
from datetime import datetime
from threading import Lock
import typer
from pathlib import Path
from typing_extensions import Annotated
from .typer_parameters import OrderCommands
from .typer_parameters import typer_argument_source_directory
from .typer_parameters import typer_argument_output_directory
from .typer_parameters import typer_argument_kerchunk_combined_reference
from .typer_parameters import typer_option_filename_pattern
from .typer_parameters import typer_option_number_of_workers
from .typer_parameters import typer_argument_longitude_in_degrees
from .typer_parameters import typer_argument_latitude_in_degrees
from .typer_parameters import typer_option_time_series
from .typer_parameters import typer_argument_timestamps
from .typer_parameters import typer_option_start_time
from .typer_parameters import typer_option_end_time
from .typer_parameters import typer_option_convert_longitude_360
from .typer_parameters import typer_option_mask_and_scale
from .typer_parameters import typer_option_nearest_neighbor_lookup
from .typer_parameters import typer_option_tolerance
from .typer_parameters import typer_option_in_memory
from .typer_parameters import typer_option_statistics
from .typer_parameters import typer_option_rounding_places
from .typer_parameters import typer_option_csv
from .typer_parameters import typer_option_variable_name_as_suffix
from .typer_parameters import typer_option_verbose
from .constants import ROUNDING_PLACES_DEFAULT
from .constants import VERBOSE_LEVEL_DEFAULT
from .select import select_time_series
from .utilities import set_location_indexers
from .statistics import print_series_statistics
from .csv import to_csv
import kerchunk
import fsspec
import multiprocessing
import ujson
from kerchunk.hdf import SingleHdf5ToZarr
from rich.progress import (
    BarColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
)
from rich import print
from .hardcodings import exclamation_mark
from .hardcodings import check_mark
from .hardcodings import x_mark
from .messages import ERROR_IN_SELECTING_DATA
import xarray as xr
from .progress import DisplayMode
from .progress import display_context
from .parquet import app as parquet
import time as timer
from enum import Enum
import hashlib


class MethodsForInexactMatches(str, Enum):
    none = None # only exact matches
    pad = 'pad' # ffill: propagate last valid index value forward
    backfill = 'backfill' # bfill: propagate next valid index value backward
    nearest = 'nearest' # use nearest valid index value


app = typer.Typer(
    cls=OrderCommands,
    add_completion=True,
    add_help_option=True,
    rich_markup_mode="rich",
    help=f'Create kerchunk reference',
)


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
    verbose: int = 0
):
    """ """
    filename = file_path.stem
    output_file = f"{output_directory}/{filename}.json"
    hash_file = f"{output_directory}/{filename}.json.hash"
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


if __name__ == "__main__":
    app()
