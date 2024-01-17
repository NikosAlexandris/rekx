---
tags:
  - Metadata
  - Dependencies
  - To Do
---

!!! warning

    Complete me!

`rekx` 

- builds its command-line interface on top of the awesome [Typer](https://typer.tiangolo.com/)
- interfaces the [Kerchunk](https://fsspec.github.io/kerchunk/) library
- [netcdf4-python](https://unidata.github.io/netcdf4-python/)
- uses [Xarray](https://docs.xarray.dev/en/stable/) and `zarr` for data handling and storage
<!-- - makes use of `dask` for parallel computing and scalability -->
- uses `numpy` for some numerical operations
- relies on `pandas` for datetime indexing and exporting data to CSV
- wraps over `fastparquet` and `kerchunk`, of course, for specific data format handling

# Code Formatting

`rekx` uses Black for code style consistency throughout the project.
It is setup as a pre-commit hook and run with each git commit.
