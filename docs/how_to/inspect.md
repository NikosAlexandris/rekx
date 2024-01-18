---
tags:
  - How-To
  - rekx
  - CLI
  - Diagnose
  - inspect
---

# Inspect data

`#!bash rekx`
can diagnose the structure of data stored in Xarray-supported file formats.

## A single file

Inspect a single NetCDF file

``` bash exec="true" result="ansi" source="above"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc
```

Perhaps restrict inspection on data variables only

``` bash exec="true" result="ansi" source="above"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data
```

!!! hint

    `rekx` can scan selectively for the following `--variable-set`s :
    `[all|coordinates|coordinates-without-data|data|metadata|time]`.
    List them via `rekx inspect --help`.

or even show _humanised_ size figures

``` bash exec="true" result="ansi" source="above"
rekx inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data --humanize
```

## A directory with multiple files

Let's consider a directory with 2 NetCDF files

``` bash exec="true" result="ansi" source="above"
ls -1 data/multiple_files_unique_shape/
```

and inspect them all,
in this case scanning only for data variables in the _current_ directory

```{.shell linenums="0"}
cd data/multiple_files_unique_shape/
rekx inspect . --variable-set data
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

``` bash exec="true" result="ansi" source="above"
rekx inspect data/multiple_files_unique_shape/ --variable-set data --no-long-table
```

## CSV Output

We all need machine readable output.
Here's how to get one for `rekx`' `inspect` command

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
rekx inspect SISin202001010000004231000101MA.nc --csv SISin202001010000004231000101MA_structure.csv
```

Let's verify it worked well

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_unique_shape/  # markdown-exec: hide
file SISin202001010000004231000101MA_structure.csv
```

!!! note

    Here's how it render's in this documentation page using [mkdocs-table-reader-plugin](https://timvink.github.io/mkdocs-table-reader-plugin/)

    {{ read_csv('data/multiple_files_unique_shape/SISin202001010000004231000101MA_structure.csv') }}
