import multiprocessing
from functools import partial
import shlex
import subprocess
import enum
from pathlib import Path
from typing import List, Optional
from abc import ABC, abstractmethod
import netCDF4 as nc
import typer
import xarray as xr
from rich import print
from typing_extensions import Annotated

from rekx.constants import VERBOSE_LEVEL_DEFAULT
from rekx.messages import NOT_IMPLEMENTED_CLI
from rekx.typer_parameters import typer_option_verbose

from .log import logger
from .models import XarrayVariableSet, select_xarray_variable_set_from_dataset
from .typer_parameters import (
    typer_option_dry_run,
    typer_argument_source_path_with_pattern,
    typer_option_output_directory,
    typer_option_filename_pattern,
)

FIX_UNLIMITED_DIMENSIONS_DEFAULT = False
CACHE_SIZE_DEFAULT = 16777216
CACHE_ELEMENTS_DEFAULT = 4133
CACHE_PREEMPTION_DEFAULT = 0.75
COMPRESSION_FILTER_DEFAULT = "zlib"
COMPRESSION_LEVEL_DEFAULT = 4
SHUFFLING_DEFAULT = None
RECHUNK_IN_MEMORY_DEFAULT = False
DRY_RUN_DEFAULT = True
SPATIAL_SYMMETRY_DEFAULT = True


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
    with nc.Dataset(netcdf_file, "r+") as dataset:
        variable = dataset.variables[variable]

        if variable.chunking() != [None]:
            variable.set_auto_chunking(chunk_size)
            print(
                f"Modified chunk size for variable '{variable}' in file '{netcdf_file}' to {chunk_size}."
            )

        else:
            print(
                f"Variable '{variable}' in file '{netcdf_file}' is not chunked. Skipping."
            )


class RechunkingBackendBase(ABC):
    @abstractmethod
    def rechunk(self, input, output_directory, **kwargs):
        pass


class nccopyBackend(RechunkingBackendBase):
    def rechunk(
        self,
        input: Path,
        variables: List[str],
        output_directory: Path,
        time: Optional[int] = None,
        latitude: Optional[int] = None,
        longitude: Optional[int] = None,
        fix_unlimited_dimensions: bool = False,
        cache_size: Optional[int] = CACHE_SIZE_DEFAULT,
        cache_elements: Optional[int] = CACHE_ELEMENTS_DEFAULT,
        cache_preemption: Optional[float] = CACHE_PREEMPTION_DEFAULT,
        compression: str = COMPRESSION_FILTER_DEFAULT,
        compression_level: int = COMPRESSION_LEVEL_DEFAULT,
        shuffling: bool = SHUFFLING_DEFAULT,
        memory: bool = RECHUNK_IN_MEMORY_DEFAULT,
        dry_run: bool = False,  # return command as a string ?
    ):  # **kwargs):
        """
        Options considered for ``nccopy`` :
        [ ] [-k kind_name]
        [ ] [-kind_code]
        [x] [-d n]  # deflate
        [x] [-s]  # shuffling
        [x] [-c chunkspec]  # chunking sizes
        [x] [-u] Convert unlimited size input dimensions to fixed size output dimensions. May speed up variable-at-a-time access, but slow down record-at-a-time access.
        [x] [-w]  # read and process data in-memory, write out in the end
        [x] [-[v|V] var1,...]
        [ ] [-[g|G] grp1,...]
        [ ] [-m bufsize]
        [x] [-h chunk_cache]  #
        [x] [-e cache_elems]  # Number of elements in cache
        [ ] [-r]
        [x] infile
        [x] outfile
        """
        chunking_shape = (
            f"-c time/{time},lat/{latitude},lon/{longitude}"
            if all([time, latitude, longitude])
            else ""
        )
        fixing_unlimited_dimensions = f"-u" if fix_unlimited_dimensions else ""
        compression_options = f"-d {compression_level}" if compression == "zlib" else ""
        shuffling_option = f"-s" if shuffling and compression_level > 0 else ""
        # --------------------------------------------------------------------
        cache_size = f"-h {cache_size} " if cache_size else ""  # cache size in bytes
        cache_elements = f"-e {cache_elements}" if cache_elements else ""
        # cache_preemption = f"-e {cache_preemption}" if cache_preemption else ""
        cache_options = cache_size + cache_elements  # + cache_preemption
        memory_option = f"-w" if memory else ""

        # build the command
        command = "nccopy "  # trailing space is important !
        # if variable_option:
        #     variable_option = f"-v {','.join(variables + [XarrayVariableSet.time])}"  # 'time' required
        #     command += f"{variable_option} "
        command += f"{chunking_shape} "  # trailing space is important !
        command += f"{fixing_unlimited_dimensions} "  # trailing space is important !
        command += f"{compression_options} "  # trailing space is important !
        command += f"{shuffling_option} "  # trailing space is important !
        command += f"{cache_options} "  # trailing space is important !
        command += f"{memory_option} "  # trailing space is important !
        command += f"{input} "  # trailing space is important !
        output_filename = f"{input.stem}"
        output_filename += f"_{time}"
        output_filename += f"_{latitude}"
        output_filename += f"_{longitude}"
        output_filename += f"_{compression}"
        output_filename += f"_{compression_level}"
        if shuffling and compression_level > 0:
            output_filename += f"_shuffled"
        output_filename += f"{input.suffix}"
        output_directory.mkdir(parents=True, exist_ok=True)
        output_filepath = output_directory / output_filename
        command += f"{output_filepath}"

        if dry_run:
            return command

        else:
            output_directory.mkdir(parents=True, exist_ok=True)
            args = shlex.split(command)
            subprocess.run(args)


