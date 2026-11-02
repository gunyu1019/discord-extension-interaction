"""Discord REST operations for commands, permissions, and interactions."""

from __future__ import annotations

from collections.abc import Sequence
from typing import NamedTuple, TYPE_CHECKING

from discord.http import Route

from discord.ext.interaction.command_scope import GlobalScope, GuildScope
from discord.ext.interaction.command_permissions import (
    CommandPermission,
    GuildCommandPermissions,
)

# Command Api


async def get_global_commands_with_localizations(http, application_id: int):
    """Fetch every global command with complete localization dictionaries."""
    route = Route(
        "GET",
        "/applications/{application_id}/commands",
        application_id=application_id,
    )
    return await http.request(route, params={"with_localizations": "true"})


async def get_guild_commands_with_localizations(
    http, application_id: int, guild_id: int
):
    """Fetch a guild's commands with full localization dictionaries."""
    route = Route(
        "GET",
        "/applications/{application_id}/guilds/{guild_id}/commands",
        application_id=application_id,
        guild_id=guild_id,
    )
    return await http.request(route, params={"with_localizations": "true"})


async def get_guild_command(http, application_id: int, guild_id: int, command_id: int):
    """Fetch one guild command through discord.py's HTTP client."""
    return await http.get_guild_command(application_id, guild_id, command_id)


async def create_guild_command(http, application_id: int, guild_id: int, payload: dict):
    """Create a guild command using Discord's name upsert endpoint."""
    return await http.upsert_guild_command(application_id, guild_id, payload)


async def edit_guild_command(
    http, application_id: int, guild_id: int, command_id: int, payload: dict
):
    """Edit a guild command by its Discord ID."""
    return await http.edit_guild_command(application_id, guild_id, command_id, payload)


async def delete_guild_command(
    http, application_id: int, guild_id: int, command_id: int
):
    """Delete a guild command by its Discord ID."""
    return await http.delete_guild_command(application_id, guild_id, command_id)


# Command Sync Api


class CommandSyncAPI:
    """Apply one command operation using the matching Discord scope endpoint."""

    def __init__(self, http, application_id: int):
        self.http = http
        self.application_id = application_id

    async def create(self, scope, command):
        payload = command.to_register_dict()
        if isinstance(scope, GlobalScope):
            return await self.http.upsert_global_command(self.application_id, payload)
        if isinstance(scope, GuildScope):
            return await create_guild_command(
                self.http,
                self.application_id,
                scope.guild_id,
                payload,
            )
        raise TypeError("unsupported command scope")

    async def edit(self, scope, command, remote):
        payload = command.to_register_dict()
        command_id = int(remote.id)
        if isinstance(scope, GlobalScope):
            return await self.http.edit_global_command(
                self.application_id,
                command_id,
                payload,
            )
        if isinstance(scope, GuildScope):
            return await edit_guild_command(
                self.http,
                self.application_id,
                scope.guild_id,
                command_id,
                payload,
            )
        raise TypeError("unsupported command scope")

    async def delete(self, scope, remote):
        command_id = int(remote.id)
        if isinstance(scope, GlobalScope):
            return await self.http.delete_global_command(
                self.application_id, command_id
            )
        if isinstance(scope, GuildScope):
            return await delete_guild_command(
                self.http,
                self.application_id,
                scope.guild_id,
                command_id,
            )
        raise TypeError("unsupported command scope")


# Command Permissions Api


