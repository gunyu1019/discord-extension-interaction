"""Resolved Discord entities share one conversion path across interactions."""

from types import SimpleNamespace

import discord

from discord.ext.interaction.implementation.resolved_objects import resolve_target


def _context(offline_client, user_payload):
    user_id = user_payload["id"]
    resolved = {
        "users": {user_id: user_payload},
        "members": {user_id: {"roles": [], "flags": 0}},
        "roles": {"600": {"id": "600", "name": "admin"}},
        "channels": {"700": {
            "id": "700", "guild_id": "300", "type": 0, "name": "general",
        }},
        "attachments": {"900": {
            "id": "900", "filename": "file.txt", "size": 3,
            "url": "https://cdn.discordapp.com/attachments/1/900/file.txt",
            "proxy_url": "https://media.discordapp.net/attachments/1/900/file.txt",
        }},
        "messages": {"800": {
            "id": "800", "channel_id": "400", "author": user_payload,
            "content": "hello", "timestamp": "2026-10-09T00:00:00+00:00",
            "edited_timestamp": None, "tts": False,
            "mention_everyone": False, "mentions": [], "mention_roles": [],
            "attachments": [], "embeds": [], "pinned": False, "type": 0,
        }},
    }
    return SimpleNamespace(
        _resolved=resolved,
        _state=offline_client._connection,
        guild_id="300",
        guild=None,
        client=offline_client,
        channel=discord.PartialMessageable(
            state=offline_client._connection, id=400, type=discord.ChannelType.text
        ),
    )


def test_user_member_role_channel_and_attachment_resolve(offline_client, user_payload):
    context = _context(offline_client, user_payload)
    user_id = user_payload["id"]

    user = resolve_target(context, "users", user_id)
    member = resolve_target(context, "members", user_id)
    role = resolve_target(context, "roles", "600")
    channel = resolve_target(context, "channels", "700")
    attachment = resolve_target(context, "attachments", "900")

    assert isinstance(user, discord.User)
    assert isinstance(member, discord.Member)
    assert member.id == int(user_id)
    assert isinstance(role, discord.Role) and role.name == "admin"
    assert isinstance(channel, discord.TextChannel) and channel.name == "general"
    assert isinstance(attachment, discord.Attachment) and attachment.filename == "file.txt"
    assert "user" not in context._resolved["members"][user_id]
    assert "position" not in context._resolved["channels"]["700"]


def test_message_and_missing_resolved_values(offline_client, user_payload):
    context = _context(offline_client, user_payload)
    message = resolve_target(context, "message", "800")
    assert isinstance(message, discord.Message)
    assert message.content == "hello"
    assert resolve_target(context, "users", "999") is None
    assert resolve_target(context, "members", "999") is None
    assert resolve_target(context, "roles", "999") is None
    assert resolve_target(context, "channels", "999") is None
    assert resolve_target(context, "message", "999") is None
