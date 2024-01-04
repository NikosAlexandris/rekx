# Kerchunking to Parquet

!!! danger "Proof-of-Concept with an issue pending clarification or/and fix"

    Be warned : the document example here is a Proof-of-Concept.

    - It works with the following change : 
    [NikosAlexandris/kerchunk/commit/97a016ba1370c11e10e0e068e08188fa34277f18][NikosAlexandris-kerchunk-commit-97a016ba1370c11e10e0e068e08188fa34277f18]

    - Yet not all is good, it seems as per the
    [discussion on the Kerchunk issue # 345][kerchunk-issue-345-comment-1807349725]

[NikosAlexandris-kerchunk-commit-97a016ba1370c11e10e0e068e08188fa34277f18]: https://github.com/NikosAlexandris/kerchunk/commit/97a016ba1370c11e10e0e068e08188fa34277f18

[kerchunk-issue-345-comment-1807349725]: https://github.com/fsspec/kerchunk/issues/345#issuecomment-1807349725

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

## Combine references

We then combine the multiple Parquet stores into a single one

``` bash
❯ rekx combine-parquet-stores . -v
Combined reference name : combined_kerchunk.parquet
```

## Verify

We verify the aggregated Parquet store is readable

``` bash
❯ rekx read-parquet combined_kerchunk.parquet SIS 8 45 '2020-01-01' --neighbor-lookup nearest
Data retrieval took 0.17 seconds ⚡⚡
Selected data : <xarray.DataArray 'SIS' (time: 1)>
array([0.], dtype=float32)
Coordinates:
    lat      float32 45.03
    lon      float32 8.025
  * time     (time) datetime64 2020-01-01
Attributes:
    cell_methods:  time: point
```
