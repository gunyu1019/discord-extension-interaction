"""OAuth Bearer-only Discord application command permissions transport."""

from collections.abc import Sequence

from ..domain.command_permissions import CommandPermission, GuildCommandPermissions


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
