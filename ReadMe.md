# rekx

**[ Under Development ]**

`rekx` interfaces the [Kerchunk](https://fsspec.github.io/kerchunk/) library
in an interactive way through the command line.
It assists in creating virtual aggregate datasets,
also known as Kerchunk reference sets,
enabling efficient, parallel and cloud-friendly in-situ data access
without duplicating original datasets.

More than a functional tool,
`rekx` serves an educational purpose on matters around
chunking, compression and reading data from file formats such as NetCDF
that are widely adopted by the scientific community
for storing and processing large time series.
It features command line tools
to diagnose data structures,
validate chunking uniformity across multiple files,
suggest good chunking shapes and parameterise the rechunking of datasets,
create and aggregate Kerchunk reference sets
and time data read operations.

## To Do

- [ ] Write clean and meaningful docstrings for each and every function
- [ ] Pytest each and every (?) function
- [ ] Packaging
- [ ] Documentation
  - [ ] Use https://squidfunk.github.io/mkdocs-material/
  - [ ] Examples
    - [ ] Diagnose
    - [ ] Suggest
    - [ ] Rechunk
    - [ ] Create references
    - [ ] Combine References
    - [ ] Select (aka read)
      - [ ] From Xarray-supported datasets
      - [ ] From Kerchunk references
  - [ ] Tutorial
- [ ] ...


## Examples

Inspect a signle NetCDF file :

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

Perhaps restrict inspection on data variables only :

``` bash
❯ rekx inspect SISin202001010000004231000101MA.nc -v --variable-set data
                                                              SISin202001010000004231000101MA.nc

  Variable   Shape              Chunks         Cache      Elements   Preemption   Type    Scale   Offset   Compression   Level   Shuffling   Read Time
 ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SIS        48 x 2600 x 2600   1 x 1 x 2600   16777216   4133       0.75         int16   -       -        zlib          4       False       0.007

                                    File size: 181550165 bytes, Dimensions: time: 48, lon: 2600, bnds: 2, lat: 2600
                                        * Cache: Size in bytes, Number of elements, Preemption ranging in [0, 1]
```

Report chunking shapes across multiple files in the same source directory :

``` bash
❯ rekx shapes . --pattern "SIS*.nc" --variable-set data 

  Variable   Shapes            Files                                            Count
 ─────────────────────────────────────────────────────────────────────────────────────
  SIS        1 x 1 x 2600      SISin202001040000004231000101MA.nc ..            4
  SIS        1 x 2600 x 2600   SISin200001010000004231000101MA_1_2600_2600.nc   1
```

### Combining parameters for rechunking

Identifying the appropriate configuration for data stored in NetCDF files,
involves systematic experimentation with various structural parameters.
The `rechunk-generator` command
varies structural data parameters and options for NetCDF files
that influence the file size and data access speed
and generates a series of `nccopy` commands for rechunking NetCDF files.
The list of commands can be fed to the mighty GNU Parallel tool
which will take care to run them in parallel.
Subsequently, `rekx inspect-multiple` will report on the new data structeres
and measure the average time it takes to read data over a geographic location.

Given the initial NetCDF file `SISin202001010000004231000101MA.nc`,
we can generate a series of experimental `nccopy` commands :

```bash
❯ rekx rechunk-generator SISin202001010000004231000101MA.nc rechunking_test --time 48 --latitude 64,128,256 --longitude 64,128,256 --compression-level 0,3,6,9 -v --shuffling --memory
Writing generated commands into rechunk_commands_for_SISin202001010000004231000101MA.txt
nccopy -c time/48,lat/64,lon/64 -d 0  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_0.nc
nccopy -c time/48,lat/64,lon/64 -d 3 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_3_shuffled.nc
nccopy -c time/48,lat/64,lon/64 -d 3  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_3.nc
nccopy -c time/48,lat/64,lon/64 -d 6 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_6_shuffled.nc
nccopy -c time/48,lat/64,lon/64 -d 6  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_6.nc
nccopy -c time/48,lat/64,lon/64 -d 9 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_9_shuffled.nc
nccopy -c time/48,lat/64,lon/64 -d 9  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_64_64_zlib_9.nc
nccopy -c time/48,lat/128,lon/128 -d 0  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_0.nc
nccopy -c time/48,lat/128,lon/128 -d 3 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_3_shuffled.nc
nccopy -c time/48,lat/128,lon/128 -d 3  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_3.nc
nccopy -c time/48,lat/128,lon/128 -d 6 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_6_shuffled.nc
nccopy -c time/48,lat/128,lon/128 -d 6  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_6.nc
nccopy -c time/48,lat/128,lon/128 -d 9 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_9_shuffled.nc
nccopy -c time/48,lat/128,lon/128 -d 9  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_128_128_zlib_9.nc
nccopy -c time/48,lat/256,lon/256 -d 0  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_0.nc
nccopy -c time/48,lat/256,lon/256 -d 3 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_3_shuffled.nc
nccopy -c time/48,lat/256,lon/256 -d 3  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_3.nc
nccopy -c time/48,lat/256,lon/256 -d 6 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_6_shuffled.nc
nccopy -c time/48,lat/256,lon/256 -d 6  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_6.nc
nccopy -c time/48,lat/256,lon/256 -d 9 -s -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_9_shuffled.nc
nccopy -c time/48,lat/256,lon/256 -d 9  -h 16777216 -e 4133 -w SISin202001010000004231000101MA.nc rechunking_test/SISin202001010000004231000101MA_48_256_256_zlib_9.nc
```

We let GNU Parallel to execute these in parallel :

``` bash
parallel < rechunk_commands_for_SISin202001010000004231000101MA.txt
```

While the output comprises as many new NetCDF files as the `nccopy` commands,
for the sake of showcasing `rekx`,
let us only inspect new NetCDF files whose filename contains the string `256` :

``` bash
❯ rekx inspect-multiple data/rechunking_test --repetitions 3 --humanize --long-table --variable-set data --pattern "*256*"

  Name                   Size        Dimensions            Variable   Shape              Chunks           Cache      Elements   Preemption   Type    Scale   Offset   Compression     Level   Shuffling   Read Time
 ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  SISin20200101000000…   726.1 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -                        0       False       0.024
                                     2600
  SISin20200101000000…   137.6 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib            6       False       0.025
                                     2600
  SISin20200101000000…   137.4 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib            9       False       0.030
                                     2600
  SISin20200101000000…   123.7 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib, shuffle   3       True        0.032
                                     2600
  SISin20200101000000…   140.1 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib            3       False       0.032
                                     2600
  SISin20200101000000…   120.9 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib, shuffle   6       True        0.034
                                     2600
  SISin20200101000000…   119.8 MiB   2 x 48 x 2600 x       SIS        48 x 2600 x 2600   48 x 256 x 256   16777216   4133       0.75         int16   -       -        zlib, shuffle   9       True        0.034
                                     2600

                                               ^ Dimensions: lat x time x lon x bnds * Cache: Size in bytes, Number of elements, Preemption strategy ranging in [0, 1]
```

The output reports on dataset structure, chunking, compression levels,
and the average time to read data over a geographic location.
Analysing such results, can guide us in choosing an effective chunking shape
and compression strategy in order to optimize our data structure.


## Other relevant projects

- https://github.com/coecms/nccompress


# Kerchunking large time series

<!-- vim-markdown-toc GFM -->

* [Long-Term Observations](#long-term-observations)
    * [Data models](#data-models)
    * [Chunking ?](#chunking-)
        * [Size and number](#size-and-number)
* [`Kerchunk`](#kerchunk)
    * [+ advantages](#-advantages)
    * [- drawbacks](#--drawbacks)
    * [How does it work?](#how-does-it-work)
    * [Experimental](#experimental)
        * [Experiment 1](#experiment-1)
    * [First time questions](#first-time-questions)
* [NetCDF utilities](#netcdf-utilities)
    * [Rechunking ?](#rechunking-)
        * [Example](#example)
* [Xarray](#xarray)
    * [Chunking](#chunking)
* [Unsorted](#unsorted)
* [Concepts](#concepts)
    * [Parallel](#parallel)
    * [Concurrent](#concurrent)
    * [Chunks](#chunks)
    * [Descriptive metadata](#descriptive-metadata)
    * [Consolidation](#consolidation)
    * [Asynchronous](#asynchronous)
    * [Serverless](#serverless)
    * [Front- and Back-end](#front--and-back-end)
* [References](#references)

<!-- vim-markdown-toc -->

# Long-Term Observations

- Size
  - example : _half-hourly_ [SARAH3][SARAH3] daily netCDF files are $~150$ - $180$ MB each
  - or $10$ years $\approx0.5$ TB

[SARAH3]: https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003

<!-- . -->
- Format
  - Past: [CSV][CSV], [JSON][JSON], [XML][XML]
  - Present: [HDF5][HDF5], [NetCDF][NetCDF]

[CSV]: https://en.wikipedia.org/wiki/Comma-separated_values
[JSON]: https://www.json.org/json-en.html
[XML]: https://www.w3.org/XML/
[HDF5]: https://www.hdfgroup.org/solutions/hdf5
[NetCDF]: https://www.unidata.ucar.edu/software/netcdf/

<!-- . -->
- Challenges
  - volume
  - metadata extraction
  - [concurrent][concurrent] & [parallel][parallel] access


## Data models

- Binary Buffers

  ```python
  full_array = read_entire_file("10_year_data.hdf5")
  one_day_data = full_array[0:24]
  ```

- HDF5

  - yet not cloud optimised
  - [H5coro][H5coro] : cloud-optimised read-only library

> HDF5 supports direct reading from cloud storage, whether over HTTP or by
> passing [fsspec][fsspec] instances.

[H5coro]: https://github.com/ICESat2-SlideRule/h5coro
[fsspec]: https://filesystem-spec.readthedocs.io


## Chunking ?

Splits data for easier reading

**Original**

| Hex                          | Text                        |
|------------------------------|-----------------------------|
| `01 02 03 04 05 06 07 08 09` | `1, 2, 3, 4, 5, 6, 7, 8, 9` |

<!-- . -->
**Chunked**

| Hex                                                                                                               |                     Text                     | Size | Number |
|-------------------------------------------------------------------------------------------------------------------|:--------------------------------------------:|------|--------|
| **`AA 05 01`** `01 02 03 04 05` **`AA 05 01`** `06 07 08 09 -`                               | `[1, 2, 3, 4, 5]` `[6, 7, 8, 9, -]` | 5    | 2      |
| **`AA 04 01`** `01 02 03 04` **`AA 04 01`** `05 06 07 08` **`AA 04 01`** `09 - - -`                               | `[1, 2, 3, 4]` `[5, 6, 7, 8]` `[9, -, -, -]` | 4    | 3      |
| **`AA 03 01`** `01 02 03` **`AA 03 01`** `04 05 06` **`AA 03 01`** `07 08 09`                                     |      `[1, 2, 3]` `[4, 5, 6]` `[7, 8, 9]`     | 3    | 3      |
| **`AA 02 01`** `01 02` **`AA 02 01`** `03 04` **`AA 02 01`** `05 06` **`AA 02 01`** `07 08` **`AA 02 01`** `09 -` | `[1, 2]` `[3, 4]` `[5, 6]` `[7, 8]` `[9, -]` | 2    | 5      |

> **`AA 0? 01`** sequences mark the _start_ of a chunk


### Size and number

The `chunks` keyword specifies the _size_ of chunks, not the number of chunks!
Increasing the number of chunks in the _time_ dimension will consume more memory!

Examples:

- chunks={'time':1, 'y':768, 'x':922} --> size of each chunk is 1*768*922 ~ 7e5
- chunks={'time':168, 'y':384, 'x':288}  --> size of each chunk is 168*384*288 ~ 2e7.


See also :

- [Chunking in HDF5][Chunking in HDF5]
- [Caching in HDF5][Caching in HDF5]


[Chunking in HDF5]: https://portal.hdfgroup.org/display/HDF5/Chunking+in+HDF5
[Caching in HDF5]: https://support.hdfgroup.org/HDF5/doc/RM/RM_H5P.html#Property-SetChunkCache

# `Kerchunk`

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


## Experimental

- Creating SARAH3 daily netCDF reference files can take $4+$ hours
- optimizing chunking can reduce this

### Experiment 1

Following an incomplete experiment, eventually worth revisiting.

**Input**

- Daily NetCDF files from 1999 to 2021 (actually, I miss a year, so up to 2022) that make up about about 1.2T
  - Each daily NetCDF file contains 48 half-hourly maps of 2600 x 2600 pixels
  - Noted here : mixed chunking shapes between years (e.g. time, lat, lon : 1 x 2600 x 2600, 1 x 1300 x 1300, and maybe more)

- The daily NetCDF files are rechunked 1 x 32 x 32, these are now 1.25T

- A first set of JSON reference files (one reference file per rechunked input NetCDF file) is about ~377G.

- A second step of (24 should be in total) yearly JSON reference files (based on the first reference set) is ~300G

- Finally, the goal is to create a single reference file to cover the complete time series

**Hardware**

``` bash
❯ free -hm
              total        used        free      shared  buff/cache   available
Mem:          503Gi       4.7Gi       495Gi       2.8Gi       3.1Gi       494Gi
Swap:            0B          0B          0B
```

**Trials**

``` bash
13G Nov  2 10:07 sarah3_sid_reference_1999.json
13G Nov  2 09:58 sarah3_sid_reference_2000.json
13G Nov  2 11:00 sarah3_sid_reference_2001.json
13G Nov  2 11:08 sarah3_sid_reference_2002.json
13G Nov  2 12:04 sarah3_sid_reference_2003.json
13G Nov  2 12:12 sarah3_sid_reference_2004.json
13G Nov  2 13:07 sarah3_sid_reference_2005.json
13G Nov  2 14:29 sarah3_sid_reference_2006.json
13G Nov  2 15:27 sarah3_sid_reference_2007.json
13G Nov  2 16:45 sarah3_sid_reference_2008.json
13G Nov  2 17:43 sarah3_sid_reference_2009.json
13G Nov  2 19:02 sarah3_sid_reference_2010.json
13G Nov  2 19:58 sarah3_sid_reference_2011.json
13G Nov  2 21:25 sarah3_sid_reference_2012.json
13G Nov  2 22:13 sarah3_sid_reference_2013.json
13G Nov  2 23:43 sarah3_sid_reference_2014.json
13G Nov  3 00:36 sarah3_sid_reference_2015.json
13G Nov  3 02:03 sarah3_sid_reference_2016.json
13G Nov  3 02:58 sarah3_sid_reference_2017.json
13G Nov  3 04:24 sarah3_sid_reference_2018.json
13G Nov  3 05:21 sarah3_sid_reference_2019.json
13G Nov  3 06:48 sarah3_sid_reference_2020.json
13G Nov  3 07:41 sarah3_sid_reference_2021.json
```

Trying to combine the above to a single reference set, fails with the following
error message :

``` python
JSONDecodeError: Could not reserve memory block
```

**Take away message**

The limiting factor for the size of the reference sets
is not the total number of bytes
but the total number of references,
so the chunking scheme is perhaps more important here.

## First time questions

- Data format?
- Chunking strategy?
- Reference file customization?


# NetCDF utilities

## Rechunking ?

Reorganizing the data into chunks that include all _timestamps_ in each chunk
for a few lat and lon coordinates
would greatly speed up such access.
To chunk the data in the input file `slow.nc`,
a netCDF file of any type, to the output file `fast.nc`,
we can use `nccopy` :

``` bash
nccopy -c time/1000,lat/40,lon/40 slow.nc fast.nc
```

to specify data chunks of 1000 times, 40 latitudes, and 40 longitudes.

> More : [nccopy examples](https://docs.unidata.ucar.edu/nug/current/netcdf_utilities_guide.html#nccopy_EXAMPLES)

Given enough memory to contain the output file,
the rechunking operation can be significantly speed up
by creating the output in memory before writing it to disk on close:

``` bash
nccopy -w -c time/1000,lat/40,lon/40 slow.nc fast.nc
```

### Example

Timing the rechunking of SID files from the SARAH3 collection using
`nccopy` laptop-with-ssd [^laptop-with-ssd]

[^laptop-with-ssd]: Laptop with SSD disk

<!-- ``` bash -->
<!-- ❯ mlr --csv --oxtab --opprint put '$Duration = (${Duration 1} + ${Duration 2} + ${Duration 3}) /3' then cut -f Time,Latitude,Longitude,Duration then sort -n Duration rechunking_timings_old.noncsv -->
<!-- ``` -->

| Time | Latitude | Longitude | Duration           |
|------|----------|-----------|--------------------|
| 1    | 2600     | 2600      | 8.659999999999998  |
| 1    | 325      | 325       | 10.55              |
| 1    | 128      | 128       | 10.606666666666667 |
| 1    | 256      | 256       | 10.966666666666667 |
| 48   | 128      | 128       | 11.063333333333333 |
| 1    | 650      | 650       | 11.063333333333334 |
| 1    | 1300     | 1300      | 11.203333333333333 |
| 48   | 256      | 256       | 11.223333333333334 |
| 48   | 325      | 325       | 11.24              |
| 48   | 64       | 64        | 11.339999999999998 |
| 1    | 512      | 512       | 11.756666666666666 |
| 1    | 1024     | 1024      | 12.24              |
| 1    | 64       | 64        | 12.856666666666667 |
| 1    | 2048     | 2048      | 15.049999999999999 |
| 1    | 32       | 32        | 15.63              |
| 48   | 32       | 32        | 304.3833333333334  |
| 48   | 650      | 650       | 343.68333333333334 |
| 48   | 1300     | 1300      | 354.58             |
| 48   | 2600     | 2600      | 367.32             |
| 48   | 512      | 512       | 417.2133333333333  |
| 48   | 1024     | 1024      | 431.3666666666666  |
| 48   | 2048     | 2048      | 641.8233333333334  |


# Xarray

## Chunking 

See useful hints at :

- [Chunking and performance][Chunking and performance]
- [Optimisation tips][Optimisation tips]
- [Dask array best practices][Dask array best practices].

[Chunking and performance]: https://docs.xarray.dev/en/stable/user-guide/dask.html#chunking-and-performance
[Optimisation tips]: https://docs.xarray.dev/en/stable/user-guide/dask.html#optimization-tips
[Dask array best practices]: https://docs.dask.org/en/latest/array-best-practices.html


# Unsorted

Source [Chunking Data: Choosing Shapes][Chunking Data: Choosing Shapes]

[Chunking Data: Choosing Shapes]: https://www.unidata.ucar.edu/blogs/developer/en/entry/chunking_data_choosing_shapes

**Intricacies of data chunking**

- Optimize read times for various ways to access data
    - either by rows, by columns, or as a rectangular subgrid
- The idea is to _minimize the number of disk accesses_.
  
  **How?** By aligning chunk borders with the most common access patterns.

**Important is**

- The total number of chunks

** Consolidation**

Metadata _consolidation_ in a Zarr context,
is a performance optimization technique
that reduces the number of read operations required to access metadata.
It can be particularly beneficial when working with remote or distributed storage systems.

_consolidation_ is
the _combination of all separate metadata files_
associated with the different arrays and groups within a Zarr hierarchy
_into a single metadata file_.

**Optimal Chunk Shapes**

   - For 2D data, rectangular chunks help balance the disk access times for
     both row-wise and column-wise access.

   - For 3D data or higher, the chunking strategy may need to be adjusted based
     on the most common access patterns.

**Rechunking Performance**

   - Rechunking : changing the chunk shape of existing datasets,
     which can be time-consuming especially for large datasets.

   - Tools like `nccopy` for netCDF-4 and `h5repack` for both HDF5 and netCDF-4
     are available for rechunking. The time it takes is usually a small
     multiple of the time to copy the data from one file to another.

**SSD vs Spinning Disk**

   - Solid State Drives (SSD) can significantly speed up the rechunking process
     and data access times as compared to traditional spinning disks.

**Chunking and Compression**

- a chunk is the _atomic unit_ of compression as well as disk access
- compressed data has to be/is forcedly chunked
- rechunking compressed data involves several steps:

  `read` $\rightarrow$ `uncompress` $\rightarrow$ `rechunk` $\rightarrow$ `recompress` $\rightarrow$  `write` new chunks

- rechunking compressed data _can sometimes be faster_ due to savings in disk
  I/O!

**Optimal layout?**

> An algorithm discussed in 
> ["Chunking Data: Choosing Shapes", by Russ
> Rew](https://www.unidata.ucar.edu/blogs/developer/en/entry/chunking_data_choosing_shapes) : 
> [chunk_shape_3D.py](https://www.unidata.ucar.edu/blog_content/data/2013/chunk_shape_3D.py)
> 
> See also : own implementation
> [`suggest.py`](https://gist.github.com/NikosAlexandris/1fbc82fd0578ce96a4d39cbffa4ed584)

An algebraic formulation for optimal chunking bases on
_equalizing the number of chunks accessed for a 1D time series and a 2D
horizontal slice in a 3D dataset_.
Let $D$ be the number of values you want in a chunk,
$N$ be the total number of chunks used to partition the array,
and $c$ be a scaling factor derived from $D$ and the dimensions of the array.
The chunk shape would then be given by the formula:

$$c = \left( \frac{D}{{25256 \times 37 \times 256 \times 512}} \right)^{1/4}$$

The resulting chunk shape is obtained by multiplying each dimension size by $c$
and truncating to an integer. The chunk shape will thus be:

$$\text{chunk\_shape} = \left( \left\lfloor 25256 \times c \right\rfloor,
\left\lfloor 37 \times c \right\rfloor, \left\lfloor 256 \times c
\right\rfloor, \left\lfloor 512 \times c \right\rfloor \right)$$

This formula **assumes** that the optimal chunk shape will distribute the chunks
equally along each dimension, and the scaling factor $c$ is calculated to
ensure the total number of values in a chunk is close to $D$, without
exceeding it.


# Concepts

## Parallel

_Parallel_
are operations running _simultaneously_ yet _independently_
in multiple threads, processes or machines.
For CPU-intensive workloads,
past the overhead of arranging such a system,
a speedup equal to the number of CPU cores is possible.

| Parallel access with | Scenario                                                                         |
|----------------------|----------------------------------------------------------------------------------|
| Lock                 | Resource A (locked) -> Process 1                                                 |
| No Lock              | Resource A $\longrightarrow$ Process 1<br>Resource A $\longrightarrow$ Process 2 |


## Concurrent

_Concurrent_
are multiple operations managed during overlapping periods
yet not necessarily executed at the exact same instant.
For the particular case of cloud storage,
the latency to get the first byte of a read can be comparable
or dominate the total time for a request.
Practically, launching many requests,
and only pay the overhead cost once (they all wait together),
enables a large speedup.


|      Execution | Task                                                                                                                                                                                                                                                             |
|---------------:|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Non-Concurrent | A $\rightarrow$ Run $\rightarrow$ Complete $\longrightarrow$ B $\rightarrow$ Run $\rightarrow$ Complete                                                                                                                                                          |
|     Concurrent | A $\rightarrow$ .. $\rightarrow$ Complete<br> .. B $\longrightarrow$ .. $\rightarrow$ Complete<br>C $\longrightarrow$ .. $\longrightarrow$ Complete<br> .. .. D $\longrightarrow$ .. $\rightarrow$ Complete<br> .. E $\rightarrow$ .. $\longrightarrow$ Complete |


## Chunks

Reading a chunk?

| Byte range |               Index              |
|-----------:|:--------------------------------:|
|   Original | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |
|  Selection |          `[3, 4, 5, 6]`          |


## Descriptive metadata

|  Compression | Size                             |  % |
|-------------:|:---------------------------------|---:|
| Decompressed | `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]` |  0 |
|   Compressed | `[0, 1, 2, 3, 4, 5, 6]`          | 30 |


## Consolidation

A single indexible aggregate dataset

| Consolidation |        Data       | Parts |
|--------------:|:-----------------:|:-----:|
|     Scattered | `[-]` `[-]` `[-]` |   3   |
|  Consolidated |  `[-----------]`  |   1   |


|             Aggregation | Simple | Simple | Virtual |
|------------------------:|:------:|:------:|:-------:|
|                    File |    A   |    B   |    V    |
| Points to $\rightarrow$ |    A   |    B   |   A, B  |


## Asynchronous

_Asynchronous_
is a mechanism performing tasks without waiting for other tasks to complete.

|    Operation | Execution                                                                                                                                                      |
|-------------:|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
|   Sequential | A $\longrightarrow$ Complete $\rightarrow$ B $\longrightarrow$ Complete $\rightarrow$ C $\longrightarrow$ Complete                                             |
| Asynchronous | A $\longrightarrow$ .. $\longrightarrow$ Complete<br>B $\longrightarrow$ .. .. $\longrightarrow$ Complete<br>C $\longrightarrow$ .. $\longrightarrow$ Complete |


## Serverless

_Serverless_
is a deployment of code in a cloud service which in turn handles
server maintenance, scaling, updates and more. 

| Deployment  | Management                                       |
|-------------|--------------------------------------------------|
| Traditional | Manual server, maintenance, scaling, updates, .. |
| Serverless  | Automated cloud service, deployment, scaling, .. |


## Front- and Back-end

| Component | Role                                                        |
|-----------|-------------------------------------------------------------|
| Backend   | Data storage, algorithms, API, processing, serving          |
| Frontend  | User interface & experience using a browsers or application |


# References

Durant, Martin; Jones, Max; Abernathey, Ryan; Hoese, David; Bednar, James
(2023). Pangeo-ML Augmentation - Enabling Cloud-native access to archival data
with Kerchunk. figshare. Preprint.
[https://doi.org/10.6084/m9.figshare.22266433.v1](https://doi.org/10.6084/m9.figshare.22266433.v1)

"NetCDF-4 Chunking Guide" by Unidata. Available at:
https://www.unidata.ucar.edu/software/netcdf/workshops/most-recent/nc4chunking/index.html
