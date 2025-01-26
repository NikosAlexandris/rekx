---
tags:
  - Tutorials
  - Analysis
  - SARAH3
  - SIS
  - Chunking
  - Rechunk
  - rekx
  - CLI
---

# Chunking SARAH3 time series

Following we explore the data structure of products from the SARAH3
climate data records produced by DWD and distributed as NetCDF files.

> **Note** : **This is a Work-in-Progress and subject to all kinds of changes!**

#### Tools

In this tutorial we will refer to the following tools : 

---

- `gdalinfo` & Co
- [`rekx`][rekx]
- `nccopy`
- `ncdump`
- Python library [`netCDF4`][netcdf4]

---

[netcdf4]: https://unidata.github.io/netcdf4-python/

[rekx]: https://github.com/NikosAlexandris/rekx

### Data Structure

Following we work with

``` bash
❯ ls -1A  /project/home/p200206/data/sis/netcdf/*.nc |wc -l
8388
```

number of NetCDF files.

Let's warm-up by examining a single file from the SARAH3 collection.
Using `gdalinfo` or `ncdump -h` we can get some basic information :

``` bash
...
```

#### Chunking Shapes

The original SARAH3 climate data records stored in netCDF files
are not shaped in a uniform way across the entire time series.
Using [`rekx`][rekx]
we can diagnose the _chunking shapes_ of SIS products.

Let's do this for $23$ $years$ of data starting from $2000$

``` bash
❯ ls -1A  /project/home/p200206/data/sis/netcdf/*.nc |head -3
/project/home/p200206/data/sis/netcdf/SISin200001010000004231000101MA.nc
/project/home/p200206/data/sis/netcdf/SISin200001020000004231000101MA.nc
/project/home/p200206/data/sis/netcdf/SISin200001030000004231000101MA.nc
```

up to and including $2022$

``` bash
❯ ls -1A  /project/home/p200206/data/sis/netcdf/*.nc |tail -3
/project/home/p200206/data/sis/netcdf/SISin2022122900000042310001I1MA.nc
/project/home/p200206/data/sis/netcdf/SISin2022123000000042310001I1MA.nc
/project/home/p200206/data/sis/netcdf/SISin2022123100000042310001I1MA.nc
```

as follows : 

``` bash
❯ rekx shapes /project/home/p200206/data/sid/netcdf/

  Variable        Shapes            Files                                   Count
 ─────────────────────────────────────────────────────────────────────────────────
  lon             2600              SISin200303090000004231000101MA.nc ..   8388
  lon_bnds        2600 x 2          SISin200303090000004231000101MA.nc ..   8388
  record_status   48                SISin200303090000004231000101MA.nc ..   8387
  record_status   4096              SISin2021110600000042310001I1MA.nc      1
  SIS             1 x 1 x 2600      SISin202010250000004231000101MA.nc ..   5434
  SIS             1 x 1300 x 1300   SISin200206230000004231000101MA.nc ..   2224
  SIS             1 x 2600 x 2600   SISin2021112700000042310001I1MA.nc ..   730
  lat             2600              SISin200303090000004231000101MA.nc ..   8388
  time            512               SISin2021020700000042310001I1MA.nc ..   6164
  time            524288            SISin200206230000004231000101MA.nc ..   2224
  lat_bnds        2600 x 2          SISin200303090000004231000101MA.nc ..   8388
```

We can read in the resulting table
the mixture of chunking shapes
within the same series of product/variable, namely `SIS`.
This is not uncommon in automatic workflows
that may run on some supercomputing facility.
Individual processes are sent to computing nodes with different specifications
and an _optimal_ chunking shape is selected
likely and mostly depending on available free memory given to the process.

> In the above table, the Files column presents the first of the files matching
> the requested pattern, in which case it is the default pattern `*.nc`.
> Find out more via `rekx shapes --help` or simply `rekx shapes`.

