"""Compatibility alias for :mod:`discord.ext.interaction.implementation.sync_planner`."""

import importlib as _importlib
import sys as _sys

_sys.modules[__name__] = _importlib.import_module(
    "discord.ext.interaction.implementation.sync_planner"
)
