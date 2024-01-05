---
tags:
  - Development
  - Programing
  - Design
  - Documentation
  - CLI
  - Ideas
---

# To Do

!!! warning

    While functional, `rekx` needs some :purple_heart: to be able to properly crunch more data chunks!

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

