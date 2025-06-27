"""
Convert Kerchunk references to Zarr
"""

import typer
from pathlib import Path
import xarray as xr
from xarray import Dataset
import zarr
from rich import print
from dask.distributed import LocalCluster, Client
from distributed import progress
from zarr.storage import DirectoryStore
from typing_extensions import Annotated, Optional, List
from .typer_parameters import (
    typer_option_dry_run,
    typer_argument_latitude_in_degrees,
    typer_argument_longitude_in_degrees,
    typer_argument_time_series,
    typer_argument_variable,
    typer_option_repetitions,
    typer_option_tolerance,
    typer_option_verbose,
)
from .constants import VERBOSE_LEVEL_DEFAULT

DASK_SCHEDULER_IP = 'localhost'
DASK_SCHEDULER_PORT = '8888'
DASK_COMPUTE = False
NUMBER_OF_WORKERS = 36

XARRAY_OPEN_DATA_COMBINE = "nested"
XARRAY_OPEN_DATA_CONCATENATE_DIMENSION = "time"
XARRAY_OPEN_DATA_ENGINE = "h5netcdf"
XARRAY_OPEN_DATA_IN_PARALLEL = True

ZARR_STORE_BASE_PATH = Path("sis_italia")
ZARR_CONSOLIDATE = True
ZARR_COMPRESSOR_CODEC = "zstd"
COMPRESSION_FILTER_DEFAULT = ZARR_COMPRESSOR_CODEC
ZARR_COMPRESSOR_LEVEL = 1
COMPRESSION_LEVEL_DEFAULT = ZARR_COMPRESSOR_LEVEL
ZARR_COMPRESSOR_SHUFFLE = "shuffle"
SHUFFLING_DEFAULT = ZARR_COMPRESSOR_SHUFFLE
# ZARR_COMPRESSOR = zarr.codecs.BloscCodec(
ZARR_COMPRESSOR = zarr.blosc.Blosc(
    cname=ZARR_COMPRESSOR_CODEC,
    clevel=ZARR_COMPRESSOR_LEVEL,
    shuffle=ZARR_COMPRESSOR_SHUFFLE,
)

NETCDF_FILENAME_PREFIX = 'SISin*'
NETCDF_COMPRESSOR_CODEC = 'zlib'
NETCDF_COMPRESSOR_LEVEL = 0
NETCDF_FILENAME_SUFFIX = f"{NETCDF_COMPRESSOR_CODEC}_{NETCDF_COMPRESSOR_LEVEL}"
NETCDF_FILENAME_EXTENSION = 'nc'

DATASET_SELECT_TOLERANCE_DEFAULT = 0.1

CHUNKING_SHAPES = [
    #(48, 2, 2),
    #(48, 4, 4),
    #(48, 8, 8),
    #(48, 16, 16),
    #(48, 32, 32),
    (48, 64, 64),
    (48, 128, 128)
]
GREEN_DASH = f"[green]-[/green]"


# Add this before generating the Zarr store
def apply_safe_chunking(dataset, main_variable, time_chunks, lat_chunks, lon_chunks):
    for var in dataset.variables:
        # Skip primary variable (handled separately)
        if var == main_variable:
            continue
            
        # Clear problematic encoding
        if 'chunks' in dataset[var].encoding:
            del dataset[var].encoding['chunks']
        if 'compressor' in dataset[var].encoding:
            del dataset[var].encoding['compressor']
            
        # Apply safe chunking to auxiliary variables
        if var in ['lat_bnds', 'lon_bnds']:
            dataset[var] = dataset[var].chunk({
                'time': time_chunks,
                'lat': lat_chunks,
                'lon': lon_chunks,
                'bnds': 2  # Explicit chunk for bounds dimension
            })
    
    return dataset


