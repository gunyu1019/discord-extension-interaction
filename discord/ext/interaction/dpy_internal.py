"""The single place where this package touches discord.py internals.

discord.py does not document the names below, so a minor release can rename or
remove them. Every other module imports them from here, which keeps an upgrade
break to one file and turns a missing name into one explicit error instead of an
``ImportError`` deep inside a feature module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from discord.channel import _channel_factory as channel_factory
    from discord.flags import MessageFlags
    from discord.http import handle_message_parameters
    from discord.utils import _from_json as from_json
    from discord.utils import _to_json as to_json
    from discord.webhook.async_ import (
        interaction_message_response_params,
        interaction_response_params,
    )
except ImportError as error:  # pragma: no cover - depends on the installed version
    raise ImportError(
        "discord.ext.interaction needs a discord.py internal that this discord.py "
        f"version does not provide ({error}). Supported range: discord.py>=2.7.1,<3."
    ) from error

if TYPE_CHECKING:
    from discord.state import ConnectionState

__all__ = (
    "channel_factory",
    "connection_state",
    "from_json",
    "get_guild_channel",
    "handle_message_parameters",
    "interaction_message_response_params",
    "interaction_response_params",
    "message_flags_from_value",
    "to_json",
)


def connection_state(client) -> ConnectionState:
    """Return the client's private ``ConnectionState``."""
    return getattr(client, "_connection")


def get_guild_channel(state: ConnectionState, data: dict):
    """Return ``(channel, guild)`` for a gateway payload (``_get_guild_channel``)."""
    return state._get_guild_channel(data)


def message_flags_from_value(value: int) -> MessageFlags:
    """Build :class:`discord.MessageFlags` from a raw integer value."""
    return MessageFlags._from_value(value)
