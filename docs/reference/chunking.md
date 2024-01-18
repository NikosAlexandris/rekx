---
tags:
  - Context
  - Chunking
---

!!! warning

    To sort out!


# What is Chunking ?

**Chunking splits data for easier reading**.

In _physical_ terms, a data variable is contiguous.
However, and especially in the case of NetCDF/HDF files,
the _physical storage_ of the data on disk,
is _chunked_ in fixed and equal-sized pieces.

**Original**

| Hex                          | Text                        |
|------------------------------|-----------------------------|
| `01 02 03 04 05 06 07 08 09` | `1, 2, 3, 4, 5, 6, 7, 8, 9` |

<!-- . -->
**Chunked**

| Hex                                                                                                               |                     Text                     | Size | Number |
|-------------------------------------------------------------------------------------------------------------------|:--------------------------------------------:|------|--------|
| **`AA 05 01`** `01 02 03 04 05` **`AA 05 01`** `06 07 08 09 -`                                                    |      `[1, 2, 3, 4, 5]` `[6, 7, 8, 9, -]`     | 5    | 2      |
| **`AA 04 01`** `01 02 03 04` **`AA 04 01`** `05 06 07 08` **`AA 04 01`** `09 - - -`                               | `[1, 2, 3, 4]` `[5, 6, 7, 8]` `[9, -, -, -]` | 4    | 3      |
| **`AA 03 01`** `01 02 03` **`AA 03 01`** `04 05 06` **`AA 03 01`** `07 08 09`                                     |      `[1, 2, 3]` `[4, 5, 6]` `[7, 8, 9]`     | 3    | 3      |
| **`AA 02 01`** `01 02` **`AA 02 01`** `03 04` **`AA 02 01`** `05 06` **`AA 02 01`** `07 08` **`AA 02 01`** `09 -` | `[1, 2]` `[3, 4]` `[5, 6]` `[7, 8]` `[9, -]` | 2    | 5      |

> **`AA 0? 01`** sequences mark the _start_ of a chunk


# Why ?

While chunking does not affect the logical relationship of data of a variable,
the read/write operations may be impacted heavily.
Chunking can optimize read operations for accessing data in various ways :

    - by rows
    - by columns
    - as a rectangular subgrid

The idea is to _minimize the number of disk accesses_.
  

# How ?

By aligning chunk sizes/borders
with the most common or preferred data access patterns.

## Good chunking shapes

   - For 2D data,
     rectangular chunks help balance the disk access times for
     both row-wise and column-wise access.

   - For 3D data or higher,
     the chunking strategy may need to be adjusted based
     on the most common access patterns.

## Optimal layout?