def read_parquet_via_zarr(
    time_series: Annotated[Path, typer_argument_time_series],
    variable: Annotated[str, typer_argument_variable],
    # longitude: Annotated[float, typer_argument_longitude_in_degrees],
    # latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # window: Annotated[int, typer_option_spatial_window_in_degrees] = None,
    tolerance: Annotated[
        Optional[float], typer_option_tolerance
    ] = DATASET_SELECT_TOLERANCE_DEFAULT,
) -> None:
    """
    Read a time series data file via Xarray's Zarr engine
    format.

    Parameters
    ----------
    time_series:
        Path to Xarray-supported input file
    variable: str
        Name of the variable to query
    longitude: float
        The longitude of the location to read data
    latitude: float
        The latitude of the location to read data
    # window:
    tolerance: float
        Maximum distance between original and new labels for inexact matches.
        Read Xarray manual on nearest-neighbor-lookups

    Returns
    -------
    data_retrieval_time : str
        The median time of repeated operations it took to retrieve data over
        the requested location

    Notes
    -----
    ``mask_and_scale`` is always set to ``False`` to avoid errors related with
    decoding timestamps. See also ...

    """
    from .models import get_file_format

    file_format = get_file_format(time_series)
    open_dataset_options = file_format.open_dataset_options()  # some Class function !

    # dataset_select_options = file_format.dataset_select_options(tolerance)
    # indexers = set_location_indexers(
    #     data_array=time_series,
    #     longitude=longitude,
    #     latitude=latitude,
    #     verbose=verbose,
    # )

    try:
        # with xr.open_dataset(str(time_series), **open_dataset_options) as dataset:
        #     _ = (
        #         dataset[variable]
        #         .sel(
        #             lon=longitude,
        #             lat=latitude,
        #             method="nearest",
        #             **dataset_select_options,
        #         )
        #         .load()
        #     )
        return xr.open_dataset(
            time_series.as_posix(),
            **open_dataset_options,
        )

    except Exception as exception:
        print(
            f"Cannot open [code]{time_series}[/code] from [code]{time_series}[/code] via Xarray: {exception}"
        )
        raise SystemExit(33)


def parse_compression_filters(compressing_filters: str) -> List[str]:
    if isinstance(compressing_filters, str):
        return compressing_filters.split(",")
    else:
        raise typer.BadParameter("Compression filters input must be a string")


def generate_zarr_store(
    dataset: Dataset,
    store: str,
    latitude_chunks: int,
    longitude_chunks: int,
    time_chunks: int = -1,
    compute: bool = DASK_COMPUTE,
    consolidate: bool = ZARR_CONSOLIDATE,
    compressor = ZARR_COMPRESSOR,
    mode: str = 'w-',
):
    """
    """
    print(f" {GREEN_DASH} Chunk the dataset")
    dataset = dataset.chunk({"time": time_chunks, "lat": latitude_chunks, "lon": longitude_chunks})
    print(f'   > Dataset shape after chunking : {dataset.data_vars}')

    print(f"   Define the store path for the current chunking shape")
    # store = LocalStore(store_path)
    store = DirectoryStore(store)

    print(f' {GREEN_DASH} Build the Dask task graph')
    return dataset.to_zarr(
        store=store,
        compute=False,
        consolidated=consolidate,
        encoding={
            dataset.SIS.name: {"compressors": compressor},
            "time": {"compressors": compressor},
            "lat": {"compressors": compressor},
            "lon": {"compressors": compressor},
        },
        mode=mode,
        safe_chunks=False,
    )


