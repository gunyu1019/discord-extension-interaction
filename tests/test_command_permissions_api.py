"""Command permissions use OAuth Bearer credentials and Discord payloads."""

import asyncio

import pytest

from discord.ext import interaction


class _Response:
    def __init__(self, payload):
        self.payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def raise_for_status(self):
        return None

    async def json(self):
        return self.payload


class _Session:
    def __init__(self):
        self.calls = []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        return _Response({
            "id": "3", "application_id": "1", "guild_id": "2",
            "permissions": [{"id": "4", "type": 1, "permission": False}],
        })


def test_permissions_edit_uses_bearer_token_and_typed_result():
    session = _Session()
    api = interaction.CommandPermissionsAPI(session, "oauth-token")
    result = asyncio.run(api.edit_command_permissions(
        1, 2, 3, [interaction.CommandPermission(
            4, interaction.CommandPermissionType.ROLE, False,
        )],
    ))
    method, url, options = session.calls[0]
    assert method == "PUT"
    assert url.endswith("/applications/1/guilds/2/commands/3/permissions")
    assert options["headers"] == {"Authorization": "Bearer oauth-token"}
    assert options["json"] == {"permissions": [{"id": "4", "type": 1, "permission": False}]}
    assert result.permissions[0].type is interaction.CommandPermissionType.ROLE


def test_permissions_api_rejects_bot_token_and_oversized_overwrites():
    with pytest.raises(ValueError, match="Bearer"):
        interaction.CommandPermissionsAPI(_Session(), "Bot secret")
    api = interaction.CommandPermissionsAPI(_Session(), "oauth-token")
    permission = interaction.CommandPermission(4, interaction.CommandPermissionType.USER, True)
    with pytest.raises(ValueError, match="100"):
        asyncio.run(api.edit_command_permissions(1, 2, 3, [permission] * 101))
