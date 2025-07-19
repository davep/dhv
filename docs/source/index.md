# Introduction

```{.textual path="docs/screenshots/basic_app.py" title="DHV" lines=40 columns=120 press="ctrl+o"}
```

DHV is a Python code exploration tool for the terminal, designed to let you
type in, load up, and edit Python code, and see what the resulting abstract
syntax tree and bytecode looks like.

If you've ever felt curious about what your Python source code gets turned
into, this is one tool that might help satisfy that curiosity.

## Installation

!!! note

    DHV requires [Python 3.13](https://docs.python.org/3/whatsnew/3.13.html) or later.

### pipx

The application can be installed using [`pipx`](https://pypa.github.io/pipx/):

```
pipx install dhv
```

### uv

The package can be install using [`uv`](https://docs.astral.sh/uv/getting-started/installation/):

```
uv tool install --python 3.13 dhv
```

## Running DHV

Once you've installed DHV using one of the [above methods](#installation),
you can run the application using the `dhv` command.

### Command line options

DHV has a number of command line options; they include:

#### `-b`, `--bindings`

Prints the application commands whose keyboard bindings can be modified,
giving the defaults too.

```sh
dhv --bindings
```
```bash exec="on" result="text"
dhv --bindings
```

#### `-h`, `--help`

Prints the help for the `dhv` command.

```sh
dhv --help
```
```bash exec="on" result="text"
dhv --help
```

#### `--license`, `--licence`

Prints a summary of DHV's license.

```sh
dhv --license
```
```bash exec="on" result="text"
dhv --license
```

#### `-t`, `--theme`

Sets DHV's theme; this overrides and changes any previous theme choice made
[via the user interface](configuration.md#theme).

To see a list of available themes use `?` as the theme name:

```sh
dhv --theme=?
```
```bash exec="on" result="text"
dhv --theme=?
```

#### `-v`, `--version`

Prints the version number of DHV.

```sh
dhv --version
```
```bash exec="on" result="text"
dhv --version
```

## Getting help

A great way to get to know DHV is to read the help screen. Once in the
application you can see this by pressing <kbd>F1</kbd>.

```{.textual path="docs/screenshots/basic_app.py" title="The DHV Help Screen" press="f1" lines=50 columns=120}
```

The help will adapt to which part of the screen has focus, providing extra
detail where appropriate.

### The command palette

Another way of discovering commands and keys in DHV is to use the command
palette (by default you can call it with <kbd>ctrl</kbd>+<kbd>p</kbd> or
<kbd>meta</kbd>+<kbd>x</kbd>).

```{.textual path="docs/screenshots/basic_app.py" title="The DHV Command Palette" press="ctrl+p" lines=50 columns=120}
```

## Questions and feedback

If you have any questions about DHV, or you have ideas for how it might be
improved, do please feel free to [visit the discussion
area](https://github.com/davep/dhv/discussions) and [ask your
question](https://github.com/davep/dhv/discussions/categories/q-a) or
[suggest an
improvement](https://github.com/davep/dhv/discussions/categories/ideas).

When doing so, please do search past discussions and also [issues current
and previous](https://github.com/davep/dhv/issues) to make sure I've not
already dealt with this, or don't have your proposed change already flagged
as something to do.

[//]: # (index.md ends here)