class CommandPermissionsAPI:
    """Use a user-authorized OAuth token, separate from the bot HTTP client."""

    def __init__(
        self,
        session,
        bearer_token: str,
        *,
        base_url: str = "https://discord.com/api/v10",
    ):
        if (
            not isinstance(bearer_token, str)
            or not bearer_token
            or bearer_token.startswith(("Bot ", "Bearer "))
        ):
            raise ValueError("a raw OAuth Bearer token is required")
        self.session = session
        self.bearer_token = bearer_token
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _snowflake(value: int) -> int:
        if type(value) is not int or value <= 0:
            raise ValueError("IDs must be positive snowflakes")
        return value

    def _path(
        self, application_id: int, guild_id: int, command_id: int | None = None
    ) -> str:
        application_id = self._snowflake(application_id)
        guild_id = self._snowflake(guild_id)
        path = f"/applications/{application_id}/guilds/{guild_id}/commands"
        if command_id is not None:
            path += f"/{self._snowflake(command_id)}/permissions"
        else:
            path += "/permissions"
        return self.base_url + path

    async def _request(self, method: str, url: str, *, payload: dict | None = None):
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        async with self.session.request(
            method, url, headers=headers, json=payload
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_guild_permissions(
        self,
        application_id: int,
        guild_id: int,
    ) -> list[GuildCommandPermissions]:
        data = await self._request("GET", self._path(application_id, guild_id))
        return [GuildCommandPermissions.from_payload(item) for item in data]

    async def get_command_permissions(
        self,
        application_id: int,
        guild_id: int,
        command_id: int,
    ) -> GuildCommandPermissions:
        data = await self._request(
            "GET", self._path(application_id, guild_id, command_id)
        )
        return GuildCommandPermissions.from_payload(data)

    async def edit_command_permissions(
        self,
        application_id: int,
        guild_id: int,
        command_id: int,
        permissions: Sequence[CommandPermission],
    ) -> GuildCommandPermissions:
        if len(permissions) > 100 or not all(
            isinstance(item, CommandPermission) for item in permissions
        ):
            raise ValueError("at most 100 CommandPermission entries are allowed")
        data = await self._request(
            "PUT",
            self._path(application_id, guild_id, command_id),
            payload={"permissions": [item.to_payload() for item in permissions]},
        )
        return GuildCommandPermissions.from_payload(data)


# Interaction Api

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Dict, Optional, Union

    from discord.file import File
    from discord.http import HTTPClient


class InteractionData(NamedTuple):
    """Identifiers needed to send a response for one interaction.

    Attributes
    ----------
    id: int
        The interaction's ID. Used for the initial ``callback`` response.
    application_id: int
        The application's ID. Used as the webhook id for the original response and followups.
    token: str
        The interaction's continuation token.
    """

    id: int
    application_id: int
    token: str


class InteractionHTTPClient:
    """Sends interaction responses through :class:`discord.http.HTTPClient`.

    Only permanent Discord REST endpoints are used
    (``/interactions/{id}/{token}/callback`` and the interaction followup webhooks).
    Rate-limit handling, retries and error translation come from ``HTTPClient``.

    Route parameters are named ``webhook_id`` / ``webhook_token`` so that
    :attr:`discord.http.Route.major_parameters` buckets these requests correctly.
    """

    def __init__(self, http: HTTPClient):
        self.http = http

    # -- Initial response -------------------------------------------------
    async def post_initial_response(
        self, data: InteractionData, payload: Dict[str, Any]
    ):
        route = Route(
            "POST",
            "/interactions/{webhook_id}/{webhook_token}/callback",
            webhook_id=data.id,
            webhook_token=data.token,
        )
        return await self.http.request(route, json=payload)

    async def get_initial_response(self, data: InteractionData):
        route = Route(
            "GET",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        return await self.http.request(route)

    async def edit_initial_response(
        self,
        data: InteractionData,
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        # ``@original`` is part of the path, not a parameter: Route would
        # percent-encode the ``@`` to ``%40``.
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def delete_initial_response(self, data: InteractionData):
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/@original",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        return await self.http.request(route)

    # -- Followup -------------------------------------------------------
    async def post_followup(
        self,
        data: InteractionData,
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        route = Route(
            "POST",
            "/webhooks/{webhook_id}/{webhook_token}",
            webhook_id=data.application_id,
            webhook_token=data.token,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def edit_followup(
        self,
        data: InteractionData,
        message_id: Union[int, str],
        payload: Optional[Dict[str, Any]] = None,
        form: Optional[list[Dict[str, Any]]] = None,
        files: Optional[Sequence[File]] = None,
    ):
        route = Route(
            "PATCH",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=data.application_id,
            webhook_token=data.token,
            message_id=message_id,
        )
        if form:
            return await self.http.request(route, form=form, files=files)
        return await self.http.request(route, json=payload)

    async def delete_followup(self, data: InteractionData, message_id: Union[int, str]):
        route = Route(
            "DELETE",
            "/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}",
            webhook_id=data.application_id,
            webhook_token=data.token,
            message_id=message_id,
        )
        return await self.http.request(route)
