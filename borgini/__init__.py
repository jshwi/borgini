"""
borgini
=======

A wrapper to quickly get you started backing up with borg

An easy to use ini style and profile based format

See README for examples or run ``borgini --help`` for usage
"""
from ._core import HOME, Data, PygmentPrint
from ._main import main
from ._version import __version__

__all__ = ["__version__", "HOME", "PygmentPrint", "Data", "funcs", "main"]
