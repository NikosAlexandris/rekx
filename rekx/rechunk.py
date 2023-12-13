from devtools import debug
from typing_extensions import Annotated
from typing import Any
from typing import Optional
from datetime import datetime
from threading import Lock
import typer
from .typer_parameters import OrderCommands
from .log import logger
from pathlib import Path
import xarray as xr
import netCDF4 as nc
from enum import Enum
from .typer_parameters import typer_option_dry_run
from rekx.typer_parameters import typer_option_verbose
from rekx.constants import VERBOSE_LEVEL_DEFAULT
from .rich_help_panel_names import rich_help_panel_rechunking
from .models import RechunkingBackend
from rich import print
# from rekx.messages import NOT_IMPLEMENTED_CLI


# app = typer.Typer(
#     cls=OrderCommands,
#     add_completion=True,
#     add_help_option=True,
#     rich_markup_mode="rich",
#     help=f'Rechunk data',
# )


# @app.command(
#     'modify-chunk-size',
#     no_args_is_help=True,
#     help=f'Modify chunk size in NetCDF files {NOT_IMPLEMENTED_CLI}',
# )
def modify_chunk_size(
    netcdf_file,
    variable,
    chunk_size,
):
    """
    Modify the chunk size of a variable in a NetCDF file.
    
    Parameters:
    - nc_file: path to the NetCDF file
    - variable_name: name of the variable to modify
    - new_chunk_size: tuple specifying the new chunk size, e.g., (2600, 2600)
    """
    with nc.Dataset(netcdf_file, 'r+') as ds:
        var = ds.variables[variable]
        
        if var.chunking() != [None]:
            var.set_auto_chunking(chunk_size)
            print(f"Modified chunk size for variable '{variable}' in file '{netcdf_file}' to {chunk_size}.")

        else:
            print(f"Variable '{variable}' in file '{netcdf_file}' is not chunked. Skipping.")


def rechunk_netcdf_via_netCDF4(
    input_filepath: Path, 
    output_filepath: Path, 
    time: int = None,
    lat: int = None,
    lon: int = None,
) -> None:
    """Rechunk data stored in a NetCDF4 file.

    Notes
    -----
    Text partially quoted from

    https://unidata.github.io/netcdf4-python/#netCDF4.Dataset.createVariable :

    The function `createVariable()` available through the `netcdf4-python`
    python interface to the netCDF C library, features the optional keyword
    `chunksizes` which can be used to manually specify the HDF5 chunk sizes for
    each dimension of the variable.

    A detailed discussion of HDF chunking and I/O performance is available at
    https://support.hdfgroup.org/HDF5/doc/Advanced/Chunking/. The default
    chunking scheme in the netcdf-c library is discussed at
    https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html.

    Basically, the chunk size for each dimension should match as closely as
    possible the size of the data block that users will read from the file.
    `chunksizes` cannot be set if `contiguous=True`.
    """
    # Check if any chunking has been requested
    if time is None and lat is None and lon is None:
        logger.info(f"No chunking requested for {input_filepath}. Exiting function.")
        return

    logger.info(f"Rechunking of {input_filepath} with chunk sizes: time={time}, lat={lat}, lon={lon}")
    new_chunks = {"time": time, "lat": lat, "lon": lon}
    with nc.Dataset(input_filepath, mode="r") as input_dataset:
        with nc.Dataset(output_filepath, mode="w") as output_dataset:
            for name in input_dataset.ncattrs():
                output_dataset.setncattr(name, input_dataset.getncattr(name))
            for name, dimension in input_dataset.dimensions.items():
                output_dataset.createDimension(
                    name, (len(dimension) if not dimension.isunlimited() else None)
                )
            for name, variable in input_dataset.variables.items():
                logger.debug(f"Processing variable: {name}")
                if name in new_chunks:
                    chunk_size = new_chunks[name]
                    import dask.array as da

                    if chunk_size is not None:
                        logger.debug(f"Chunking variable `{name}` with chunk sizes: {chunk_size}")
                        x = da.from_array(
                            variable, chunks=(chunk_size,) * len(variable.shape)
                        )
                        debug(locals())
                        output_dataset.createVariable(
                            name,
                            variable.datatype,
                            variable.dimensions,
                            zlib=True,
                            complevel=4,
                            chunksizes=(chunk_size,) * len(variable.shape),
                        )
                        output_dataset[name].setncatts(input_dataset[name].__dict__)
                        output_dataset[name][:] = x
                    else:
                        logger.debug(f"No chunk sizes specified for `{name}`, copying as is.")
                        output_dataset.createVariable(name, variable.datatype, variable.dimensions)
                        output_dataset[name].setncatts(input_dataset[name].__dict__)
                        output_dataset[name][:] = variable[:]
                else:
                    logger.debug(f"Variable `{name}` not in chunking list, copying as is.")
                    output_dataset.createVariable(name, variable.datatype, variable.dimensions)
                    output_dataset[name].setncatts(input_dataset[name].__dict__)
                    output_dataset[name][:] = variable[:]

    logger.info(f"Completed rechunking from {input_filepath} to {output_filepath}")


