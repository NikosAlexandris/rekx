---
tags:
  - How-To
  - rekx
  - CLI
  - Kerchunk
  - JSON
  - SARAH3
  - SIS
---

# Kerchunking to JSON

## Example data

Let us work with the following example files
from the SARAH3 climate data records 

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/
ls -1
```

## Check for consistency

In order to create a Kerchunk reference,
all datasets need to be _identically shaped_ in terms of chunk sizes!
Thus, let us confirm this is the case with our sample data :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx shapes . --validate-consistency
```

Or we can add `-v` to report the shapes for each _variable_ :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx shapes . --validate-consistency -v
```

## Reference input files

We can proceed to create a JSON Kerchunk reference
for each of the input NetCDF files. 
However,
before producing any new file,
let's `--dry-run` the command in question
to see what _will_ happen :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx reference . sarah3_sis_kerchunk_references_json -v --dry-run
```

> `--dry-run` is quite useful -- we need some indication things are right
> before engaging with real massive processing!

This looks okay, so let's give it a real go 

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx reference . sarah3_sis_kerchunk_references_json -v
```

> Note that **Kerchunking processes run in parallel!**

The output of the above command is 

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
tree sarah3_sis_kerchunk_references_json/
```

## Aggregate references

Next,
we want to cobine the single references into one file.
Let's dry-run the `combine` command :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx combine sarah3_sis_kerchunk_references_json sarah3_sis_kerchunk_reference_json --dry-run
```

!!! warning

    In the above example not the subtle name difference :
    `sarah3_sis_kerchunk_references_json` != `sarah3_sis_kerchunk_reference_json`

This also looks fine. So let's create the single reference file

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx combine sarah3_sis_kerchunk_references_json sarah3_sis_kerchunk_reference_json -v
```

The file `sarah3_sis_kerchunk_reference_json` has been created an seems to be a
valid one

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
file sarah3_sis_kerchunk_reference_json
```

## Test it!

Let's try to retrieve data over a geographic location though

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx select-json sarah3_sis_kerchunk_reference_json SIS 8 45 --neighbor-lookup nearest -v
```

The final report of the data series over the location lon, lat `(8, 45)`
verifies that Kerchunking worked as expected.
