# Kerchunking large time series

<!-- vim-markdown-toc GFM -->

* [Long-Term Observations](#long-term-observations)
    * [Data models](#data-models)
    * [Chunking ?](#chunking-)
* [`Kerchunk`](#kerchunk)
    * [+ advantages](#-advantages)
    * [- drawbacks](#--drawbacks)
    * [How does it work?](#how-does-it-work)
    * [Experimental](#experimental)
    * [First time questions](#first-time-questions)
* [NetCDF utilities](#netcdf-utilities)
    * [Rechunking ?](#rechunking-)
* [Xarray](#xarray)
    * [Chunking](#chunking)
* [Concepts](#concepts)
    * [Parallel](#parallel)
    * [Concurrent](#concurrent)
    * [Chunks](#chunks)
    * [Descriptive metadata](#descriptive-metadata)
    * [Consolidation](#consolidation)
    * [Asynchronous](#asynchronous)
    * [Serverless](#serverless)
    * [Front- and Back-end](#front--and-back-end)

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
with specific reference to netCDF4/HDF5 files.

**How?** Kerchunk

- extracts metadata in a single scan
- arranges multiple chunks from multiple files
- with [dask][dask] and [zarr][zarr],
  reads chunks in [parallel][^parallel] and/or
  [concurrently][^concurrently] within a single indexible aggregate dataset

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

- Creating SARAH3 daily netCDF reference files can take 4+ hours
- optimizing chunking can reduce this


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