def rechunk_netcdf_via_xarray(
    input_filepath: Path, 
    output_filepath: Path, 
    time: int = typer.Option(None, help="New chunk size for the 'time' dimension."),
    lat: int = typer.Option(None, help="New chunk size for the 'lat' dimension."),
    lon: int = typer.Option(None, help="New chunk size for the 'lon' dimension."),
) -> None:
    """
    Rechunk a NetCDF dataset and save it to a new file.

    Parameters
    ----------
    input_filepath : Path
        The path to the input NetCDF file.
    output_filepath : Path
        The path to the output NetCDF file where the rechunked dataset will be saved.
    chunks : Dict[str, Union[int, None]]
        A dictionary specifying the new chunk sizes for each dimension. 
        Use `None` for dimensions that should not be chunked.
    
    Returns
    -------
    None
        The function saves the rechunked dataset to `output_filepath`.

    Examples
    --------
    # >>> rechunk_netcdf(Path("input.nc"), Path("output.nc"), {'time': 365, 'lat': 25, 'lon': 25})
    """
    dataset = xr.open_dataset(input_filepath)
    chunks = {'time': time, 'lat': lat, 'lon': lon}
    dataset_rechunked = dataset.chunk(chunks)
    dataset_rechunked.to_netcdf(output_filepath)


# @app.command(
#     "rechunk",
#     no_args_is_help=True,
#     help="Rechunk a NetCDF file and save it to a new file.",
#     rich_help_panel=rich_help_panel_rechunking,
# )
def rechunk(
    input: Annotated[Optional[Path], typer.Argument(help="Input NetCDF file.")] = None,
    output: Annotated[Optional[Path], typer.Argument(help="Path to the output NetCDF file.")] = None,
    time: Annotated[int, typer.Option(help="New chunk size for the `time` dimension.")] = None,
    lat: Annotated[int, typer.Option(help="New chunk size for the `lat` dimension.")] = None,
    lon: Annotated[int, typer.Option(help="New chunk size for the `lon` dimension.")] = None,
    backend: Annotated[RechunkingBackend, typer.Option(help="Backend to use for rechunking. [code]nccopy[/code] [red]Not Implemented Yet![/red]")] = RechunkingBackend.nccopy,
    dask_scheduler: Annotated[str, typer.Option(help="The port:ip of the dask scheduler")] = None,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """ """
    if verbose:
        import time as timer
        rechunking_timer_start = timer.time()

    if dask_scheduler:
        from dask.distributed import Client
        client = Client(dask_scheduler)
        typer.echo(f"Using Dask scheduler at {dask_scheduler}")

    if dry_run:
        print(f"[bold]Dry run[/bold] of [bold]operations that would be performed[/bold]:")
        print(f"> Input file [code]{input}[/code]")
        print(f"> Target chunking shape : {time}, {lat}, {lon}")
        print(f"> Output file [code]{output}[/code]")
        print(f"> Rechunking via {backend}")
        return  # Exit for a dry run

    if backend == 'xarray':
        rechunk_netcdf_via_xarray(Path(input), Path(output), time, lat, lon)
    elif backend == 'netCDF4':
        rechunk_netcdf_via_netCDF4(Path(input), Path(output), time, lat, lon)
    else:
        raise ValueError(f"Unsupported backend: {backend}")

    if verbose:
        rechunking_timer_end = timer.time()
        elapsed_time = rechunking_timer_end - rechunking_timer_start
        logger.debug(f"Rechunking via {backend} took {timer_end - timer_start:.2f} seconds")
        print(f"Rechunking took {elapsed_time:.2f} seconds.")


if __name__ == "__main__":
    app()
