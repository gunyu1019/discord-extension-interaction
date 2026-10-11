"""Compatibility alias for :mod:`discord.ext.interaction.models.section`."""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module(
    "discord.ext.interaction.models.section"
)
