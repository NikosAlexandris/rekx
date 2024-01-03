# Diagnose data structures

`rekx`
can diagnose the structure of data stored in Xarray-supported file formats.

## Data structures

Inspect a signle NetCDF file

``` bash
❯ rekx inspect SISin202001010000004231000101MA.nc -v
                                                              SISin202001010000004231000101MA.nc

  Variable        Shape              Chunks         Cache      Elements   Preemption   Type      Scale   Offset   Compression   Level   Shuffling   Read Time
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  lat_bnds        2600 x 2           2600 x 2       16777216   4133       0.75         float32   -       -        zlib          4       False       -
  lon             2600               2600           16777216   4133       0.75         float32   -       -        zlib          4       False       -
  record_status   48                 48             16777216   4133       0.75         int8      -       -        zlib          4       False       -
  lon_bnds        2600 x 2           2600 x 2       16777216   4133       0.75         float32   -       -        zlib          4       False       -
  lat             2600               2600           16777216   4133       0.75         float32   -       -        zlib          4       False       -
  time            48                 512            16777216   4133       0.75         float64   -       -        zlib          4       False       -
  SIS             48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16     -       -        zlib          4       False       0.007

                                        File size: 181550165 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                           * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

Perhaps restrict inspection on data variables only

``` bash
❯ rekx inspect SISin202001010000004231000101MA.nc -v --variable-set data
                                                              SISin202001010000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.007

                                    File size: 181550165 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                        * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

## Chunking shapes

Report chunking shapes across multiple files in the same source directory

``` bash
❯ rekx shapes . --pattern "SIS*.nc" --variable-set data 

  Variable   Shapes            Files                                            Count
 ─────────────────────────────────────────────────────────────────────────────────────
  SIS        1 x 1 x 2600      SISin202001040000004231000101MA.nc ..            4
  SIS        1 x 2600 x 2600   SISin200001010000004231000101MA_1_2600_2600.nc   1
```
