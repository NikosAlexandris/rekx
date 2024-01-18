---
tags:
  - To Do
  - How-To
  - rekx
  - CLI
  - Rechunk
  - NetCDF
  - nccopy
---

# `rekx rechunk`

!!! warning

    `rekx rechunk` **yet not implemented!**

# `nccopy`

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

## Rechunking Performance

Rechunking existing dataset can be time-consuming
especially for large datasets.
Tools like `nccopy` for netCDF-4 and `h5repack` for both HDF5 and netCDF-4
are available for rechunking.
Usually it takes a small multiple of the time to copy the data
from one file to another.

### Example of `nccopy` operations

Timing the rechunking of SID files from the SARAH3 collection using
`nccopy` on a laptop-with-ssd [^laptop-with-ssd]

[^laptop-with-ssd]: Laptop with SSD disk

<!-- ``` bash -->
<!-- ❯ mlr --csv --oxtab --opprint put '$Duration = (${Duration 1} + ${Duration 2} + ${Duration 3}) /3' then cut -f Time,Latitude,Longitude,Duration then sort -n Duration rechunking_timings_old.noncsv -->
<!-- ``` -->
!!! inline end danger "Why does it take 300+ seconds?"

    Why does the duration of rechunking jump from ~15 to 300+ seconds for some
    chunkings shape combinations where the chunk size for `time` is 48 ?

| Time | Latitude | Longitude | Duration[^D]       |
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

[^D]: Average of 3 repetitions
