---
tags:
  - NetCDF
  - Time Series
  - Kerchunk
  - Python
hide:
  - navigation
  - toc
---

# rekx :fontawesome-solid-cubes:🦖

![License](https://img.shields.io/badge/License-EUPL--1.2-blue.svg)
![GitHub tag (with filter)](https://img.shields.io/github/v/tag/NikosAlexandris/rekx)
[![Documentation](https://img.shields.io/badge/Documentation-Available-green.svg)](https://nikosalexandris.github.io/rekx/)
[![ci](https://github.com/NikosAlexandris/rekx/actions/workflows/ci.yml/badge.svg)](https://github.com/NikosAlexandris/rekx/actions/workflows/ci.yml)

<!-- <figure markdown> -->
  ![rekx](images/rekx_document_72dpi.png){ align=right }[^*]
  <!-- <figcaption>Image caption</figcaption> -->
  [^*]: <a href="https://www.freepik.com/free-vector/hand-drawn-dinosaur-outline-illustration_58593460.htm#query=trex&position=47&from_view=search&track=sph&uuid=27caf12e-35ea-47ad-a113-2d4f5981f58f">Original T-Rex drawn by pikisuperstar</a> on Freepik
<!-- </figure> -->

!!! danger "Experimental"

    **Everything is under heavy development and subject to change!**
    Interested ? Peek over at the [To Do](to_do.md) list !


# What ?

`rekx` seamlessly interfaces
the [Kerchunk](https://fsspec.github.io/kerchunk/) library [@Durant2023]
in an interactive way through the command line.
It assists in creating virtual aggregate datasets,
also known as Kerchunk reference sets,
which allows for an efficient, parallel and cloud-friendly way
to access data in-situ without duplicating the original datasets.

More than a functional tool,
`rekx` serves an educational purpose on matters around
chunking, compression and efficient data reading
from common scientific file formats such as NetCDF
used extensively to store large time-series.
While there is abundant documentation on such topics,
it is often highly technical
and oriented towards developers,
`rekx` tries to simplify these concepts through practical examples.


# Why ?

Similarly,
existing tools for managing HDF and NetCDF data,
such as `cdo`, `nco`, and others,
often have overlapping functionalities
and present a steep learning curve for non-experts.
`rekx` focuses on practical aspects of efficient data access
trying to simplify these processes.

It features simple command line tools to:

- diagnose data structures
- validate uniform chunking across files
- suggest good chunking shapes
- parameterise the rechunking of datasets.
- create and aggregate Kerchunk reference sets
- time data read operations for performance analysis

`rekx` dedicates to practicality, simplicity, and essence.

!!! enso "The Zen of Chunking"

    Chunks are equal-sized data blocks.

    Chunks are _required_ for _compression_, _extendible_ data
    and _subsetting_ large datasets.
    
    Small chunks lead to a large number of chunks.
    
    Large chunks lead to a small number of chunks.

    Appropriately sized chunks can improve performance.
    
    Unthoughtfully sized chunks will decrease performance.
    
    Good chunk sizes depend on data access patterns.
    
    Good chunk sizes balance read/write operations and computational efficiency.
    
    There is no _one size fits all_.

