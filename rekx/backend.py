import enum
from abc import ABC, abstractmethod
from pathlib import Path
from typing_extensions import List, Optional

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


class RechunkingBackendBase(ABC):
    @abstractmethod
    def rechunk(self, input_filepath, output_directory, **kwargs):
        pass


class nccopyBackend(RechunkingBackendBase):
    def rechunk(
        self,
        input_filepath: Path,
        variables: List[str],
        output_directory: Path,
        time: int | None = None,
        latitude: int | None = None,
        longitude: int | None = None,
        fix_unlimited_dimensions: bool = False,
        cache_size: int | None = CACHE_SIZE_DEFAULT,
        cache_elements: int | None = CACHE_ELEMENTS_DEFAULT,
        cache_preemption: float | None = CACHE_PREEMPTION_DEFAULT,
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
        variable_option = f"-v {','.join(variables)}" if variables else "" # 'time' required
        chunking_shape = (
            f"-c time/{time},lat/{latitude},lon/{longitude}"
            if all([time, latitude, longitude])
            else ""
        )
        fixing_unlimited_dimensions = f"-u" if fix_unlimited_dimensions else ""
        compression_options = f"-d {compression_level}" if compression == "zlib" else ""
        shuffling_option = f"-s" if shuffling and compression_level > 0 else ""
        cache_size_option = f"-h {cache_size} " if cache_size else ""  # cache size in bytes
        cache_elements_option = f"-e {cache_elements}" if cache_elements else ""
        memory_option = f"-w" if memory else ""

        # Collect all non-empty options into a list
        options = [
            variable_option,
            chunking_shape,
            fixing_unlimited_dimensions,
            compression_options,
            shuffling_option,
            cache_size_option,
            cache_elements_option,
            memory_option,
            input_filepath,
        ]
        # Build the command by joining non-empty options
        command = "nccopy " + " ".join(filter(bool, options)) + " "

        # Build the output file path
        output_filename = f"{Path(input_filepath).stem}"
        output_filename += f"_{time}"
        output_filename += f"_{latitude}"
        output_filename += f"_{longitude}"
        output_filename += f"_{compression}"
        output_filename += f"_{compression_level}"
        if shuffling and compression_level > 0:
            output_filename += f"_shuffled"
        output_filename += f"{Path(input_filepath).suffix}"
        output_directory.mkdir(parents=True, exist_ok=True)
        output_filepath = output_directory / output_filename
        command += f"{output_filepath}"

        if dry_run:
            return command

        else:
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



