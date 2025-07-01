"""Provides functions and classes for managing the app's data."""

##############################################################################
# Local imports.
from .config import (
    Configuration,
    load_configuration,
    save_configuration,
    update_configuration,
)

##############################################################################
# Exports.
__all__ = [
    "Configuration",
    "load_configuration",
    "save_configuration",
    "update_configuration",
]

### __init__.py ends here
