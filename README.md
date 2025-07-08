# DHV

![DHV](https://raw.githubusercontent.com/davep/dhv/refs/heads/main/.images/dhv.gif)

## Introduction

DHV is a terminal-based tool for diving into Python code, the emphasis for
now being on [bytecode disassembly](https://docs.python.org/3/library/dis.html).

> [!IMPORTANT]
>
> Python's `dis` module is a bit of a moving target; because of this and to
> try and keep the code as clean as possible DHV only works with Python 3.13
> or later.

## Installing

### pipx

The package can be installed using [`pipx`](https://pypa.github.io/pipx/):

```sh
$ pipx install dhv
```

### uv

The package can be install using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```sh
uv tool install --python 3.13 dhv
```

## Using DHV

Once you've installed DHV using one of the above methods, you can run the
application using the `dhv` command.

The best way to get to know DHV is to read the help screen, once in the main
application you can see this by pressing <kbd>F1</kbd>.

## Getting help

If you need help, or have any ideas, please feel free to [raise an
issue](https://github.com/davep/dhv/issues) or [start a
discussion](https://github.com/davep/dhv/discussions).

## TODO

See [the TODO tag in
issues](https://github.com/davep/dhv/issues?q=is%3Aissue+is%3Aopen+label%3ATODO)
to see what I'm planning.

[//]: # (README.md ends here)
