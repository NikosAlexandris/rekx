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

### A single file

Inspect a single NetCDF file

``` bash
❯ rekx inspect SISin202001010000004231000101MA.nc
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
❯ rekx inspect SISin202001010000004231000101MA.nc --variable-set data
                                                              SISin202001010000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.007

                                    File size: 181550165 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                        * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

!!! hint

    `rekx` can scan selectively for the following `--variable-set`s :
    `[all|coordinates|coordinates-without-data|data|metadata|time]`.
    List them via `rekx inspect --help`.

or even show _humanised_ size figures

``` bash
❯ rekx inspect SISin202001010000004231000101MA.nc --variable-set data --humanize
                                                           SISin202001010000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.010

                                    File size: 173.1 MiB bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                        * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

### A directory with multiple files

Let's consider a directory with 2 NetCDF files

``` bash
❯ ls -1
SISin202001010000004231000101MA.nc
SISin202001020000004231000101MA.nc
```

and inspect them all, in this case scanning only for data variables

``` bash
❯ rekx inspect . --variable-set data

  Name                      Size        Dimensions             Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SISin20200101000000423…   181550165   2 x 48 x 2600 x 2600   SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.011
  SISin20200102000000423…   182167423   2 x 48 x 2600 x 2600   SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.011

                            Dimensions: lat x bnds x time x lon | Cache size in bytes | Number of elements | Preemption strategy ranging in [0, 1] | Average time of 10 reads in seconds
```

!!! info

    The `.` means in Linux the _current_ working directory

By default,
multiple files are reported on a _long table_.
For whatever the reason might be, we night not want this.
We can instead ask for independent tables per input file :

``` bash
❯ rekx inspect . --variable-set data --no-long-table
                                                           SISin202001010000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.014

                                    File size: 181550165 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                        * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
                                                           SISin202001020000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.014

                                    File size: 182167423 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
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

## Consistency

Consider a case where we want _only_ to know
if our NetCDF data are uniformely chunked or not.
No more or less than a _yes_ or a _no_ answer.
`rekx` can [`validate`][rekx.diagnose]
for a uniform chunking shape across multiple NetCDF files.

Let's list some NetCDF files which differ in terms of their chunking shapes :

``` bash
❯ ls -1 *.nc
SISin200001010000004231000101MA_1_2600_2600.nc
SISin202001010000004231000101MA.nc
SISin202001020000004231000101MA.nc
SISin202001030000004231000101MA.nc
SISin202001040000004231000101MA.nc
SRImm201301010000003231000101MA.nc
```

From the file names, we expect to have at least two different chunking shapes.
Let's try first with the files named after a common pattern :

``` bash
❯ rekx validate . --pattern "SIS*MA.nc"
✓ All files are consistently shaped!
```

Indeed, the requested files are chunked identically.
What about the other file `SISin200001010000004231000101MA_1_2600_2600.nc` ?

``` bash
❯ rekx validate .
ValueError: Chunk size mismatch in file 'SISin202001030000004231000101MA.nc' for variable 'time'. Expected (1,) but got (512,)
```

Voilà, this is a _no_ !