class NetCDF4Backend(RechunkingBackendBase):
    def rechunk(
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
            logger.info(
                f"No chunking requested for {input_filepath}. Exiting function."
            )
            return

        # logger.info(f"Rechunking of {input_filepath} with chunk sizes: time={time}, lat={lat}, lon={lon}")
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
                    # logger.debug(f"Processing variable: {name}")
                    if name in new_chunks:
                        chunk_size = new_chunks[name]
                        import dask.array as da

                        if chunk_size is not None:
                            # logger.debug(f"Chunking variable `{name}` with chunk sizes: {chunk_size}")
                            x = da.from_array(
                                variable, chunks=(chunk_size,) * len(variable.shape)
                            )
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
                            # logger.debug(f"No chunk sizes specified for `{name}`, copying as is.")
                            output_dataset.createVariable(
                                name, variable.datatype, variable.dimensions
                            )
                            output_dataset[name].setncatts(input_dataset[name].__dict__)
                            output_dataset[name][:] = variable[:]
                    else:
                        # logger.debug(f"Variable `{name}` not in chunking list, copying as is.")
                        output_dataset.createVariable(
                            name, variable.datatype, variable.dimensions
                        )
                        output_dataset[name].setncatts(input_dataset[name].__dict__)
                        output_dataset[name][:] = variable[:]

        # logger.info(f"Completed rechunking from {input_filepath} to {output_filepath}")


class XarrayBackend(RechunkingBackendBase):
    def rechunk_netcdf_via_xarray(
        input_filepath: Path,
        output_filepath: Path,
        time: int = None,
        latitude: int = None,
        longitude: int = None,
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
        chunks = {"time": time, "lat": lat, "lon": lon}
        dataset_rechunked = dataset.chunk(chunks)
        dataset_rechunked.to_netcdf(output_filepath)


@enum.unique
class RechunkingBackend(str, enum.Enum):
    all = "all"
    netcdf4 = "netCDF4"
    xarray = "xarray"
    nccopy = "nccopy"

    @classmethod
    def default(cls) -> "RechunkingBackend":
        """Default rechunking backend to use"""
        return cls.nccopy

    def get_backend(self) -> RechunkingBackendBase:
        """Array type associated to a backend."""

        if self.name == "nccopy":
            return nccopyBackend()

        elif self.name == "netcdf4":
            return NetCDF4Backend()

        elif self.name == "xarray":
            return XarrayBackend()

        else:
            raise ValueError(f"No known backend for {self.name}.")


def rechunk(
    input: Annotated[Optional[Path], typer.Argument(help="Input NetCDF file.")],
    output_directory: Annotated[
        Optional[Path], typer.Argument(help="Path to the output NetCDF file.")
    ],
    time: Annotated[int, typer.Option(help="New chunk size for the `time` dimension.")],
    latitude: Annotated[
        int, typer.Option(help="New chunk size for the `lat` dimension.")
    ],
    longitude: Annotated[
        int, typer.Option(help="New chunk size for the `lon` dimension.")
    ],
    fix_unlimited_dimensions: Annotated[
        bool, typer.Option(help="Convert unlimited size input dimensions to fixed size dimensions in output.")
    ] = FIX_UNLIMITED_DIMENSIONS_DEFAULT,
    variable_set: Annotated[
        XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")
    ] = XarrayVariableSet.all,
    cache_size: Optional[int] = CACHE_SIZE_DEFAULT,
    cache_elements: Optional[int] = CACHE_ELEMENTS_DEFAULT,
    cache_preemption: Optional[float] = CACHE_PREEMPTION_DEFAULT,
    compression: str = COMPRESSION_FILTER_DEFAULT,
    compression_level: int = COMPRESSION_LEVEL_DEFAULT,
    shuffling: str = SHUFFLING_DEFAULT,
    memory: bool = RECHUNK_IN_MEMORY_DEFAULT,
    dry_run: Annotated[bool, typer_option_dry_run] = DRY_RUN_DEFAULT,
    backend: Annotated[
        RechunkingBackend,
        typer.Option(
            help="Backend to use for rechunking. [code]nccopy[/code] [red]Not Implemented Yet![/red]"
        ),
    ] = RechunkingBackend.nccopy,
    dask_scheduler: Annotated[
        str, typer.Option(help="The port:ip of the dask scheduler")
    ] = None,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    Rechunk a NetCDF4 dataset with options to fine tune the output
    """
    if verbose:
        import time as timer

        rechunking_timer_start = timer.time()

    # if dask_scheduler:
    #     from dask.distributed import Client
    #     client = Client(dask_scheduler)
    #     typer.echo(f"Using Dask scheduler at {dask_scheduler}")

    with xr.open_dataset(input, engine="netcdf4") as dataset:
        # with Dataset(input, 'r') as dataset:
        selected_variables = select_xarray_variable_set_from_dataset(
            XarrayVariableSet, variable_set, dataset
        )
        rechunk_parameters = {
            "input": input,
            "variables": selected_variables,
            "output_directory": output_directory,
            "time": time,
            "latitude": latitude,
            "longitude": longitude,
            "fix_unlimited_dimensions": fix_unlimited_dimensions,
            "cache_size": cache_size,
            "cache_elements": cache_elements,
            "cache_preemption": cache_preemption,
            "shuffling": shuffling,
            "compression": compression,
            "compression_level": compression_level,
            "memory": memory,
        }
        backend = backend.get_backend()
        command = backend.rechunk(**rechunk_parameters, dry_run=dry_run)
        if dry_run:
            print(
                f"[bold]Dry run[/bold] the [bold]following command that would be executed[/bold]:"
            )
            print(f"    {command}")
            # print(f"    {rechunk_parameters}")
            return  # Exit for a dry run

        else:
            command_arguments = shlex.split(command)
            try:
                subprocess.run(command_arguments, check=True)
                print(f"Command {command} executed successfully.")
            except subprocess.CalledProcessError as e:
                print(f"An error occurred while executing the command: {e}")

        if verbose:
            rechunking_timer_end = timer.time()
            elapsed_time = rechunking_timer_end - rechunking_timer_start
            logger.debug(f"Rechunking via {backend} took {elapsed_time:.2f} seconds")
            print(f"Rechunking took {elapsed_time:.2f} seconds.")


from typing import Union


def parse_chunks(chunks: Union[int, str]) -> List[int]:
    if isinstance(chunks, str):
        return [int(chunk_size) for chunk_size in chunks.split(",")]
    elif isinstance(chunks, int):
        return [chunks]
    else:
        raise typer.BadParameter("Chunks must be a list of integers.")


def parse_compression_filters(compressing_filters: str) -> List[str]:
    if isinstance(compressing_filters, str):
        return compressing_filters.split(",")
    else:
        raise typer.BadParameter("Compression filters input must be a string")


def parse_numerical_option(input: int) -> List[int]:
    if isinstance(input, int):
        return [input]
    elif isinstance(input, str):
        return [int(property) for property in input.split(",")]
    else:
        raise typer.BadParameter(
            "Input must be a either a single integer or float or a string of comma-separated values."
        )


def parse_float_option(input: float) -> List[float]:
    if isinstance(input, str):
        print(f"This input is a string!")
        return [float(string) for string in input.split(",")]
    return [input]


def callback_compression_filters():
    return ["zlib"]


def generate_rechunk_commands(
    input: Annotated[Path | None, typer.Argument(help="Input NetCDF file.")],
    output: Annotated[
        Path | None, typer.Argument(help="Path to the output NetCDF file.")
    ],
    time: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `time` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    latitude: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `lat` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    longitude: Annotated[
        int | None,
        typer.Option(
            help="New chunk size for the `lon` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    fix_unlimited_dimensions: Annotated[
        bool,
        typer.Option(
            help="Convert unlimited size input dimensions to fixed size dimensions in output."
        ),
    ] = FIX_UNLIMITED_DIMENSIONS_DEFAULT,
    spatial_symmetry: Annotated[
        bool,
        typer.Option(
            help="Add command only for identical latitude and longitude chunk sizes"
        ),
    ] = SPATIAL_SYMMETRY_DEFAULT,
    variable_set: Annotated[
        XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")
    ] = XarrayVariableSet.all,
    cache_size: Annotated[
        int,
        typer.Option(
            help="Cache size", show_default=True, parser=parse_numerical_option
        ),
    ] = CACHE_SIZE_DEFAULT,
    cache_elements: Annotated[
        int,
        typer.Option(help="Number of elements in cache", parser=parse_numerical_option),
    ] = CACHE_ELEMENTS_DEFAULT,
    cache_preemption: Annotated[
        float,
        typer.Option(
            help=f"Cache preemption strategy {NOT_IMPLEMENTED_CLI}",
            parser=parse_float_option,
        ),
    ] = CACHE_PREEMPTION_DEFAULT,
    compression: Annotated[
        str, typer.Option(help="Compression filter", parser=parse_compression_filters)
    ] = COMPRESSION_FILTER_DEFAULT,
    compression_level: Annotated[
        int, typer.Option(help="Compression level", parser=parse_numerical_option)
    ] = COMPRESSION_LEVEL_DEFAULT,
    shuffling: Annotated[bool, typer.Option(help=f"Shuffle... ")] = SHUFFLING_DEFAULT,
    memory: Annotated[
        bool, typer.Option(help="Use the -w flag to nccopy")
    ] = RECHUNK_IN_MEMORY_DEFAULT,
    # backend: Annotated[RechunkingBackend, typer.Option(help="Backend to use for rechunking. [code]nccopy[/code] [red]Not Implemented Yet![/red]")] = RechunkingBackend.nccopy,
    dask_scheduler: Annotated[
        str, typer.Option(help="The port:ip of the dask scheduler")
    ] = None,
    commands_file: Path = "rechunk_commands.txt",
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    Generate variations of rechunking commands based on `nccopy`.
    """
    # Shuffling makes sense only along with compression
    if any([level > 0 for level in compression_level]) and shuffling:
        shuffling = [shuffling, False]
    else:
        shuffling = [False]
    with xr.open_dataset(input, engine="netcdf4") as dataset:
        selected_variables = select_xarray_variable_set_from_dataset(
            XarrayVariableSet, variable_set, dataset
        )
        import itertools

        commands = []
        for (
            chunking_time,
            chunking_latitude,
            chunking_longitude,
            caching_size,
            caching_elements,
            caching_preemption,
            compressing_filter,
            compressing_level,
            shuffling,
        ) in itertools.product(
            time,
            latitude,
            longitude,
            cache_size,
            cache_elements,
            cache_preemption,
            compression,
            compression_level,
            shuffling,
        ):
            backend = RechunkingBackend.nccopy.get_backend()  # hard-coded!
            # Review Me ----------------------------------------------------
            if spatial_symmetry and chunking_latitude != chunking_longitude:
                continue
            else:
                command = backend.rechunk(
                    input=input,
                    variables=list(selected_variables),
                    output_directory=output,
                    time=chunking_time,
                    latitude=chunking_latitude,
                    longitude=chunking_longitude,
                    fix_unlimited_dimensions=fix_unlimited_dimensions,
                    cache_size=caching_size,
                    cache_elements=caching_elements,
                    cache_preemption=caching_preemption,
                    compression=compressing_filter,
                    compression_level=compressing_level,
                    shuffling=shuffling,
                    memory=memory,
                    dry_run=True,  # just return the command!
                )
                if not command in commands:
                    commands.append(command)

    commands_file = Path(
        commands_file.stem + "_for_" + input.stem + commands_file.suffix
    )
    if verbose:
        print(
            f"[bold]Writing generated commands into[/bold] [code]{commands_file}[/code]"
        )
        for command in commands:
            print(f" [green]>[/green] [code dim]{command}[/code dim]")

    if not dry_run:
        with open(commands_file, "w") as f:
            for command in commands:
                f.write(command + "\n")
    # else:
    #     print(commands)


def generate_rechunk_commands_for_multiple_netcdf(
    source_path: Annotated[Path, typer_argument_source_path_with_pattern],
    time: Annotated[
        int,
        typer.Option(
            help="New chunk size for the `time` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    latitude: Annotated[
        int,
        typer.Option(
            help="New chunk size for the `lat` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    longitude: Annotated[
        int,
        typer.Option(
            help="New chunk size for the `lon` dimension.",
            parser=parse_numerical_option,
        ),
    ],
    fix_unlimited_dimensions: Annotated[
        bool,
        typer.Option(
            help="Convert unlimited size input dimensions to fixed size dimensions in output."
        ),
    ] = FIX_UNLIMITED_DIMENSIONS_DEFAULT,
    pattern: Annotated[str, typer_option_filename_pattern] = "*.nc",
    output_directory: Annotated[Path, typer_option_output_directory] = Path('.'),
    spatial_symmetry: Annotated[
        bool,
        typer.Option(
            help="Add command only for identical latitude and longitude chunk sizes"
        ),
    ] = SPATIAL_SYMMETRY_DEFAULT,
    variable_set: Annotated[
        XarrayVariableSet, typer.Option(help="Set of Xarray variables to diagnose")
    ] = XarrayVariableSet.all,
    cache_size: Annotated[
        int,
        typer.Option(
            help="Cache size", show_default=True, parser=parse_numerical_option
        ),
    ] = CACHE_SIZE_DEFAULT,
    cache_elements: Annotated[
        int,
        typer.Option(help="Number of elements in cache", parser=parse_numerical_option),
    ] = CACHE_ELEMENTS_DEFAULT,
    cache_preemption: Annotated[
        float,
        typer.Option(
            help=f"Cache preemption strategy {NOT_IMPLEMENTED_CLI}",
            parser=parse_float_option,
        ),
    ] = CACHE_PREEMPTION_DEFAULT,
    compression: Annotated[
        str, typer.Option(help="Compression filter", parser=parse_compression_filters)
    ] = COMPRESSION_FILTER_DEFAULT,
    compression_level: Annotated[
        int, typer.Option(help="Compression level", parser=parse_numerical_option)
    ] = COMPRESSION_LEVEL_DEFAULT,
    shuffling: Annotated[
        bool,
        typer.Option(
            help=f"Shuffle... [reverse bold orange] Testing [/reverse bold orange]"
        ),
    ] = SHUFFLING_DEFAULT,
    memory: bool = RECHUNK_IN_MEMORY_DEFAULT,
    # backend: Annotated[RechunkingBackend, typer.Option(help="Backend to use for rechunking. [code]nccopy[/code] [red]Not Implemented Yet![/red]")] = RechunkingBackend.nccopy,
    dask_scheduler: Annotated[
        str, typer.Option(help="The port:ip of the dask scheduler")
    ] = None,
    commands_file: Path = "rechunk_commands.txt",
    workers: Annotated[int, typer.Option(help="Number of worker processes.")] = 4,
    dry_run: Annotated[bool, typer_option_dry_run] = False,
    verbose: Annotated[int, typer_option_verbose] = VERBOSE_LEVEL_DEFAULT,
):
    """
    Generate variations of rechunking commands based on `nccopy`.
    """
    input_file_paths = []
    if source_path.is_file():
        input_file_paths.append(source_path)

    elif source_path.is_dir():
        input_file_paths = list(source_path.glob(pattern))

    else:
        print(f'Something is wrong with the [code]source_path[/code] input.')
        return

    if not list(input_file_paths):
        print(
            f"No files found in [code]{source_path}[/code] matching the pattern [code]{pattern}[/code]!"
        )
        return

    if dry_run:
        print(f"[bold]Dry running operations that would be performed[/bold]:")
        print(
            f"> Reading files in [code]{source_path}[/code] matching the pattern [code]{pattern}[/code]"
        )
        print(f"> Number of files matched : {len(list(input_file_paths))}")
        print(f"> Writing rechunking commands in [code]{commands_file}[/code]")
        return  # Exit for a dry run

    if input_file_paths and not output_directory.exists():
        output_directory.mkdir(parents=True, exist_ok=True)
        if verbose > 0:
            print(f"[yellow]Convenience action[/yellow] : creating the requested output directory [code]{output_directory}[/code].")
    with multiprocessing.Pool(processes=workers) as pool:
        partial_generate_rechunk_commands = partial(
                generate_rechunk_commands,
                output=output_directory,
                time=time,
                latitude=latitude,
                longitude=longitude,
                fix_unlimited_dimensions=fix_unlimited_dimensions,
                spatial_symmetry=spatial_symmetry,
                variable_set=variable_set,
                cache_size=cache_size,
                cache_elements=cache_elements,
                cache_preemption=cache_preemption,
                compression=compression,
                compression_level=compression_level,
                shuffling=shuffling,
                memory=memory,
                dask_scheduler=dask_scheduler,
                commands_file=commands_file,
                dry_run=dry_run,
                verbose=verbose,
        )
        pool.map(partial_generate_rechunk_commands, input_file_paths)
    if verbose:
        print(f"[bold green]Done![/bold green]")
