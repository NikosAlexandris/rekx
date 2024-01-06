---
tags:
  - Context
  - Chunking
---

# Context for Chunking

!!! warning

    To sort out!

## First time questions

- Data format?
- Chunking strategy?
- Reference file customization?

## Challenges with long-term observations

- Size, Volume
    - example : _half-hourly_ [SARAH3][SARAH3] daily netCDF files are $~150$ - $180$ MB each
    - or $10$ years $\approx0.5$ TB


- Format
    - Past: [CSV][CSV], [JSON][JSON], [XML][XML]
    - Present: [HDF5][HDF5], [NetCDF][NetCDF]

- Metadata extraction

- Data access
    - [concurrent][concurrent] & [parallel][parallel] access

[SARAH3]: https://wui.cmsaf.eu/safira/action/viewDoiDetails?acronym=SARAH_V003
[CSV]: https://en.wikipedia.org/wiki/Comma-separated_values
[JSON]: https://www.json.org/json-en.html
[XML]: https://www.w3.org/XML/
[HDF5]: https://www.hdfgroup.org/solutions/hdf5
[NetCDF]: https://www.unidata.ucar.edu/software/netcdf/


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


## What is Chunking ?

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

### Size and number of chunks

Chunks affect both memory usage and processing efficiency.
An important distinction for efficient data handling
is the _size_ or _number_ of chunks in a dataset.
The `chunks` keyword in NetCDF, Xarray and similar libraries,
specifies the _size_ of each chunk in a dimension,
not the number of chunks!
Thus,
the smaller a chunk size,
the larger the number of chunks and vice versa.

Consequently,
decreasing the size of chunks
will increase the number of chunks
which in turn can lead to higher memory overhead
due to the larger number of chunks,
rather than direct memory consumption of the data.

| Chunking shape                   | Size or Number of elements in chunk | Number of chunks |
|----------------------------------|-------------------------------------|------------------|
| `{'time':1, 'y':768, 'x':922}`   | (708,096) Smaller                   | Larger           |
| `{'time':168, 'y':384, 'x':288}` | (18,579,456) Larger                 | Smaller          |

While a larger number of smaller chunks might increase overhead,
it doesn't necessarily mean a higher memory footprint.
Memory usage is not exclusively determined by the size or number of chunks.
Rather it depends by how many chunks are loaded into memory at once.
Hence,
even if we have a large number of small chunks,
it won't necessarily increase the total memory used by the data,
as long as we don't load all chunks into memory simultaneously.

!!! quote ""

    Memory usage depends on the number of chunks loaded into memory at once.

The focus is on
the efficiency and optimization of data processing and access,
rather than memory usage implied by the number and size of the chunks.

<!-- Examples: -->

<!-- - `chunks = {'time':1, 'y':768, 'x':922}` -1-> size of each chunk is $1*768*922 = 708096$ -->
<!-- - `chunks = {'time':168, 'y':384, 'x':288}`  -1-> size of each chunk is $168*384*288 = 18579456$ -->

See also :

- [Chunking in HDF5][Chunking in HDF5]
- [https://support.hdfgroup.org/HDF5/doc/Advanced/Chunking/](https://support.hdfgroup.org/HDF5/doc/Advanced/Chunking/)
- [Caching in HDF5][Caching in HDF5]
- [14 Chunking and Deflating Data with NetCDF-4][nc4chunking]

[Chunking in HDF5]: https://portal.hdfgroup.org/display/HDF5/Chunking+in+HDF5
[Caching in HDF5]: https://support.hdfgroup.org/HDF5/doc/RM/RM_H5P.html#Property-SetChunkCache
[nc4chunking]: (https://www.unidata.ucar.edu/software/netcdf/workshops/2011/nc4chunking/)

