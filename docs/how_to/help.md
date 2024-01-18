---
tags:
  - rekx
  - CLI
  - How-To
  - Help
  - Logging
  - Debugging
hide:
  - toc
---

# Help ?

For each and every command, there is a `--help` option. Please consult it to
grasp the details for a command, its arguments and optional parameters, default
values and settings that can further shape the output.

For example,

``` bash exec="true" result="ansi" source="above"
rekx --help
```

The help for the command `shapes`

``` bash exec="true" result="ansi" source="above"
rekx shapes --help
```
# Verbosity

Most of the commands feature an extra `--verbose` or shortly `-v` flag. It'll
make `rekx` to be more communicative about what he did.

For example
check the difference of executing the same command
without `-v`

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_shapes/  # markdown-exec: hide
rekx shapes . --variable-set data --validate-consistency
```

and with `-v`

``` bash exec="true" result="ansi" source="above"
cd data/multiple_files_multiple_shapes/  # markdown-exec: hide
rekx shapes . --variable-set data --validate-consistency -v
```

# Logging

`rekx` is growing and learning as we all do, by trial & error :-).
To get some background information on _how_ `rekx` is crunching data,
we can instruct the `--log` option right before any subcommand :

``` bash exec="true" result="ansi" source="above"
rekx --log inspect data/single_file/SISin202001010000004231000101MA.nc --variable-set data
```

A `.log` is created
containing timestamped details
on the execution of important commands and their output.

Example :

``` bash exec="true" result="ansi" source="above"
cat *.log
```
