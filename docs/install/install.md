---
tags:
  - rekx
  - Python
  - install
  - pip
  - direnv
  - virtual environment
---

# Install

!!! danger "Experimental"

    **Everything is under heavy development and subject to change!**

## Virtual environment

Before all, **create a [virtual environment][venv]!**

[venv]: https://docs.python.org/3/library/venv.html

Regardless of our favourite programming language
or tool to manage environments,
chances are high we'd benefit from using [`direnv`][direnv].
In the context of a Python package, like [`rekx`][rekx], `direnv` supports all such
well known tools from standard `venv`, `pyenv` and `pipenv`, to `anaconda`, `Poetry`, `Hatch`, `Rye` and `PDM`.
Have a look at [direnv's Wiki page for Python][direnv-wiki-python].


???+ info

    `rekx` is developed inside a virtual environment (re-)created and
    (re-)activated via `direnv`. The following `.envrc` does all of it :
    
    ``` title=".envrc"
    --8<-- ".envrc"
    ```

    Finf more about `layout python` in
    [direnv/wiki/Python#venv-stdlib-module](https://github.com/direnv/direnv/wiki/Python#venv-stdlib-module).


## `pip install`

Once inside a dedicated virtual environment,
we can install `rekx` using `pip` : 

``` bash
pip install git+https://github.com/NikosAlexandris/rekx
```

## `pip uninstall`

Done with `rekx` ?  Uninstall via

``` bash
pip uninstall rekx
```

Of course,
we can remove the entire virtual environment we created for it!

??? tip "Clean pip cache?"

    In case we need to clean it from the cache too, we can do

    ```bash
    pip cache remove rekx
    ```

## Verify

``` bash
..
```

[rekx]: https://github.com/NikosAlexandris/rekx

[direnv-wiki-python]: https://github.com/direnv/direnv/wiki/Python

[direnv]: https://direnv.net/
