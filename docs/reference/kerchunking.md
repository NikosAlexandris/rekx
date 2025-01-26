---
tags:
  - To Do
  - Kerchunk
---

# Kerchunk

!!! warning

    Unsorted notes

[kerchunk][kerchunk] supports cloud-friendly access of data
with specific reference to netCDF4/HDF5 files.[^funded-by-nasa]

**How?** Kerchunk

- extracts metadata in a single scan
- arranges multiple chunks from multiple files
- with [dask][dask] and [zarr][zarr],
  reads chunks in [parallel](##Parallel) and/or
  [concurrently](##Concurrency) within a single indexible aggregate dataset

[^funded-by-nasa]: Development supported by NASA fundung [https://doi.org/10.6084/m9.figshare.22266433.v1](https://doi.org/10.6084/m9.figshare.22266433.v1)

[kerchunk]: https://fsspec.github.io/kerchunk/

[dask]: https://www.dask.org/

[zarr]: https://zarr.readthedocs.io/en/stable/

[^parallel]: see [Parallel](##Parallel)

[^concurrently]: see [Concurrency](##Concurrency)


## + advantages

+ supports _parallel_ and _concurrent_ reads  
+ memory efficiency
+ parallel processing
+ data locality


## - drawbacks

- ?


## How does it work?

- Combines `fsspec`, `dask`, and `zarr`

  ```python
  one_day_data = read_chunk("10_year_data_chunked.hdf5", chunk_index=0)
  ```

- **Reference** file :

  ```json
  {
    "version": 1,
    "shapes": {"var1": [365, 24]},
    "refs": {
      "var1/0": ["file_1.nc", "0:24"],
      "var1/1": ["file_2.nc", "0:24"],
      // ...
    }
  }
  ```
!!! seealso

    - [References specification](https://fsspec.github.io/kerchunk/spec.html)


## Real world examples

- [Using Kerchunk with uncompressed NetCDF 64-bit offset files: Cloud-optimized access to HYCOM Ocean Model output on AWS Open Data](https://medium.com/pangeo/using-kerchunk-with-uncompressed-netcdf-64-bit-offset-files-cloud-optimized-access-to-hycom-ocean-9008ba6d0d67)
- [Generate references for HYCOM using kerchunk (Notebook)](https://nbviewer.org/gist/rsignell/932ead1fbf143061bd620e7cf764cbb0)
