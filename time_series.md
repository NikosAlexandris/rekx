# Kerchunking large time series

<!-- vim-markdown-toc Marked -->

* [Long-Term Observations](#long-term-observations)
    * [Data models](#data-models)
    * [Chunking ?](#chunking-?)
* [`Kerchunk`](#`kerchunk`)
    * [+ advantages](#+-advantages)
    * [- drawbacks](#--drawbacks)
    * [How does it work?](#how-does-it-work?)
    * [Experimental](#experimental)
    * [First time questions](#first-time-questions)
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

- HDF5: Effective yet **not** cloud-optimized.

  > HDF5 supports direct reading from cloud storage, whether over HTTP or by passing [fsspec][fsspec] instances.

[fsspec]: https://filesystem-spec.readthedocs.io


## Chunking ?

Splits data for easier reading

**Original**

| Hex                          | Text                        |
|------------------------------|-----------------------------|
| `01 02 03 04 05 06 07 08 09` | `1, 2, 3, 4, 5, 6, 7, 8, 9` |

<!-- . -->
**Chunked**

| Hex                                                                           |                 Text                |
|-------------------------------------------------------------------------------|:-----------------------------------:|
| **`AA 03 01`** `01 02 03` **`AA 03 01`** `04 05 06` **`AA 03 01`** `07 08 09` | `[1, 2, 3]` `[4, 5, 6]` `[7, 8, 9]` |

> **`AA 03 01`** marks the start of a chunk

See also :

- [Chunking in HDF5][Chunking in HDF5]
- [Caching in HDF5][Caching in HDF5]


[Chunking in HDF5]: https://portal.hdfgroup.org/display/HDF5/Chunking+in+HDF5
[Caching in HDF5]: https://support.hdfgroup.org/HDF5/doc/RM/RM_H5P.html#Property-SetChunkCache


# `Kerchunk`

[kerchunk][kerchunk] supports cloud-friendly access of data
with specific reference to netCDF4/HDF5 files.

- extract metadata in a single scan
- arrange multiple chunks from multiple files
- with [dask][dask] and [zarr][zarr],
  read chunks in [parallel][parallel] and/or
  [concurrently][concurrently] within a single indexible aggregate dataset

[kerchunk]: https://fsspec.github.io/kerchunk/
[dask]: https://www.dask.org/
[zarr]: https://zarr.readthedocs.io/en/stable/
[parallel]: see [Parallel](##Parallel)
[concurrently]: see [Concurrency](##Concurrency)

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


# Xarray

## Chunking 

See useful hints at [Chunking and performance][Chunking and performance],
[Optimisation tips][Optimisation tips], [Dask array best practices][Dask array
best practices].

[Chunking and performance]: https://docs.xarray.dev/en/stable/user-guide/dask.html#chunking-and-performance
[Optimisation tips]: https://docs.xarray.dev/en/stable/user-guide/dask.html#optimization-tips
[Dask array best practices]: https://docs.dask.org/en/latest/array-best-practices.html


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
