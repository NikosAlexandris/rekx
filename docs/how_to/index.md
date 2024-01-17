---
tags:
  - How-To
  - CLI
  - Data
  - SARAH-3
hide:
  - toc
---

!!! abstract "Learn how to ..."

    :material-magnify: Diagnose the structural characteristics of data
    packed in NetCDF/HDF5 with [**`inspect`**](inspect.md) and 
    [**`shapes`**](shapes.md)

    :material-check-all: **`validate`** uniform chunking across multiple files

    :material-lightbulb-question: [**`suggest`**](suggest.md)
    good chunking shapes

    :fontawesome-solid-cubes-stacked: [**`rechunk`**](rechunk.md)
    NetCDF datasets

    Create [**`parquet`**](kerchunk_to_parquet.md) :simple-apacheparquet:
    and JSON :simple-json: [Kerchunk **`reference`** sets](kerchunk_to_json.md)

    :material-vector-combine: **`combine`** Kerchunk reference sets

    :material-select: **`select`** data from Kerchunk reference sets

    :material-speedometer: Get an idea about
    [**`read-performance`**](read_performance.md)
    of data from NetCDF/HDF files and Kerchunk reference sets

!!! info "Data"

    Many examples in this documentation
    use NetCDF files from
    the Surface Solar Radiation Climate Data Record (SARAH-3)[@EUM_SAF_CM_SARAH_V003].

!!! note "Literage programming!"

    The How-To examples are real commands executed at the time of building this
    very documentation.  This ensures that the command output, is indeed what
    you'd really get by installing `rekx`!  This literate programming
    experience is achieved with the use of the wonderful plugin
    [markdown-exec](https://pawamoy.github.io/markdown-exec/).
