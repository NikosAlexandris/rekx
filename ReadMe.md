# rekx 🦖

![Under Heavy Development](https://img.shields.io/badge/Under%20Heavy%20Development-purple?style=for-the-badge)

![License](https://img.shields.io/badge/License-EUPL--1.2-blue.svg)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/NikosAlexandris/rekx)
![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=flat&logo=MaterialForMkDocs&logoColor=white)
[![Documentation](https://img.shields.io/badge/Documentation-Available-green.svg)](https://nikosalexandris.github.io/rekx/)

[^*] <img align="right" width="300" height="300" src="rekx_draft_logo_72dpi.png">
<!-- ![rekx](rekx_draft_logo_72dpi.png)[^*] -->
[^*]: <a href="https://www.freepik.com/free-vector/hand-drawn-dinosaur-outline-illustration_58593460.htm#query=trex&position=47&from_view=search&track=sph&uuid=27caf12e-35ea-47ad-a113-2d4f5981f58f">Original T-Rex drawn by pikisuperstar</a> on Freepik

`rekx` seamlessly interfaces
the [Kerchunk](https://fsspec.github.io/kerchunk/) library
in an interactive way through the command line.
It assists in creating virtual aggregate datasets,
also known as Kerchunk reference sets,
which allows for an efficient, parallel and cloud-friendly way
to access data in-situ without duplicating the original datasets.

More than a functional tool,
`rekx` serves an educational purpose on matters around
chunking, compression and efficient data reading
from common scientific file formats such as NetCDF
used extensively to store large time-series.
While there is abundant documentation on such topics,
it is often highly technical
and oriented towards developers,
`rekx` tries to simplify these concepts through practical examples.

Similarly,
existing tools for managing HDF and NetCDF data,
such as `cdo`, `nco`, and others,
often have overlapping functionalities
and present a steep learning curve for non-experts.
`rekx` focuses on practical aspects of efficient data access
trying to simplify these processes.
It features simple command line tools
to diagnose data structures,
validate uniform chunking across files,
suggest good chunking shapes and parameterise the rechunking of datasets,
create and aggregate Kerchunk reference sets
and time data read operations.

`rekx` dedicates to practicality, simplicity, and essence.

***Interested ? Head over to the [documentation](https://nikosalexandris.github.io/rekx/).***

## To Do

- [ ] Complete backend for rechunking, support for 
    - [ ] NetCDF4
    - [ ] Xarray
    - [ ] `nccopy`
- [ ] Simplify command line interface
    - [ ] merge "multi" commands to single/simple ones ?
    - [ ] make `common-shape` and `validate` options to `shapes` ?
    - [ ] clean non-sense `suggest-alternative` command or merge to `suggest`
    - [ ] merge `reference-parquet` to `reference`
    - [ ] as above, same for/with `combine` commands
    - [ ] does a sepatate `select-fast` make sense ?
    - [ ] review various select/read commands
- [ ] Go through :
    - [ ] https://peps.python.org/pep-0314/
    - [ ] ?
- [ ] Write clean and meaningful docstrings for each and every function
- [ ] Pytest each and every (?) function
- [ ] Packaging
- [ ] Documentation
    - [x] Use https://squidfunk.github.io/mkdocs-material/
    - [ ] Simple examples
        - [ ] Diagnose
        - [ ] Suggest
        - [ ] Rechunk
        - [x] Kerchunk
            - [x] JSON
                - [x] Create references
                - [x] Combine references
                - [x] Read data from aggregated reference and load in memory
            - [x] Parquet
                - [x] Create references
                - [x] Combine references
                - [x] Read data from aggregated reference and load in memory
                - [ ] Pending issue [https://github.com/fsspec/kerchunk/issues/345#issuecomment-1807349725](https://github.com/fsspec/kerchunk/issues/345#issuecomment-1807349725)
        - [ ] Select (aka read)
            - [ ] From Xarray-supported datasets
            - [ ] From Kerchunk references
    - [ ] Tutorial
        - [ ] Rechunking and Kerchunking SARAH3 products
    - [ ] Add visuals to [Concepts](reference/concepts.md)