We can restrict the scan
by using the `--variable-set` option
and ask for `data` variables,
i.e. excluding _coordinates_[^1]
or other non-data _dimensions_[^2] in the NetCDF file :

``` bash
❯ rekx shapes /project/home/p200206/data/sis/netcdf/ --variable-set data

  Variable   Shapes            Files                                   Count
 ────────────────────────────────────────────────────────────────────────────
  SIS        1 x 1 x 2600      SISin200712100000004231000101MA.nc ..   5434
  SIS        1 x 1300 x 1300   SISin200310120000004231000101MA.nc ..   2224
  SIS        1 x 2600 x 2600   SISin2022100200000042310001I1MA.nc ..   730
```

Similar for SID _data_ :

``` bash
❯ rekx shapes /project/home/p200206/data/sid/netcdf/ --variable-set data

  Variable   Shapes            Files                                   Count
 ────────────────────────────────────────────────────────────────────────────
  SID        1 x 1 x 2600      SIDin201312270000004231000101MA.nc ..   5081
  SID        1 x 1300 x 1300   SIDin200303090000004231000101MA.nc ..   2224
```

> The `--variable-set` understands the following sets of Xarray variables :
> `[all|coordinates|coordinates-without-data|data|metadata|time]`

We can also scan the chunking shapes of _time_ coordinates : 

``` bash
❯ rekx shapes /project/home/p200206/data/sid/netcdf/ --variable-set time

  Variable   Shapes   Files                                   Count
 ───────────────────────────────────────────────────────────────────
  time       524288   SIDin200005200000004231000101MA.nc ..   2224
  time       512      SIDin201101240000004231000101MA.nc ..   5081
```

This result is somehow difficult to understand and we can indeed inspect these
in more detail in the following section.

[^1]: _coordinates_ has a special meaning in Xarray
[^2]: _dimensions_ has _different meanings_ between Xarray and the netCDF4
    Python library

Finally,
let's have a look in the structure of the now-retired SRI products
from the SARAH2 collection :

``` bash
❯ rekx shapes /project/home/p200206/data/sri/netcdf/ --variable-set data

  Variable    Shapes              Files                                   Count
 ───────────────────────────────────────────────────────────────────────────────
  SRI         1 x 4 x 401 x 401   SRImm199801010000003231000101MA.nc ..   420
  kato_bnds   29 x 2              SRImm199801010000003231000101MA.nc ..   420
```

---

> **Notes**
>
> Uniform chunking shapes along the entire time series of a product,
> can be a choice to better serve specific access patterns.

---

#### One step back : structure of a single NetCDF file

Besides the chunking shape `1 x 1 x 2600`,
other important aspects are obviously
the **data type** and eventually **scaling** and **offset** factors,
internal **chunk caching**,
**compression** and **shuffling**.

##### Compression & Caching

While all options may be important in some context,
_compression_ has a direct and measurable impact
on the reading and writing speed.
On the other hand,
the size of the internal _cache_,
the number of elements
and the preemption strategy for cached chunks,
affects reading times in a repetitive data-access context,
for example processing or just serving data through some application.

In the [manual for `nccopy`][nccopy]
the level of compression is referred to as _deflation level_ .
`0` corresponds to no compression and `9` to maximum compression,
The compression depends also the chunking configuration.
In fact, a compressed variable (in a NetCDF file) _must be chunked_.[^3]

[^3]: Interesting details are discussed in [ NetCDF Compression][netcdf_compression]

[netcdf_compression]: https://www.unidata.ucar.edu/blogs/developer/en/entry/netcdf_compression

[nccopy]: https://docs.unidata.ucar.edu/nug/current/netcdf_utilities_guide.html#guide_nccopy

###### Inspecting a single file

**Chunking shape**

To get a better idea of the structural components that matter,
we can use `rekx inspect` : 

