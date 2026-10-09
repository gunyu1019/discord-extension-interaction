"""Shared pytest setup.

Puts the repository root on ``sys.path`` so ``discord.ext.interaction`` resolves
to the working tree even without an editable install. ``discord`` core still
comes from the installed ``discord.py`` (a regular package beats the namespace
portion in the repo).
"""
import pathlib
import sys

_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import discord  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def offline_client():
    """A real ``interaction.Client`` with no gateway connection.

    Construction creates the HTTPClient / connection state but performs no I/O
    until ``login``/``connect``, so it is safe to build in a test.
    """
    from discord.ext import interaction

    return interaction.Client(intents=discord.Intents.none())


@pytest.fixture
def user_payload():
    return {
        "id": "424242424242424242",
        "username": "tester",
        "discriminator": "0",
        "global_name": "tester",
        "avatar": None,
        "public_flags": 0,
    }
