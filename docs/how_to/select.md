---
tags:
  - How-To
  - rekx
  - CLI
  - select
---

# Select

With `rekx` we can retrieve values from Xarray-supported data

``` bash exec="true" result="ansi" source="above"
cd data/single_file/
rekx select SISin202001010000004231000101MA.nc SIS 8 45
```

or print the regular Xarray-style data array overview

``` bash exec="true" result="ansi" source="above"
cd data/single_file/  # markdown-exec: hide
rekx select SISin202001010000004231000101MA.nc SIS 8 45 -v
```
