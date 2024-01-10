---
tags:
  - How-To
  - rekx
  - CLI
  - NetCDF
  - Chunking
  - Caching
  - nccopy
  - Parallel processing
  - GNU Parallel
---

!!! danger "Fix Me"

    Explain better the idea, the commands and the example !

# Chunking parameterisation

## Combining parameters

Identifying the _appropriate_ configuration for data stored in NetCDF files,
involves systematic experimentation with various structural parameters.
The `rechunk-generator` command
varies structural data parameters and options for NetCDF files
that influence the file size and data access speed
and generates a series of `nccopy` commands for rechunking NetCDF files.
The list of commands can be fed to 
[GNU Parallel](https://www.gnu.org/software/parallel/)
which will take care to run them in parallel.
Subsequently,
`rekx inspect` can report on the new data structures
and the average time it takes to retrieve data over a geographic location.

Given the initial NetCDF file `SISin202001010000004231000101MA.nc`,
we can use `rekx rechunk-generator` 
to generate a series of experimental `nccopy` commands 
and save them in a file prefixed with
`rechunk_commands_for_` followed after the name of the input NetCDF file :

```bash
❯ rekx rechunk-generator SISin202001010000004231000101MA.nc rechunking_test --time 48 --latitude 64,128,256 --longitude 64,128,256 --compression-level 0,3,6,9 -v --shuffling --memory
```

!!! example

    In this example, we ask for possible chunk sizes for :

    - `time` to be $48$, that is only one size
    
    - `latitude` and `longitude` sizes $64$, $128$ and $256$
    
    - `compression-level`s $0$, $3$, $64$, and $9$

      In addition, we ask for `--shuffling`.
      Since shuffling wouldn't make sense for uncompressed data,
      `rekx` takes care to only add it along with compression levels greater than 0.

    - [`caching` parameters][Caching in HDF5] will be set to the default values since we did not
      specify them

    There are more options and we can list them with the typical --help option.

[Caching in HDF5]: https://support.hdfgroup.org/HDF5/doc/RM/RM_H5P.html#Property-SetChunkCache

The above command will generate

``` bash
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

## Process in parallel

We let the mighty [GNU Parallel](https://www.gnu.org/software/parallel/)
execute these commands in parallel

``` bash
parallel < rechunk_commands_for_SISin202001010000004231000101MA.txt
```

While the output comprises as many new NetCDF files as the `nccopy` commands,
for the sake of showcasing `rekx`,
let us only inspect new NetCDF files whose filename contains the string `256` :

``` bash
❯ rekx inspect rechunking_test --repetitions 3 --humanize --long-table --variable-set data --pattern "*256*"
```

The above command will return

``` bash
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

!!! info

    Note, the reported reading times
    are averages of repeated reads of the data in the memory
    to ensure we are really retrieving data values!
    Look for the `repetitions` parameter in `rekx inspect --help`.

The output reports on dataset structure, chunking, compression levels,
and the average time to read data over a geographic location.
Analysing such results, can guide us in choosing an effective chunking shape
and compression strategy in order to optimize our data structure.


To get a machine readable output of such an analysis, `rekx` can write this out
in a CSV file via the `--csv` option.

!!! warning "Complete Me"

    Complete documentation of this example!

# See also

- [A Utility to Help Benchmark Results: bm_file](https://docs.unidata.ucar.edu/nug/current/netcdf_perf_chunking.html#bm_file)