def convert_parquet_to_zarr_store(
    time_series: Annotated[Path, typer_argument_time_series],
    zarr_store: Annotated[Path, typer.Argument(help='Local Zarr store')],
    variable: Annotated[str, typer_argument_variable],
    # longitude: Annotated[float, typer_argument_longitude_in_degrees],
    # latitude: Annotated[float, typer_argument_latitude_in_degrees],
    # window: Annotated[int, typer_option_spatial_window_in_degrees] = None,
    time: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `time` dimension.",
        ),
    ],
    latitude: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `lat` dimension.",
        ),
    ],
    longitude: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `lon` dimension.",
        ),
    ],
    # tolerance: Annotated[
    #     Optional[float], typer_option_tolerance
    # ] = DATASET_SELECT_TOLERANCE_DEFAULT,
    compression: Annotated[
        str, typer.Option(help="Compression filter")
    ] = COMPRESSION_FILTER_DEFAULT,
    compression_level: Annotated[
        int, typer.Option(help="Compression level")
    ] = COMPRESSION_LEVEL_DEFAULT,
    shuffling: Annotated[str, typer.Option(help=f"Shuffle... ")] = SHUFFLING_DEFAULT,
    # backend: Annotated[RechunkingBackend, typer.Option(help="Backend to use for rechunking. [code]nccopy[/code] [red]Not Implemented Yet![/red]")] = RechunkingBackend.nccopy,
    dask_scheduler: Annotated[
        str, typer.Option(help="The port:ip of the dask scheduler")
    ] = None,
    workers: Annotated[int, typer.Option(help="Number of worker processes.")] = 4,
    memory_limit: Annotated[int, typer.Option(help="Memory limit for the Dask cluster in GB")] = 222,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    1. Read Parquet index via the Zarr engine
    2. Rechunk. Again.
    3. Generate Zarr store
    4. Time speed of reading complete time series over a single geographic location
    """
    # Read Parquet Index

    dataset = read_parquet_via_zarr(
        time_series=time_series,
        variable=variable,
        # longitude=longitude,
        # latitude=latitude,
        # tolerance=tolerance,
    )
    
    # Remove bounds variables if present
    drop_vars = [v for v in ['lat_bnds', 'lon_bnds'] if v in dataset.variables]
    if drop_vars:
        dataset = dataset.drop_vars(drop_vars)

    # Remove the 'bnds' dimension if now unused
    if 'bnds' in dataset.dims and all('bnds' not in var.dims for var in dataset.variables):
        dataset = dataset.drop_dims('bnds')

   # Remove 'bounds' attributes from lat/lon coordinates
    for coord in ['lat', 'lon']:
        if coord in dataset.coords and 'bounds' in dataset[coord].attrs:
            del dataset[coord].attrs['bounds']

    print(f"{dataset=}")


    # In your conversion function:
    dataset = apply_safe_chunking(
        dataset,
        main_variable=variable,
        time_chunks=time,
        lat_chunks=latitude,
        lon_chunks=longitude
    )

    # # Before generating Zarr store
    # for var in dataset.variables:
    #     if var != variable:  # main_variable='SIS'
    #         # Clear conflicting encoding for non-primary variables
    #         dataset[var].encoding.pop('chunks', None)
    #         dataset[var].encoding.pop('compressor', None)

    # # Rechunk
    # dataset = dataset.chunk({'time': time, 'lat': latitude, 'lon': longitude})

    # Generate Zarr store -- Build the Dask task graph
    
    future = generate_zarr_store(
        dataset=dataset,
        store=str(zarr_store),
        time_chunks=time,
        latitude_chunks=latitude,
        longitude_chunks=longitude,
        compute=False,
        consolidate=ZARR_CONSOLIDATE,
        compressor=ZARR_COMPRESSOR,
        mode='w-',
    )

    # Launch a Dask Cluster ?

    # with LocalCluster(
    #     host=DASK_SCHEDULER_IP,
    #     scheduler_port=DASK_SCHEDULER_PORT,
    #     n_workers=workers,
    #     memory_limit=f"{memory_limit}G",
    # ) as cluster:
    #     print(f"   {GREEN_DASH} Connect to local cluster")
        # with Client(cluster) as client:
    with Client(dask_scheduler, n_workers=workers, memory_limit=memory_limit) as client:  # noqa
        print(f'{client=}')
        future = future.persist()
        progress(future)
