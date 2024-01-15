---
tags:
  - How-To
  - rekx
  - CLI
  - Diagnose
  - inspect
  - shapes
---

# Diagnose data structures

`rekx`
can diagnose the structure of data stored in Xarray-supported file formats.

## Data structure

### A single file

Inspect a single NetCDF file

```{.shell linenums="0"}
rekx inspect data/single_file/SISin202001010000004231000101MA.nc
```
``` bash exec="true" result="ansi"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc
```

Perhaps restrict inspection on data variables only

```{.shell linenums="0"}
❯ rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data
```
``` bash exec="true" result="ansi"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data
```

!!! hint

    `rekx` can scan selectively for the following `--variable-set`s :
    `[all|coordinates|coordinates-without-data|data|metadata|time]`.
    List them via `rekx inspect --help`.

or even show _humanised_ size figures

```{.shell linenums="0"}
rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data --humanize
```
``` bash exec="true" result="ansi"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data --humanize
```

### A directory with multiple files

Let's consider a directory with 2 NetCDF files

```{.shell linenums="0"}
❯ ls -1 data/multiple_files_unique_shape/
```
``` bash exec="true" result="ansi"
ls -1 data/multiple_files_unique_shape/
```

and inspect them all,
in this case scanning only for data variables in the _current_ directory

```{.shell linenums="0"}
> cd data/multiple_files_unique_shape/
❯ rekx inspect . --variable-set data
```
``` bash exec="true" result="ansi"
rekx inspect data/multiple_files_unique_shape/ --variable-set data
```

!!! info

    The `.` means in Linux the _current_ working directory

By default,
multiple files are reported on a _long table_.
For whatever the reason might be, we night not want this.
We can instead ask for independent tables per input file :

```{.shell linenums="0"}
❯ rekx inspect data/multiple_files_unique_shape/ --variable-set data --no-long-table
```
``` bash exec="true" result="ansi"
rekx inspect data/multiple_files_unique_shape/ --variable-set data --no-long-table
```

## Chunking shape

The _chunking shape_ refers to the chunk _sizes_ of the variables typically
found in a NetCDF file, or else any Xarray-supported file format.
`rekx` can scan a `source_directory` for files that match a given `pattern`
and report the chunking shapes across all of them.

Following we scan the _current_ directory for filenames starting with `SIS` and
having the suffix `.nc` :

```{.shell linenums="0"}
❯ ls -1 data/multiple_files_multiple_products/
```
``` bash exec="true" result="ansi"
ls -1 data/multiple_files_multiple_products/
```

```{.shell linenums="0"}
❯ rekx shapes data/multiple_files_multiple_products/ --pattern "SIS*.nc" --variable-set data 
```
``` bash exec="true" result="ansi"
 rekx shapes data/multiple_files_multiple_products/ --pattern "SIS*.nc" --variable-set data 
```

### Uniform chunking shape?

We can also verify the uniqueness of one chunking shape across all input files.
To exemplify, in a directory containing :

```{.shell linenums="0"}
❯ ls -1 data/multiple_files_unique_shape/
```
``` bash exec="true" result="ansi"
ls -1 data/multiple_files_unique_shape/
```

we navigate to the directory in question
and scan for chunking shapes in the _current_ directory

```{.shell linenums="0"}
❯ cd data/multiple_files_unique_shape/
❯ rekx shapes .
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_unique_shape/
```

or restrict the scan to _data_ variables only,
as in the `inspect` command example above

```{.shell linenums="0"}
❯ rekx shapes . --variable-set data
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_unique_shape/ --variable-set data
```

We can verify the one and only chunking shape via

``` bash
❯ rekx shapes . --variable-set data --validate-consistency
✓ Variables are consistently shaped across all files!
```

Else, let's scan another directory containing

```{.shell linenums="0"}
❯ ls data/multiple_files_multiple_shapes/
```
``` bash exec="true" result="ansi"
ls data/multiple_files_multiple_shapes/
```

For the following _shapes_

```{.shell linenums="0"}
❯ cd data/multiple_files_multiple_shapes/
❯ rekx shapes . --variable-set data
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_shapes/ --variable-set data
```

and check for _chunking_ consistency and expect a negative response since we
have more than one shape :

```{.shell linenums="0"}
❯ rekx shapes . --variable-set data --validate-consistency
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_shapes/ --variable-set data --validate-consistency
```

Interested for a long table ?
Use the verbosity flag :

```{.shell linenums="0"}
❯ rekx shapes . --variable-set data --validate-consistency -v
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_shapes/ --variable-set data --validate-consistency -v
```

### Maximum common chunking shape

It might be useful to know the maximum common chunking shape
across files of a product series, like the SIS or SID products 
from the SARAH3 climate data records. 

Say for example a directory contains the following SARAH3 products :

```{.shell linenums="0"}
❯ ls data/multiple_files_multiple_products/
```
``` bash exec="true" result="ansi"
ls data/multiple_files_multiple_products/
```

`rekx` will fetch the maximum common shapes like so :

!!! warning "Output format subject to change"

    The output format will likely be modified in one single table
    that features both the _Shapes_ and _Common Shape_ columns

```{.shell linenums="0"}
❯ cd data/multiple_files_multiple_products/
❯ rekx shapes . --variable-set data --common-shapes
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_products/ --variable-set data --common-shapes
```

## Consistency

Consider a case where we want _only_ to know
if our NetCDF data are uniformely chunked or not.
No more or less than a _yes_ or a _no_ answer.
`rekx` can [`validate`][rekx.diagnose]
for a uniform chunking shape across multiple NetCDF files.

Let's list some NetCDF files which differ in terms of their chunking shapes :

```{.shell linenums="0"}
❯ ls data/multiple_files_multiple_products/*.nc
```
``` bash exec="true" result="ansi"
ls data/multiple_files_multiple_products/*.nc
```

From the file names, we expect to have at least two different chunking shapes.
Let's try first with the files named after a common pattern :

```{.shell linenums="0"}
❯ cd data/multiple_files_multiple_products/
❯ rekx shapes . --pattern "SIS*MA.nc" --validate-consistency
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_products/ --pattern "SIS*MA.nc" --validate-consistency
```

Indeed, the requested files are chunked identically.
What about the other file `SISin200001010000004231000101MA_1_2600_2600.nc` ?

```{.shell linenums="0"}
❯ cd data/multiple_files_multiple_products/
❯ rekx shapes . --validate-consistency
```
``` bash exec="true" result="ansi"
rekx shapes data/multiple_files_multiple_products/ --validate-consistency
```

Voilà, this is a _no_ !
