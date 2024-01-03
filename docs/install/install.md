# Installation

> **Everything is experimental and subject to change!**

## Virtual environment

Before all, **create a virtual environment!**

Regardless of your favourite programming language
or tool to manage environments
chances are high you'd benefit from using [`direnv`][direnv].
In the context of a Python package, like [`rekx`][rekx], `direnv` supports all such
well known tools from standard `venv`, `pyenv` and `pipenv`, to `anaconda`, `Poetry`, `Hatch`, `Rye` and `PDM`.
Have a look at [direnv's Wiki page for Python][direnv-wiki-python].

## `pip install`

Once inside a dedicated virtual environment,
we can install `rekx` using `pip` : 

``` bash
pip install git+https://github.com/NikosAlexandris/rekx
```

[rekx]: https://github.com/NikosAlexandris/rekx

[direnv-wiki-python]: https://github.com/direnv/direnv/wiki/Python

[direnv]: https://direnv.net/
