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

!!! danger "Proof-of-Concept with an issue pending clarification or/and fix"

    - It works with the following change : 
    [NikosAlexandris/kerchunk/commit/97a016ba1370c11e10e0e068e08188fa34277f18][NikosAlexandris-kerchunk-commit-97a016ba1370c11e10e0e068e08188fa34277f18]

    - Yet not all is good, it seems as per the
    [discussion on the Kerchunk issue # 345][kerchunk-issue-345-comment-1807349725]

    Thus, to reproduce the following example we need to :

    1. Best to create a new virtual environment !

    2. Install `rekx`

        ``` bash
        pip install git+https://github.com/NikosAlexandris/rekx
        ```

    3. Install [Kerchunk with a slightly modified source code of `hdf.py`](https://github.com/NikosAlexandris/kerchunk/commit/97a016ba1370c11e10e0e068e08188fa34277f18) :
    
        ``` bash
        pip install git+https://github.com/NikosAlexandris/kerchunk
        ```

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

??? danger "Error if using the _current_ [Kerchunk version 0.2.2](https://github.com/fsspec/kerchunk/releases/tag/0.2.2)"

    ``` bash
    Combined reference name : combined_kerchunk.parquet
    Failed creating the combined_kerchunk.parquet : 'NoneType' object has no attribute 'split'!
    Traceback (most recent call last):
      File "/software/rekx/rekx/parquet.py", line 303, in combine_parquet_stores_to_parquet
        multifile_kerchunk = mzz.translate()
                             ^^^^^^^^^^^^^^^
      File "/software/rekx/.rekx_virtual_environment/lib/python3.11/site-packages/kerchunk/combine.py", line 497, in translate
        self.first_pass()
      File "/software/rekx/.rekx_virtual_environment/lib/python3.11/site-packages/kerchunk/combine.py", line 259, in first_pass
        value = self._get_value(i, z, var, fn=self._paths[i])
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "/software/rekx/.rekx_virtual_environment/lib/python3.11/site-packages/kerchunk/combine.py", line 235, in _get_value
        o = cftime.num2date(o, units=units, calendar=calendar)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "src/cftime/_cftime.pyx", line 580, in cftime._cftime.num2date
      File "src/cftime/_cftime.pyx", line 95, in cftime._cftime._dateparse
      File "src/cftime/_cftime.pyx", line 76, in cftime._cftime._datesplit
    AttributeError: 'NoneType' object has no attribute 'split'
    ```

## Verify

We verify the aggregated Parquet store is readable

``` bash
❯ rekx read-performance combined_kerchunk.parquet SIS 8 45 -v
Data read in memory in : 0.123 seconds ⚡⚡
<xarray.DataArray 'SIS' (time: 192)>
array([  0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,  46., 114., 179., 238., 290., 333., 359.,
       379., 377., 372., 344., 306., 262., 206., 137.,  69.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,  46., 110., 175.,
       231., 291., 332., 356., 378., 376., 370., 344., 308., 260., 203.,
       137.,  69.,   7.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,  13.,  61.,  74., 112., 142., 162., 185., 251., 251., 176.,
       152., 136., 111.,  84.,  65.,  44.,   3.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.,  46., 105., 173., 236., 259., 322.,
       371., 373., 382., 358., 347., 311., 267., 205., 147.,  74.,   9.,
         0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,   0.,
         0.,   0.,   0.,   0.,   0.], dtype=float32)
Coordinates:
    lat      float32 45.03
    lon      float32 8.025
  * time     (time) datetime64 2020-01-01 ... 2020-01-04T23:30:00
Attributes:
    cell_methods:  time: point
```
