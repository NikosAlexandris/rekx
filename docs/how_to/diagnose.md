---
tags:
  - How-To
  - rekx
  - CLI
  - Diagnose
  - inspect
  - shapes
---

# Diagnose data structures

`rekx`
can diagnose the structure of data stored in Xarray-supported file formats.

## Data structure

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

## Chunking shape

The _chunking shape_ refers to the chunk _sizes_ of the variables typicall
found in a NetCDF file, or else any Xarray-supported file format.
`rekx` can scan a `source_directory` for files that match a given `pattern`
and report the chunking shapes across all of them :

``` bash
❯ rekx shapes . --pattern "SIS*.nc" --variable-set data 

  Variable   Shapes            Files                                            Count
 ─────────────────────────────────────────────────────────────────────────────────────
  SIS        1 x 1 x 2600      SISin202001040000004231000101MA.nc ..            4
  SIS        1 x 2600 x 2600   SISin200001010000004231000101MA_1_2600_2600.nc   1
```

### Maximum common chunking shape

It might be useful to know the maximum common chunking shape
across files of a product series, like the SIS or SID products 
from the SARAH3 climate data records. 

Say for example a directory contains the following SARAH3 products :

``` bash
❯ ls -1 data/*.nc
data/SISin200001010000004231000101MA_1_2600_2600.nc
data/SISin202001010000004231000101MA.nc
data/SISin202001020000004231000101MA.nc
data/SISin202001030000004231000101MA.nc
data/SISin202001040000004231000101MA.nc
data/SRImm201301010000003231000101MA.nc
```

`rekx` will fetch the maximum common shapes like so :

!!! warning "Output format subject to change"

    The output format will likely be modified in one single table
    that features both the _Shapes_ and _Common Shape_ columns

``` bash
❯ rekx shapes data --variable-set data --common-shapes

  Variable    Common Shape
 ───────────────────────────────
  SRI         1 x 4 x 401 x 401
  kato_bnds   29 x 2
  SIS         1 x 2600 x 2600


  Variable    Shapes              Files                                            Count
 ────────────────────────────────────────────────────────────────────────────────────────
  SRI         1 x 4 x 401 x 401   SRImm201301010000003231000101MA.nc               1
  kato_bnds   29 x 2              SRImm201301010000003231000101MA.nc               1
  SIS         1 x 1 x 2600        SISin202001030000004231000101MA.nc ..            4
  SIS         1 x 2600 x 2600     SISin200001010000004231000101MA_1_2600_2600.nc   1
```
