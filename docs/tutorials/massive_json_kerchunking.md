---
tags:
  - Tutorial
  - Kerchunk
  - Kerchunking
  - JSON
  - Experimental
  - Revisit-Me
---

# Massive JSON Kerchunking

!!! danger "Experimental"

    Following is an incomplete experiment, eventually worth revisiting.

## Overview

- Creating SARAH3 daily netCDF reference files can take $4+$ hours
- optimizing chunking can reduce this


## Input

- Daily NetCDF files from 1999 to 2021  
  (actually missing a year, so normally it'd be up to 2022) that make up about about 1.2T
    - Each daily NetCDF file contains 48 half-hourly maps of 2600 x 2600 pixels
    - Noted here : mixed chunking shapes between years  
    (e.g. `time, lat, lon` : `1 x 2600 x 2600`, `1 x 1300 x 1300`, and maybe more)
    - rechunked to `1 x 32 x 32`, thus now 1.25T

- A first set of JSON reference files (one reference file per rechunked input NetCDF file) is about ~377G.

- A second step of (24 should be in total) yearly JSON reference files (based on the first reference set) is ~300G

- Finally, the goal is to create a single reference file to cover the complete time series

## Hardware

``` bash
❯ free -hm
              total        used        free      shared  buff/cache   available
Mem:          503Gi       4.7Gi       495Gi       2.8Gi       3.1Gi       494Gi
Swap:            0B          0B          0B
```

## Trials

``` bash
13G Nov  2 10:07 sarah3_sid_reference_1999.json
13G Nov  2 09:58 sarah3_sid_reference_2000.json
13G Nov  2 11:00 sarah3_sid_reference_2001.json
13G Nov  2 11:08 sarah3_sid_reference_2002.json
13G Nov  2 12:04 sarah3_sid_reference_2003.json
13G Nov  2 12:12 sarah3_sid_reference_2004.json
13G Nov  2 13:07 sarah3_sid_reference_2005.json
13G Nov  2 14:29 sarah3_sid_reference_2006.json
13G Nov  2 15:27 sarah3_sid_reference_2007.json
13G Nov  2 16:45 sarah3_sid_reference_2008.json
13G Nov  2 17:43 sarah3_sid_reference_2009.json
13G Nov  2 19:02 sarah3_sid_reference_2010.json
13G Nov  2 19:58 sarah3_sid_reference_2011.json
13G Nov  2 21:25 sarah3_sid_reference_2012.json
13G Nov  2 22:13 sarah3_sid_reference_2013.json
13G Nov  2 23:43 sarah3_sid_reference_2014.json
13G Nov  3 00:36 sarah3_sid_reference_2015.json
13G Nov  3 02:03 sarah3_sid_reference_2016.json
13G Nov  3 02:58 sarah3_sid_reference_2017.json
13G Nov  3 04:24 sarah3_sid_reference_2018.json
13G Nov  3 05:21 sarah3_sid_reference_2019.json
13G Nov  3 06:48 sarah3_sid_reference_2020.json
13G Nov  3 07:41 sarah3_sid_reference_2021.json
```

Trying to combine the above to a single reference set,
fails with the following error message :

``` python
JSONDecodeError: Could not reserve memory block
```

## Take away message

**The limiting factor**
for the size of the reference sets
is **not** the total number of bytes
**but the total number of references**.
Hence,
the chunking scheme is perhaps more important here.
