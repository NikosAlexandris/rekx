# Kerchunking to JSON

## Example data

Let us work with the following example files
from the SARAH3 climate data records 

``` bash
❯ ls -1
SISin202001010000004231000101MA.nc
SISin202001020000004231000101MA.nc
SISin202001030000004231000101MA.nc
SISin202001040000004231000101MA.nc
```

## Check for consistency

In order to create a Kerchunk reference,
all datasets need to be _identically shaped_ in terms of chunk sizes!
Thus, let us confirm this is the case with our sample data :

``` bash
❯ rekx validate .
✓ All files are consistently shaped!
```

Or we can add `-v` to report the shapes for each _variable_ :

``` bash
❯ rekx validate . -v
✓ All files are consistently shaped!

  Variable        Shape
 ──────────────────────────────
  time            512
  lon             2600
  lon_bnds        2600 x 2
  lat             2600
  lat_bnds        2600 x 2
  SIS             1 x 1 x 2600
  record_status   48
```

## Reference input files

We can proceed to create a JSON Kerchunk reference
for each of the input NetCDF files. 
However,
before producing any new file,
let's `--dry-run` the command in question
to see what _will_ happen :

``` bash
❯ rekx reference . sarah3_sis_kerchunk_references_json -v --dry-run
Dry run of operations that would be performed:
> Reading files in . matching the pattern *.nc
> Number of files matched: 4
> Creating single reference files to sarah3_sis_kerchunk_references_json
```

> `--dry-run` is quite useful -- we need some indication things are right
> before engaging with real massive processing!

This looks okay, so let's give it a real go 

``` bash
❯ rekx reference . sarah3_sis_kerchunk_references_json -v
```

> Note that **Kerchunking processes run in parallel!**

The output of the above command is 

``` bash

❯ tree sarah3_sis_kerchunk_references_json/
[nik      4.0K]  sarah3_sis_kerchunk_references_json/
├── [nik      9.3M]  SISin202001010000004231000101MA.json
├── [nik        32]  SISin202001010000004231000101MA.json.hash
├── [nik      9.3M]  SISin202001020000004231000101MA.json
├── [nik        32]  SISin202001020000004231000101MA.json.hash
├── [nik      9.3M]  SISin202001030000004231000101MA.json
├── [nik        32]  SISin202001030000004231000101MA.json.hash
├── [nik      9.3M]  SISin202001040000004231000101MA.json
└── [nik        32]  SISin202001040000004231000101MA.json.hash

1 directory, 8 files
```

## Aggregate references

Next,
we want to cobine the single references into one file.
Let's dry-run the `combine` command :

``` bash
❯ rekx combine sarah3_sis_kerchunk_references_json sarah3_sis_kerchunk_reference_json --dry-run
Dry run of operations that would be performed:
> Reading files in sarah3_sis_kerchunk_references_json matching the pattern *.json
> Number of files matched: 4
> Writing combined reference file to sarah3_sis_kerchunk_reference_json
```

This also looks fine. So let's create the single reference file

``` bash
❯ rekx combine sarah3_sis_kerchunk_references_json sarah3_sis_kerchunk_reference_json -v
```

The file `sarah3_sis_kerchunk_reference_json` has been created an seems to be a
valid one

``` bash
❯ file sarah3_sis_kerchunk_reference_json
sarah3_sis_kerchunk_reference_json: ASCII text, with very long lines (65536), with no line terminators
```

## Test it!

Let's try to retrieve data over a geographic location though

``` bash
❯ rekx select-json sarah3_sis_kerchunk_reference_json SIS 8 45 --neighbor-lookup nearest -v
✓ Coordinates : 8.0, 45.0.
<xarray.DataArray 'SIS' (time: 192)>
[192 values with dtype=int16]
Coordinates:
    lat      float32 45.03
    lon      float32 8.025
  * time     (time) datetime64[ns] 2020-01-01 ... 2020-01-04T23:30:00
Attributes:
    cell_methods:   time: point
    long_name:      Surface Downwelling Shortwave Radiation
    missing_value:  -999
    standard_name:  surface_downwelling_shortwave_flux_in_air
    units:          W m-2
    _FillValue:     -999
```

The final report of the data series over the location lon, lat `(8, 45)`
verifies that Kerchunking worked as expected.
