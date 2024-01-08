---
tags:
  - To Do
  - Notes
  - Unsorted
---

# Unsorted notes

!!! warning

    To sort out!

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


**Problems Using Chunking**

Issues that can cause performance problems with chunking include:

- Very small chunks can create very large datasets which can degrade access performance.

    - The smaller the chunk size the more chunks that HDF5 has to keep track of,
    and the more time it will take to search for a chunk.

- Very large chunks need to be read and uncompressed entirely before any access operation.

    - There can be a performance penalty for reading a small subset, if the chunk size is substantially larger than the subset. Also, a dataset may be larger than expected if there are chunks that only contain a small amount of data.

- Smaller chunk-cache than the predefined chunk size. 

    - A chunk does not fit in the Chunk Cache. Every chunked dataset has a chunk cache associated with it that has a default size of 1 MB. The purpose of the chunk cache is to improve performance by keeping chunks that are accessed frequently in memory so that they do not have to be accessed from disk.
    - If a chunk is too large to fit in the chunk cache, it can significantly degrade performance.

It is a good idea to:

- Avoid very small chunk sizes
- Be aware of the 1 MB chunk cache size default
- Test the data with different chunk sizes to determine the optimal chunk size to use.
- Consider the chunk size in terms of the most common access patterns for the data.

See also : 

- [https://docs.hdfgroup.org/hdf5/develop/_l_b_com_dset.html](https://docs.hdfgroup.org/hdf5/develop/_l_b_com_dset.html)

- [https://docs.hdfgroup.org/hdf5/develop/_l_b_dset_layout.html](https://docs.hdfgroup.org/hdf5/develop/_l_b_dset_layout.html)

- [https://ntrs.nasa.gov/api/citations/20180008456/downloads/20180008456.pdf](https://ntrs.nasa.gov/api/citations/20180008456/downloads/20180008456.pdf)

- [https://www.hdfgroup.org/2017/05/hdf5-data-compression-demystified-2-performance-tuning/](https://www.hdfgroup.org/2017/05/hdf5-data-compression-demystified-2-performance-tuning/)

- [https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html#default_chunking_4_1](https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html#default_chunking_4_1)

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
