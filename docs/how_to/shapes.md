---
tags:
  - How-To
  - rekx
  - CLI
  - Diagnose
  - shapes
---

# Chunking shape

The _chunking shape_ refers to the chunk _sizes_ of the variables typically
found in a NetCDF file, or else any Xarray-supported file format.
`rekx` can scan a `source_directory` for files that match a given `pattern`
and report the chunking shapes across all of them.

Given the following files in the _current_ directory

``` bash exec="true" result="ansi" source="above"
ls -1 data/multiple_files_multiple_products/
```

we scan for filenames starting with `SIS`
and having the suffix `.nc` :

``` bash exec="true" result="ansi" source="above"
rekx shapes data/multiple_files_multiple_products/ --pattern "SIS*.nc"
```

or restrict the same scan to _data_ variables only

``` bash exec="true" result="ansi" source="above"
rekx shapes data/multiple_files_multiple_products/ --pattern "SIS*.nc" --variable-set data 
```

### Uniform chunking shape?

We can also verify the uniqueness of one chunking shape across all input files.
To exemplify, in a directory containing :

``` bash exec="true" result="ansi" source="above"
ls -1 data/multiple_files_unique_shape/
```

we navigate to the directory in question
and scan for chunking shapes in the _current_ directory

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/
rekx shapes . --variable-set data
```

We can verify the one and only chunking shape via `--validate-consistency`

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx shapes . --variable-set data --validate-consistency
```

Else, let us scan another directory containing the files

``` bash exec="true" result="ansi" source="above"
ls data/multiple_files_multiple_shapes/
```

For the following _shapes_

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_shapes/
rekx shapes . --variable-set data
```

we check for _chunking_ consistency
and expect a negative response since we have more than one shape :

``` bash exec="true" result="ansi"
cd data/multiple_files_multiple_shapes/  # markdown-exec: hide
rekx shapes . --variable-set data --validate-consistency
```

Interested for a long table ?
Use the verbosity flag :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_shapes/  # markdown-exec: hide
rekx shapes . --variable-set data --validate-consistency -v
```

### Maximum common chunking shape

It might be useful to know the maximum common chunking shape
across files of a product series, like the SIS or SID products 
from the SARAH3 climate data records. 

Say for example a directory contains the following SARAH3 products :

``` bash exec="true" result="ansi" source="above"
ls data/multiple_files_multiple_products/
```

`rekx` will fetch the maximum common shapes like so :

!!! warning "Output format subject to change"

    The output format will likely be modified in one single table
    that features both the _Shapes_ and _Common Shape_ columns

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_products/  # markdown-exec: hide
rekx shapes . --variable-set data --common-shapes
```

## Consistency

Consider a case where we want _only_ to know
if our NetCDF data are uniformely chunked or not.
No more or less than a _yes_ or a _no_ answer.
`rekx` can [`validate`][rekx.diagnose]
for a uniform chunking shape across multiple NetCDF files.

Let's list some NetCDF files which differ in terms of their chunking shapes :

``` bash exec="true" result="ansi" source="above"
ls data/multiple_files_multiple_products/*.nc
```

From the file names, we expect to have at least two different chunking shapes.
Let's try first with the files named after a common pattern :

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_products/
rekx shapes . --pattern "SIS*MA.nc" --validate-consistency
```

Indeed, the requested files are chunked identically.
What about the other file `SISin200001010000004231000101MA_1_2600_2600.nc` ?

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_products/
rekx shapes . --validate-consistency
```

Voilà, this is a _no_ !
