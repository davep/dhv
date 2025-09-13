# DHV ChangeLog

## Unrelased

**Released: WiP**

- Migrated from `rye` to `uv` for development management.
  ([#21](https://github.com/davep/dhv/pull/21))
- Added Python 3.14 as a tested/supported Python version.
  ([#22](https://github.com/davep/dhv/pull/22))
- Unpinned `tree-sitter`.
- Pinned to Textual v6.1.0 or later.

## v0.4.1

**Released: 2025-07-21**

- Pinned `tree-sitter` to `<0.25.0` because Textual isn't compatible with
  the latest version and now causes a crash (see
  [issues#5976](https://github.com/Textualize/textual/issues/5976)).

## v0.4.0

**Released: 2025-07-16**

- Added a command to set the theme for the code editor panel.
  ([#12](https://github.com/davep/dhv/pull/12))
- Added support for jumping to the AST documentation from the AST panel.
  ([#13](https://github.com/davep/dhv/pull/13))

## v0.3.0

**Released: 2025-07-12**

- Added support for viewing the AST of the Python code.
  ([#8](https://github.com/davep/dhv/pull/8))

## v0.2.0

**Released: 2025-07-09**

- Added the ability to pass a filename on the command line.
  ([#5](https://github.com/davep/dhv/pull/5))

## v0.1.1

**Released: 2025-07-08**

- Initial release.

## v0.1.0

**Released: 2025-07-01**

- Initial placeholder package to test that the name is available in PyPI.

[//]: # (ChangeLog.md ends here)
