"""Convert Discord resolved data into discord.py objects at the adapter boundary."""

import discord
from discord.channel import _channel_factory

from discord.ext.interaction.implementation.message import Message
from discord.ext.interaction.implementation.resolved import resolve_attachment


def resolve_target(context, target_type: str, target_id: int | str | None):
    """Resolve a user, member, role, channel, message or attachment by ID."""
    if target_id is None:
        return None
    key = str(target_id)
    kind = "messages" if target_type == "message" else target_type
    if kind == "attachments":
        return resolve_attachment(context, target_id)

    data = context._resolved.get(kind, {}).get(key)
    if data is None:
        return None

    if kind == "messages":
        return Message(state=context._state, channel=context.channel, data=dict(data))
    if kind == "users":
        return discord.User(data=data, state=context._state)

    guild_id = context.guild_id
    if kind in ("members", "roles") and guild_id is None:
        return None
    guild = context.guild or (discord.Object(id=int(guild_id)) if guild_id else None)

    if kind == "members":
        member_data = dict(data)
        user_data = context._resolved.get("users", {}).get(key)
        if user_data is None:
            return None
        member_data["user"] = user_data
        return discord.Member(data=member_data, state=context._state, guild=guild)
    if kind == "roles":
        return discord.Role(data=data, state=context._state, guild=guild)
    if kind == "channels":
        channel_data = dict(data)
        factory, channel_type = _channel_factory(channel_data["type"])
        if factory is None:
            raise discord.InvalidData(
                "Unknown channel type {type} for channel ID {id}.".format_map(
                    channel_data
                )
            )
        if channel_type in (discord.ChannelType.group, discord.ChannelType.private):
            return factory(
                me=context.client.user, data=channel_data, state=context._state
            )
        channel_data.setdefault("position", None)
        channel_guild_id = channel_data.get("guild_id") or guild_id
        if channel_guild_id is None:
            return None
        channel_guild = context.client.get_guild(
            int(channel_guild_id)
        ) or discord.Object(id=int(channel_guild_id))
        return factory(guild=channel_guild, state=context._state, data=channel_data)
    return None
