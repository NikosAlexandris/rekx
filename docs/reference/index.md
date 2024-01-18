---
tags:
  - Context
  - Background
  - Chunking
---

!!! warning

    To sort out!

# Context

## First time questions

- Data format?
- Chunking strategy?
- Reference file customization?

## Background

### Challenges with long-term observations

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


### Data models

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