An algorithm discussed in 
["Chunking Data: Choosing Shapes", by RussRew](https://www.unidata.ucar.edu/blogs/developer/en/entry/chunking_data_choosing_shapes) : 
[chunk_shape_3D.py](https://www.unidata.ucar.edu/blog_content/data/2013/chunk_shape_3D.py)

!!! seealso

    - [How to **`suggest`**](how_to/suggest.md) a good chunking shape with `rekx` (**Experimental**)
    - [Source code reference for **`suggest`**](cli/suggest.md)

An algebraic formulation for _optimal chunking_ bases on
_equalizing the number of chunks accessed for a 1D time series and a 2D
horizontal slice in a 3D dataset_.

!!! note

    `rekx` prefers to avoid the word _optimal_, as possible.
    There is no one-size-fits-all and hence, it may be more appropriate
    to speak about _good_, _appropriate_ or _preferred_ chunking.

Let $D$ be the number of values you want in a chunk,
$N$ be the total number of chunks used to partition the array,
and $c$ be a scaling factor derived from $D$ and the dimensions of the array.
The chunk shape would then be given by the formula:

$$c = \left( \frac{D}{{25256 \times 37 \times 256 \times 512}} \right)^{1/4}$$

The resulting chunk shape is obtained by multiplying each dimension size by $c$
and truncating to an integer. The chunk shape will thus be:

$$\text{chunk shape} = \left( \left\lfloor 25256 \times c \right\rfloor,
\left\lfloor 37 \times c \right\rfloor, \left\lfloor 256 \times c
\right\rfloor, \left\lfloor 512 \times c \right\rfloor \right)$$

This formula **assumes** that the optimal chunk shape will distribute the chunks
equally along each dimension, and the scaling factor $c$ is calculated to
ensure the total number of values in a chunk is close to $D$, without
exceeding it.


# Size and number of chunks

!!! tip

   **Important is the total number of chunks.**

Chunks affect both memory usage and processing efficiency.
An important distinction for efficient data handling
is between the _size_ and the _number_ of chunks in a dataset.
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


# Compression

- Chunking splits the data in equal-sized blocks or chunks of a pre-defined size
- Only the chunks of data required are accessed
- The HDF5 file format stores compressed data in chunks 
- a chunk is the _atomic unit_ of compression as well as disk access
- thus, compressed data is forcedly chunked
- rechunking compressed data involves several steps:

    `read` $\rightarrow$ `uncompress` $\rightarrow$ `rechunk` $\rightarrow$ `recompress` $\rightarrow$  `write` new chunks

- rechunking compressed data _can sometimes be faster_ due to savings in disk
  I/O!

Chunking is required for :
    - compression and other filters
    - creating extendible or unlimited dimension datasets
    - subsetting very large datasets to improve performance

While chunking can improve performance for large datasets,
using a chunking layout without considering the consequences of the chunk size,
can lead to poor performance.
Unfortunately,
it is easy to end up with some random and inefficient chunking layout due to ...


# Caching

!!! danger "To Do"

    Discuss about [caching in HDF5][Caching in HDF5]!


# Problems

Issues that can cause performance problems with chunking include:

- Very small chunks can create very large datasets which can degrade access performance.

    - The smaller the chunk size the more chunks that HDF5 has to keep track of,
    and the more time it will take to search for a chunk.

- Very large chunks need to be read and uncompressed entirely before any access operation.

    - There can be a performance penalty for reading a small subset, if the chunk size is substantially larger than the subset. Also, a dataset may be larger than expected if there are chunks that only contain a small amount of data.

- Smaller chunk-cache than the predefined chunk size. 

    - A chunk does not fit in the Chunk Cache. Every chunked dataset has a chunk cache associated with it that has a default size of 1 MB. The purpose of the chunk cache is to improve performance by keeping chunks that are accessed frequently in memory so that they do not have to be accessed from disk.
    - If a chunk is too large to fit in the chunk cache, it can significantly degrade performance.


# Recommendations

It is a good idea to:

- Avoid very small chunk sizes
- Be aware of the 1 MB chunk cache size default
- Test the data with different chunk sizes to determine the optimal chunk size to use.
- Consider the chunk size in terms of the most common access patterns for the data.


# Resources

!!! seealso "See also :"

    Information regarding chunking and various data structure characteristics
    is largely sourced from resources provided by Unidata.
    Recognized as an authoritative entity,
    Unidata is not only the developer but also the maintainer of NetCDF.

<!-- - [Chunking in HDF5][Chunking in HDF5] -->
- [Chunking Data: Choosing Shapes][Chunking Data: Choosing Shapes]

- [Parallel I/O using netCDF, National Supercomputing Service (CSCS)][Parallel I/O using netCDF, CSCS]
- [Chunking and Deflating Data with NetCDF-4 - 2012 Unidata NetCDF Workshop][Unidata NetCDF Workshop 2012]

- [Chunking and Deflating Data with NetCDF-4 - 2011 Unidata NetCDF Workshop][Unidata NetCDF Workshop 2011][@unidata_2011_nc4chunking]

- [Support on Chunking in HDF5][Support on Chunking in HDF5] -- **No longer maintained**

- [Caching in HDF5][Caching in HDF5]

- [https://docs.hdfgroup.org/hdf5/develop/_l_b_com_dset.html](https://docs.hdfgroup.org/hdf5/develop/_l_b_com_dset.html)

- [https://docs.hdfgroup.org/hdf5/develop/_l_b_dset_layout.html](https://docs.hdfgroup.org/hdf5/develop/_l_b_dset_layout.html)

- [https://ntrs.nasa.gov/api/citations/20180008456/downloads/20180008456.pdf](https://ntrs.nasa.gov/api/citations/20180008456/downloads/20180008456.pdf)

- [https://www.hdfgroup.org/2017/05/hdf5-data-compression-demystified-2-performance-tuning/](https://www.hdfgroup.org/2017/05/hdf5-data-compression-demystified-2-performance-tuning/)

- [https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html#default_chunking_4_1](https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html#default_chunking_4_1)

<!-- [Chunking in HDF5]: https://portal.hdfgroup.org/display/HDF5/Chunking+in+HDF5 -->

[Chunking Data: Choosing Shapes]: https://www.unidata.ucar.edu/blogs/developer/en/entry/chunking_data_choosing_shapes

[Parallel I/O using netCDF, CSCS]: https://www.cscs.ch/fileadmin/user_upload/contents_publications/tutorials/fast_parallel_IO/IntroToParallelnetCDF_MC.pdf

[Unidata NetCDF Workshop 2012]: https://www.unidata.ucar.edu/software/netcdf/workshops/most-recent/nc4chunking/index.html

[Unidata NetCDF Workshop 2011]: https://www.unidata.ucar.edu/software/netcdf/workshops/2011/nc4chunking/

[Support on Chunking in HDF5]: https://support.hdfgroup.org/HDF5/doc/Advanced/Chunking/

[Caching in HDF5]: https://support.hdfgroup.org/HDF5/doc/RM/RM_H5P.html#Property-SetChunkCache
