"""Resolve command option IDs using the interaction's resolved payload."""

import discord


def resolve_mentionable(context, value):
    """Return a resolved member, user or role, retaining an unknown ID."""
    key = str(value)
    resolved = context._resolved
    guild = context.guild
    snowflake = int(value)

    if key in resolved.get("members", {}) and guild is not None:
        return guild.get_member(snowflake) or context.target("members", target_id=value)
    if key in resolved.get("users", {}):
        return context.client.get_user(snowflake) or context.target(
            "users", target_id=value
        )
    if key in resolved.get("roles", {}) and guild is not None:
        return guild.get_role(snowflake) or context.target("roles", target_id=value)
    return value


def resolve_attachment(context, value):
    """Build an Attachment from resolved.attachments, retaining an unknown ID."""
    data = context._resolved.get("attachments", {}).get(str(value))
    if data is None:
        return value
    return discord.Attachment(data=data, state=context._state)
