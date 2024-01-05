---
tags:
  - How-To
  - rekx
  - CLI
  - Performance
  - read-performance
---

# Read performance

rekx can measure the average time it takes
to read over a geographic location
and load it im memory.
It understands both
Xarray-supported file formats as well as Kerchunk reference sets.

!!! tip
    
    In fact, `rekx` can repeat the reading + loading operation
    as many times as you see fit ! Look out for the `repetitions` parameter.

## NetCDF

``` bash
❯ rekx read-performance SISin202001040000004231000101MA.nc SIS 8 45 -v
Data read in memory in : 0.011 seconds ⚡⚡
<xarray.DataArray 'SIS' (time: 48)>
array([  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,  46, 105, 173, 236, 259, 322, 371, 373, 382, 358, 347,
       311, 267, 205, 147,  74,   9,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0], dtype=int16)
Coordinates:
  * time     (time) datetime64 2020-01-04 ... 2020-01-04T23:30:00
    lon      float32 8.025
    lat      float32 45.03
Attributes:
    _FillValue:     -999
    missing_value:  -999
    standard_name:  surface_downwelling_shortwave_flux_in_air
    long_name:      Surface Downwelling Shortwave Radiation
    units:          W m-2
    cell_methods:   time: point
```

or indeed let the read operation run 100 times

``` bash
❯ rekx read-performance SISin202001040000004231000101MA.nc SIS 8 45 -v --repetitions 100
Data read in memory in : 0.009 seconds ⚡⚡
<xarray.DataArray 'SIS' (time: 48)>
array([  0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
         0,   0,  46, 105, 173, 236, 259, 322, 371, 373, 382, 358, 347,
       311, 267, 205, 147,  74,   9,   0,   0,   0,   0,   0,   0,   0,
         0,   0,   0,   0,   0,   0,   0,   0,   0], dtype=int16)
Coordinates:
  * time     (time) datetime64 2020-01-04 ... 2020-01-04T23:30:00
    lon      float32 8.025
    lat      float32 45.03
Attributes:
    _FillValue:     -999
    missing_value:  -999
    standard_name:  surface_downwelling_shortwave_flux_in_air
    long_name:      Surface Downwelling Shortwave Radiation
    units:          W m-2
    cell_methods:   time: point

```

## JSON

!!! bug "Support for JSON in-progress"

    `read-performance` still needs some refactoring to support JSON Kerchunk
    reference sets !


## Parquet

See [Kerchunking to Parquet](kerchunk_to_parquet.md#verify).