``` bash
❯ rekx inspect SISin202001030000004231000101MA.nc --variable SIS -v  --variable-set data
                                            SISin202001030000004231000101MA.nc

  Variable   Shape              Chunks         Cache*                   Type    Scale   Offset   Compression   Shuffling   Read Time
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216 x 4133 x 0.75   int16   -       -        zlib: 4       -           0.014

                           File size: 182379797 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                               * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

**More metadata**

Aside the chunking shape,
this file

- has default caching options pre-set :
  - size in bytes : `16777216`
  - number of elements : `4133`
  - preemption strategy factor : `0.75`
- is of signed integer `int16` type
- is compressed with `zlib` and level `4`

> **Reading time**
>
>Note also the last reported value : $0.014$ seconds,
>which is the reading time of the complete time series
>over a [random/specific **FixMe**] location (here longitude = 8, latitude = 45).
>
> *Further discussed in the following sections.*

##### Inspecting multiple Files


``` bash
❯ rekx inspect-multiple . --pattern "SIS*.nc" --variable-set data --csv netcdf_inspection.csv
                                                  SISin202001040000004231000101MA.nc

  Variable   Shape              Chunks         Cache*                   Type    Scale   Offset   Compression   Shuffling   Read Time
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216 x 4133 x 0.75   int16   -       -        zlib: 4       -           0.020

                           File size: 181921207 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                               * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
                                                  SISin202001030000004231000101MA.nc

  Variable   Shape              Chunks         Cache*                   Type    Scale   Offset   Compression   Shuffling   Read Time
 ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216 x 4133 x 0.75   int16   -       -        zlib: 4       -           0.020

                           File size: 182379797 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                               * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

and the output CSV file
which is one of the most common machine-readable file format,
_easy_ for post-processing with tools like [Miller][miller]:

[miller]: https://miller.readthedocs.io/

```
File Name,Variable,Shape,Chunks,Cache,Type,Scale,Offset,Compression,Shuffling,Read Time
SISin202001040000004231000101MA.nc,SIS,48 x 2600 x 2600,1 x 1 x 2600,16777216 x 4133 x 0.75,int16,-,-,zlib: 4,-,0.020
SISin202001030000004231000101MA.nc,SIS,48 x 2600 x 2600,1 x 1 x 2600,16777216 x 4133 x 0.75,int16,-,-,zlib: 4,-,0.020
```


<details>
<summary>One more example on the SID product and its time variable</summary>
<br>
 
Following are the first 10 lines from inspecting the structure of the time variables

```bash
❯ head rekx_inspect_multiple_sarah3_sid_netcdf_time_variables  -n 13

  Name                                 Size        Dimensions             Variable   Shape   Chunks   Cache*                   Type      Scale   Offset   Compression   Shuffling   Read Time
 ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIDin201404160000004231000101MA.nc   164196658   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin201708220000004231000101MA.nc   156170619   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin200901090000004231000101MA.nc   86572475    2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin200801190000004231000101MA.nc   158217045   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin201312280000004231000101MA.nc   162279218   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin201506140000004231000101MA.nc   158821070   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin200205050000004231000101MA.nc   141475008   2 x 48 x 2600 x 2600   time       48      524288   16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin200008140000004231000101MA.nc   142813391   2 x 48 x 2600 x 2600   time       48      524288   16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin201406230000004231000101MA.nc   160036830   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
  SIDin201806010000004231000101MA.nc   161138656   2 x 48 x 2600 x 2600   time       48      512      16777216 x 4133 x 0.75   float64   -       -        zlib: 4       -           -
```

Indeed there are at least two chunk sizes for the _time_ variable in SID
products : $512$ and $524288$.

Why is that so ?

</details>


### Baseline

**Initial Read Test**

We can see the structural differences
reflected in the time required to read such data.
We will read the time series using xarray without any chunking
or additional optimizations.

``` bash
rekx read
```

At this point we adopt these timings as a baseline for comparison.

- **Basic File Details**:

1. Time reading the entire series over specific locations
2. Note the file size and any other relevant metadata

### Rechunking

#### Chunks sizes

First,
we experiment with rechunking the original data in a series of target chunking shapes.
We start with `1 x 2600 x 2600` as the base case which is merely a simple copy.

This work is primarily motivated by the need for efficient access
to massive time series,
both for processing and serving data through the web.
Hence,
we focus in chunking first along the time dimension
as well as combinations of latitude and longitude.

* Measuring the time required for rechunking and the time it takes to read the rechunked data.

#### Compression [ToDo]

After selecting a _good_ chunking shape, we can experiment with compression and measure the impact on read times.

> Compression is controlled via the `-d` option in nccopy

* Test different compression levels to balance read performance and file size.

#### Caching [ToDo]

We experiment with internal netCDF caching options (`-h` and `-e`). Measure if caching improves read performance for your specific use case.

#### Additional Parameters [ToDo]

**Shuffling**

Test if enabling shuffling (`-s` option) alongside compression affects performance.

**Memory Buffer Size**

Experiment with different memory buffer sizes (`-m` option) to see if it influences read speeds.

### Automated & Parallel Rechunking

``` bash
SOURCE_DIRECTORY="/project/home/p200206/data/sis/chunks_1_2600_2600"
OUTPUT_DIRECTORY="/project/home/p200206/data/sis/rechunking"
❯ rekx rechunk-generator \
  "$SOURCE_DIRECTORY"/SISin200001010000004231000101MA_1_2600_2600.nc \
  "$OUTPUT_DIRECTORY" \
   --time 1,12,24,48 \
   --latitude 64,128,256,512,1024,2048,325,650,1300,2600 \
   --longitude 64,128,256,512,1024,2048,325,650,1300,2600 \
   --variable-set data \
   --compression-level 0,3,6,9 \
   --spatial-symmetry
```

genrates commands with combinations of parameters for rechunking in a text file
like 

``` bash
nccopy -v SIS,time -c time/1,lat/64,lon/64 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_64_64_zlib_0.nc
```

<details>
<summary>Rechunking commands</summary>
<br>

