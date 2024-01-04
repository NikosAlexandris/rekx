---
tags:
  - How-To
  - Help
  - CLI
---

# Help ?

For each and every command, there is a `--help` option. Please consult it to
grasp the details for a command, its arguments and optional parameters, default
values and settings that can further shape the output.

For example,

``` bash
rekx
```

returns (**currently**)

```
 Usage: rekx [OPTIONS] COMMAND [ARGS]...

 🙾  🦖 Rekx command line interface prototype

╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --version                                                    Show the version and exit.                │
│ --install-completion        [bash|zsh|fish|powershell|pwsh]  Install completion for the specified      │
│                                                              shell.                                    │
│                                                              [default: None]                           │
│ --show-completion           [bash|zsh|fish|powershell|pwsh]  Show completion for the specified shell,  │
│                                                              to copy it or customize the installation. │
│                                                              [default: None]                           │
│ --help                                                       Show this message and exit.               │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Diagnose chunking layout ─────────────────────────────────────────────────────────────────────────────╮
│ inspect        Inspect Xarray-supported data                                                           │
│ shapes         Diagnose chunking shapes in multiple Xarray-supported data                              │
│ common-shape   Determine common chunking shape in multiple Xarray-supported data                       │
│ validate       Validate chunk size consistency along multiple Xarray-supported data                    │
│ validate-json  Validate chunk size consistency along multiple Kerchunk reference files How to get      │
│                available variables?                                                                    │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Suggest chunking layout ────────────────────────────────────────────────────────────────╮
│ suggest              Suggest a good chunking shape, ex. '8784,2600,2600' Needs a review! │
│ suggest-alternative  Suggest a good chunking shape Merge to suggest                      │
│ suggest-symmetrical  Suggest a good chunking shape Merge to suggest                      │
╰──────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Rechunk data ──────────────────────────────────────────────────────────────────────────────────╮
│ modify-chunks      Modify in-place the chunk size metadata in NetCDF files Yet not implemented! │
│ rechunk            Rechunk data                                                                 │
│ rechunk-generator  Generate variations of rechunking commands for multiple files                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Create references ────────────────────────────────────────────────────────────────────────────────────╮
│ reference                Create Kerchunk JSON reference files                                          │
│ reference-parquet        Create Parquet references to an HDF5/NetCDF file Merge to reference           │
│ reference-multi-parquet  Create Parquet references to multiple HDF5/NetCDF files Merge to              │
│                          reference-parquet                                                             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Combine references ───────────────────────────────────────────────────────────────────────────────────╮
│ combine                 Combine Kerchunk reference sets (JSONs to JSON)                                │
│ combine-to-parquet      Combine Kerchunk reference sets into a single Parquet store (JSONs to Parquet) │
│ combine-parquet-stores  Combine multiple Parquet stores (Parquets to Parquet)                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Select from time series ──────────────────────────────────────────────────────────────────────────────╮
│ select         Select time series over a location                                                     │
│ select-fast    Bare read time series from Xarray-supported data and optionally write to CSV  ⏲        │
│              Performance Test                                                                          │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Select from Kerchunk references ──────────────────────────────────────────────────────────────────────╮
│ select-json                Select time series over a location from a JSON Kerchunk reference set      │
│ select-json-from-memory    Select time series over a location from a JSON Kerchunk reference set in   │
│                          memory                                                                        │
│ select-parquet            Select data from a Parquet references store                                 │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─  ⏲ Read performance  ────────────────────────────────────────────╮
│ read            Bare read time series from Xarray-supported data │
│ read-parquet   Read data from a Parquet references store         │
╰───────────────────────────────────────────────────────────────────╯
```

The help for the command `shapes`

``` bash
rekx shapes --help
```

is (**currently**)

``` bash
❯ rekx shapes --help

 Usage: rekx shapes [OPTIONS] SOURCE_DIRECTORY

 Diagnose chunking shapes in multiple Xarray-supported data

╭─ Time series ──────────────────────────────────────────────────────────────────────────────────────────╮
│ *    source_directory      PATH  Source directory path [default: None] [required]                      │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ──────────────────────────────────────────────────────────────────────────────────────────────╮
│ --pattern             TEXT                                     Filename pattern to match               │
│                                                                [default: *.nc]                         │
│ --variable-set        [all|coordinates|coordinates-without-da  Set of Xarray variables to diagnose     │
│                       ta|data|metadata|time]                   [default: XarrayVariableSet.all]        │
│ --help                                                         Show this message and exit.             │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Input / Output ───────────────────────────────────────────────────────────────────────────────────────╮
│ --csv              PATH     CSV output filename [default: None]                                        │
│ --verbose  -v      INTEGER  Show details while executing commands [default: 0]                         │
╰────────────────────────────────────────────────────────────────────────────────────────────────────────
```
