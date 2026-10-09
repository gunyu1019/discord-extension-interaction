"""Mentionable and Attachment options use Discord's resolved payload."""

from types import SimpleNamespace

import discord

from discord.ext import interaction
from discord.ext.interaction.serialization.resolved import resolve_mentionable


def _frame(user_payload, options, resolved):
    return {
        "id": "100000000000000000",
        "application_id": "200000000000000000",
        "type": 2,
        "token": "token",
        "version": 1,
        "user": user_payload,
        "channel_id": "300000000000000000",
        "locale": "en-US",
        "data": {
            "id": "400000000000000000",
            "name": "inspect",
            "type": 1,
            "options": options,
            "resolved": resolved,
        },
    }


def _attachment_data():
    return {
        "id": "123",
        "filename": "report.txt",
        "size": 6,
        "url": "https://cdn.discordapp.com/attachments/1/123/report.txt",
        "proxy_url": "https://media.discordapp.net/attachments/1/123/report.txt",
    }


def test_root_mentionable_user_and_attachment_use_resolved(offline_client, user_payload):
    frame = _frame(
        user_payload,
        [{"name": "target", "type": 9, "value": user_payload["id"]},
         {"name": "file", "type": 11, "value": "123"}],
        {"users": {user_payload["id"]: user_payload},
         "attachments": {"123": _attachment_data()}},
    )
    ctx = interaction.ApplicationContext(frame, offline_client)

    assert isinstance(ctx.options["target"], discord.User)
    assert ctx.options["target"].id == int(user_payload["id"])
    assert isinstance(ctx.options["file"], discord.Attachment)
    assert ctx.options["file"].filename == "report.txt"


def test_subcommand_options_use_same_resolver(offline_client, user_payload):
    frame = _frame(
        user_payload,
        [{"name": "detail", "type": 1, "options": [
            {"name": "target", "type": 9, "value": user_payload["id"]},
            {"name": "file", "type": 11, "value": "123"},
        ]}],
        {"users": {user_payload["id"]: user_payload},
         "attachments": {"123": _attachment_data()}},
    )
    options = interaction.ApplicationContext(frame, offline_client).options["subcommand"].options

    assert isinstance(options["target"], discord.User)
    assert isinstance(options["file"], discord.Attachment)


def test_mentionable_role_uses_resolved_role():
    role = object()
    guild = SimpleNamespace(get_member=lambda _id: None, get_role=lambda _id: role)
    context = SimpleNamespace(
        _resolved={"roles": {"123": {"id": "123", "name": "admin"}}},
        guild=guild,
    )

    assert resolve_mentionable(context, "123") is role


def test_mentionable_role_falls_back_to_resolved_object_when_cache_misses():
    role = object()
    guild = SimpleNamespace(get_member=lambda _id: None, get_role=lambda _id: None)
    context = SimpleNamespace(
        _resolved={"roles": {"123": {"id": "123", "name": "admin"}}},
        guild=guild,
        target=lambda kind, target_id: role if (kind, target_id) == ("roles", "123") else None,
    )

    assert resolve_mentionable(context, "123") is role


def test_missing_resolved_entry_keeps_option_id(offline_client, user_payload):
    frame = _frame(
        user_payload,
        [{"name": "target", "type": 9, "value": "999"},
         {"name": "file", "type": 11, "value": "123"}],
        {},
    )
    options = interaction.ApplicationContext(frame, offline_client).options

    assert options == {"target": "999", "file": "123"}