``` bash
nccopy -v SIS,time -c time/1,lat/64,lon/64 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_64_64_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/64,lon/64 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_64_64_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/64,lon/64 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_64_64_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/64,lon/64 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_64_64_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/128,lon/128 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_128_128_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/128,lon/128 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_128_128_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/128,lon/128 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_128_128_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/128,lon/128 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_128_128_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/256,lon/256 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_256_256_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/256,lon/256 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_256_256_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/256,lon/256 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_256_256_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/256,lon/256 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_256_256_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/512,lon/512 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_512_512_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/512,lon/512 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_512_512_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/512,lon/512 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_512_512_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/512,lon/512 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_512_512_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/1024,lon/1024 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1024_1024_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/1024,lon/1024 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1024_1024_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/1024,lon/1024 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1024_1024_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/1024,lon/1024 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1024_1024_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/2048,lon/2048 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2048_2048_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/2048,lon/2048 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2048_2048_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/2048,lon/2048 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2048_2048_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/2048,lon/2048 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2048_2048_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/325,lon/325 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_325_325_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/325,lon/325 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_325_325_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/325,lon/325 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_325_325_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/325,lon/325 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_325_325_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/650,lon/650 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_650_650_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/650,lon/650 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_650_650_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/650,lon/650 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_650_650_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/650,lon/650 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_650_650_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/1300,lon/1300 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1300_1300_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/1300,lon/1300 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1300_1300_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/1300,lon/1300 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1300_1300_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/1300,lon/1300 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_1300_1300_zlib_9.nc
nccopy -v SIS,time -c time/1,lat/2600,lon/2600 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2600_2600_zlib_0.nc
nccopy -v SIS,time -c time/1,lat/2600,lon/2600 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2600_2600_zlib_3.nc
nccopy -v SIS,time -c time/1,lat/2600,lon/2600 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2600_2600_zlib_6.nc
nccopy -v SIS,time -c time/1,lat/2600,lon/2600 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_1_2600_2600_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/64,lon/64 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_64_64_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/64,lon/64 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_64_64_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/64,lon/64 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_64_64_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/64,lon/64 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_64_64_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/128,lon/128 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_128_128_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/128,lon/128 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_128_128_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/128,lon/128 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_128_128_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/128,lon/128 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_128_128_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/256,lon/256 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_256_256_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/256,lon/256 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_256_256_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/256,lon/256 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_256_256_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/256,lon/256 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_256_256_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/512,lon/512 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_512_512_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/512,lon/512 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_512_512_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/512,lon/512 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_512_512_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/512,lon/512 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_512_512_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/1024,lon/1024 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1024_1024_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/1024,lon/1024 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1024_1024_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/1024,lon/1024 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1024_1024_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/1024,lon/1024 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1024_1024_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/2048,lon/2048 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2048_2048_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/2048,lon/2048 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2048_2048_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/2048,lon/2048 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2048_2048_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/2048,lon/2048 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2048_2048_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/325,lon/325 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_325_325_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/325,lon/325 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_325_325_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/325,lon/325 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_325_325_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/325,lon/325 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_325_325_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/650,lon/650 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_650_650_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/650,lon/650 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_650_650_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/650,lon/650 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_650_650_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/650,lon/650 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_650_650_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/1300,lon/1300 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1300_1300_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/1300,lon/1300 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1300_1300_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/1300,lon/1300 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1300_1300_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/1300,lon/1300 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_1300_1300_zlib_9.nc
nccopy -v SIS,time -c time/12,lat/2600,lon/2600 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2600_2600_zlib_0.nc
nccopy -v SIS,time -c time/12,lat/2600,lon/2600 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2600_2600_zlib_3.nc
nccopy -v SIS,time -c time/12,lat/2600,lon/2600 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2600_2600_zlib_6.nc
nccopy -v SIS,time -c time/12,lat/2600,lon/2600 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_12_2600_2600_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/64,lon/64 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_64_64_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/64,lon/64 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_64_64_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/64,lon/64 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_64_64_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/64,lon/64 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_64_64_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/128,lon/128 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_128_128_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/128,lon/128 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_128_128_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/128,lon/128 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_128_128_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/128,lon/128 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_128_128_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/256,lon/256 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_256_256_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/256,lon/256 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_256_256_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/256,lon/256 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_256_256_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/256,lon/256 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_256_256_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/512,lon/512 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_512_512_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/512,lon/512 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_512_512_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/512,lon/512 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_512_512_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/512,lon/512 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_512_512_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/1024,lon/1024 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1024_1024_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/1024,lon/1024 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1024_1024_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/1024,lon/1024 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1024_1024_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/1024,lon/1024 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1024_1024_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/2048,lon/2048 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2048_2048_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/2048,lon/2048 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2048_2048_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/2048,lon/2048 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2048_2048_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/2048,lon/2048 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2048_2048_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/325,lon/325 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_325_325_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/325,lon/325 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_325_325_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/325,lon/325 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_325_325_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/325,lon/325 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_325_325_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/650,lon/650 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_650_650_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/650,lon/650 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_650_650_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/650,lon/650 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_650_650_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/650,lon/650 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_650_650_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/1300,lon/1300 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1300_1300_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/1300,lon/1300 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1300_1300_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/1300,lon/1300 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1300_1300_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/1300,lon/1300 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_1300_1300_zlib_9.nc
nccopy -v SIS,time -c time/24,lat/2600,lon/2600 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2600_2600_zlib_0.nc
nccopy -v SIS,time -c time/24,lat/2600,lon/2600 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2600_2600_zlib_3.nc
nccopy -v SIS,time -c time/24,lat/2600,lon/2600 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2600_2600_zlib_6.nc
nccopy -v SIS,time -c time/24,lat/2600,lon/2600 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_24_2600_2600_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/64,lon/64 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_64_64_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/64,lon/64 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_64_64_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/64,lon/64 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_64_64_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/64,lon/64 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_64_64_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/128,lon/128 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_128_128_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/128,lon/128 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_128_128_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/128,lon/128 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_128_128_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/128,lon/128 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_128_128_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/256,lon/256 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_256_256_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/256,lon/256 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_256_256_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/256,lon/256 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_256_256_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/256,lon/256 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_256_256_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/512,lon/512 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_512_512_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/512,lon/512 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_512_512_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/512,lon/512 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_512_512_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/512,lon/512 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_512_512_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/1024,lon/1024 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1024_1024_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/1024,lon/1024 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1024_1024_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/1024,lon/1024 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1024_1024_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/1024,lon/1024 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1024_1024_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/2048,lon/2048 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2048_2048_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/2048,lon/2048 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2048_2048_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/2048,lon/2048 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2048_2048_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/2048,lon/2048 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2048_2048_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/325,lon/325 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_325_325_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/325,lon/325 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_325_325_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/325,lon/325 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_325_325_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/325,lon/325 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_325_325_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/650,lon/650 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_650_650_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/650,lon/650 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_650_650_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/650,lon/650 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_650_650_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/650,lon/650 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_650_650_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/1300,lon/1300 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1300_1300_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/1300,lon/1300 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1300_1300_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/1300,lon/1300 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1300_1300_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/1300,lon/1300 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_1300_1300_zlib_9.nc
nccopy -v SIS,time -c time/48,lat/2600,lon/2600 -d 0 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2600_2600_zlib_0.nc
nccopy -v SIS,time -c time/48,lat/2600,lon/2600 -d 3 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2600_2600_zlib_3.nc
nccopy -v SIS,time -c time/48,lat/2600,lon/2600 -d 6 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2600_2600_zlib_6.nc
nccopy -v SIS,time -c time/48,lat/2600,lon/2600 -d 9 -h 16777216 -e 4133 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc /project/home/p200206/data/sis/rechunking/SISin200001010000004231000101MA_1_2600_2600_48_2600_2600_zlib_9.nc
```

