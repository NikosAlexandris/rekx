---
tags:
  - To Do
  - Notes
  - Unsorted
---

# Unsorted notes

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
