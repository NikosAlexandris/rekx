---
tags:
  - To Do
  - How-To
  - rekx
  - CLI
  - Kerchunk
  - Parquet
  - SARAH3
  - SIS
  - read-performance
---

# Kerchunking to Parquet

!!! danger "Proof-of-Concept with an issue pending software updates"

    The example works with :

    - a _suggested_ update for [fsspec][fsspec-git-pull-1492]
    - and a not-yet-released version of [Kerchunk][kerchunk-git@b9659c32449539ef6addcb7a12520715cecf3253]


[fsspec-git-pull-1492]: https://github.com/fsspec/filesystem_spec/pull/1492

[kerchunk-git@b9659c32449539ef6addcb7a12520715cecf3253]: https://github.com/fsspec/kerchunk.git@b9659c32449539ef6addcb7a12520715cecf3253

## Example data

This goes on with the same example data as in [Kerchunking to JSON](kerchunk_to_json.md#example-data).

``` bash
❯ ls -1
SISin202001010000004231000101MA.nc
SISin202001020000004231000101MA.nc
SISin202001030000004231000101MA.nc
SISin202001040000004231000101MA.nc
```

## Reference to Parquet store

We create Parquet stores using the Kerchunk engine 

``` bash
❯ rekx reference-multi-parquet . -v
Creating the following Parquet stores in . :
  SISin202001020000004231000101MA.parquet
  SISin202001030000004231000101MA.parquet
  SISin202001040000004231000101MA.parquet
  SISin202001010000004231000101MA.parquet
Done!
```

Let's check for the new files :

``` bash
❯ ls -1
SISin202001010000004231000101MA.nc
SISin202001010000004231000101MA.parquet
SISin202001020000004231000101MA.nc
SISin202001020000004231000101MA.parquet
SISin202001030000004231000101MA.nc
SISin202001030000004231000101MA.parquet
SISin202001040000004231000101MA.nc
SISin202001040000004231000101MA.parquet
```

There is one `.parquet` store for each input file.


## Combine references

We then combine the multiple Parquet stores into a single one

``` bash
❯ rekx combine-parquet-stores . -v
Combined reference name : combined_kerchunk.parquet
```

We verify the new file is there :

``` bash
❯ ls -1tr
SISin202001030000004231000101MA.nc
SISin202001010000004231000101MA.nc
SISin202001020000004231000101MA.nc
SISin202001040000004231000101MA.nc
SISin202001010000004231000101MA.parquet
SISin202001030000004231000101MA.parquet
SISin202001020000004231000101MA.parquet
SISin202001040000004231000101MA.parquet
combined_kerchunk.parquet
```

## Verify

Does it work ?
We verify the aggregated Parquet store is readable

``` bash
❯ rekx read-performance combined_kerchunk.parquet SIS 8 45 -v
Data read in memory in : 0.132 ⚡⚡
```

`read-performance` won't show more than just the time it took to load the data
in memory.  Let's go a step further and print out the values :

``` bash
❯ rekx select-parquet combined_kerchunk.parquet SIS 8 45
🗴 Something went wrong in selecting the data : "not all values found in index 'lon'. Try setting the
`method` keyword argument (example: method='nearest')."
```

!!! error

    No panic! The above error is a good sign actually since there is no exact
    pair of coordinates at longitude, latitude : (8, 45) over which location
    to retrieve data.

Let's get the closest pair of coordinates that really exists in the data by
instructing the `--neighbor-lookup nearest` option :

``` bash
❯ rekx select-parquet combined_kerchunk.parquet SIS 8 45 --neighbor-lookup nearest
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 46.0, 114.0, 179.0, 238.0,
290.0, 333.0, 359.0, 379.0, 377.0, 372.0, 344.0, 306.0, 262.0, 206.0, 137.0, 69.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 46.0, 110.0, 175.0, 231.0, 291.0, 332.0, 356.0, 378.0, 376.0, 370.0,
344.0, 308.0, 260.0, 203.0, 137.0, 69.0, 7.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 61.0,
74.0, 112.0, 142.0, 162.0, 185.0, 251.0, 251.0, 176.0, 152.0, 136.0, 111.0, 84.0, 65.0, 44.0, 3.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 46.0, 105.0, 173.0, 236.0, 259.0, 322.0, 371.0, 373.0, 382.0,
358.0, 347.0, 311.0, 267.0, 205.0, 147.0, 74.0, 9.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
0.0, 0.0, 0.0, 0.0, 0.0, 0.0
```

or add `-v` for a Xarray-styled output

``` bash
❯ rekx select-parquet combined_kerchunk.parquet SIS 8 45 --neighbor-lookup nearest -v
✓ Coordinates : 8.0, 45.0.
<xarray.DataArray 'SIS' (time: 192)>
array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,  46., 114., 179., 238., 290., 333., 359., 379., 377.,
       372., 344., 306., 262., 206., 137.,  69.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,  46., 110., 175., 231., 291., 332., 356., 378., 376.,
       370., 344., 308., 260., 203., 137.,  69.,   7.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,  13.,  61.,  74., 112., 142., 162., 185., 251., 251.,
       176., 152., 136., 111.,  84.,  65.,  44.,   3.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,  46., 105., 173., 236., 259., 322., 371., 373., 382.,
       358., 347., 311., 267., 205., 147.,  74.,   9.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.],
      dtype=float32)
Coordinates:
    lat      float32 45.03
    lon      float32 8.025
  * time     (time) datetime64[ns] 2020-01-01 ... 2020-01-04T23:30:00
Attributes:
    cell_methods:   time: point
    long_name:      Surface Downwelling Shortwave Radiation
    standard_name:  surface_downwelling_shortwave_flux_in_air
    units:          W m-2

```

Now it worked!  One more option : let's get a statistical overview instead :

``` bash
❯ rekx select-parquet combined_kerchunk.parquet SIS 8 45 --neighbor-lookup nearest --statistics
                   Selected series

           Statistic   Value
 ────────────────────────────────────────────────────
               Start   2020-01-01T00:00:00.000000000
                 End   2020-01-04T23:30:00.000000000
               Count   192

                 Min   0.0
     25th Percentile   0.0
                Mean   72.97396
              Median   0.0
                Mode   0.0
                 Max   382.0
                 Sum   14011.0
            Variance   14933.45
  Standard deviation   122.2025

         Time of Min   2020-01-01T00:00:00.000000000
        Index of Min   0
         Time of Max   2020-01-04T11:30:00.000000000
        Index of Max   167

                     Caption text
```