</details>

The input file is

``` bash
❯ ls -lahrt /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc
-rw-r-----. 1 u101014 p200206 158M Nov 13 13:39 /project/home/p200206/data/sis/chunks_1_2600_2600/SISin200001010000004231000101MA_1_2600_2600.nc
```

while the collection of rechunked data from this single file requires 

``` bash
❯ du -sch /project/home/p200206/data/sis/rechunking/
47G	/project/home/p200206/data/sis/rechunking/
47G	total
```

> ---
> This is **quite some space**,
> so we better **be careful** further on
> **when engaging with massive processing**.
>
> ---

### Incremental Testing  [ToDo]

**Step-by-Step Approach**

Each test should change only one parameter at a time from the baseline or the previous test configuration.

**Automated Testing**

Use a Python script to automate the testing process as much as possible. This ensures consistency and reproducibility.

### Evaluation and Analysis

**Data Analysis**

- Collecting and analysing the data
- Focus on read times for different scenarios ?

**Identify Trade-offs**

Looking for trade-offs between chunking, compression, and caching.

### Use Xarray and Python

**Xarray for reading**

`xarray` provides a convenient interface and can handle chunking efficiently.

**Profiling Tools**

Use Python profiling tools to analyze the performance of different read operations.

### Considerations for Script Development

- **Modularity** : modular scripting allows for systematic parameterisation.

- **Logging** : comprehensive logging to record test conditions and results.

- **Visualization** of the performance data to better understand and communicate the results.

### Final Thoughts

- **Iterative Approach** : Initial results may lead to new hypotheses and test conditions.

- Detailed **documentation** of each test scenario and its results.

# References
