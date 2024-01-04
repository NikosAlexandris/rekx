# Chunking parameterisation

## Combining parameters

Identifying the _appropriate_ configuration for data stored in NetCDF files,
involves systematic experimentation with various structural parameters.
The `rechunk-generator` command
varies structural data parameters and options for NetCDF files
that influence the file size and data access speed
and generates a series of `nccopy` commands for rechunking NetCDF files.
The list of commands can be fed to the mighty GNU Parallel tool
which will take care to run them in parallel.
Subsequently, `rekx inspect-multiple` will report on the new data structeres
and measure the average time it takes to read data over a geographic location.

Given the initial NetCDF file `SISin202001010000004231000101MA.nc`,
we can generate a series of experimental `nccopy` commands :

```bash
❯ rekx rechunk-generator SISin202001010000004231000101MA.nc rechunking_test --time 48 --latitude 64,128,256 --longitude 64,128,256 --compression-level 0,3,6,9 -v --shuffling --memory
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

We let GNU Parallel to execute these in parallel

``` bash
parallel < rechunk_commands_for_SISin202001010000004231000101MA.txt
```

While the output comprises as many new NetCDF files as the `nccopy` commands,
for the sake of showcasing `rekx`,
let us only inspect new NetCDF files whose filename contains the string `256` :

``` bash
❯ rekx inspect rechunking_test --repetitions 3 --humanize --long-table --variable-set data --pattern "*256*"

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

The output reports on dataset structure, chunking, compression levels,
and the average time to read data over a geographic location.
Analysing such results, can guide us in choosing an effective chunking shape
and compression strategy in order to optimize our data structure.
