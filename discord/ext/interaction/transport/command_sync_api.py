"""Discord REST adapter for planned global and guild command changes."""

from ..domain.command_scope import GlobalScope, GuildScope
from .command_api import create_guild_command, edit_guild_command, delete_guild_command


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
                self.http, self.application_id, scope.guild_id, payload,
            )
        raise TypeError("unsupported command scope")

    async def edit(self, scope, command, remote):
        payload = command.to_register_dict()
        command_id = int(remote.id)
        if isinstance(scope, GlobalScope):
            return await self.http.edit_global_command(
                self.application_id, command_id, payload,
            )
        if isinstance(scope, GuildScope):
            return await edit_guild_command(
                self.http, self.application_id, scope.guild_id, command_id, payload,
            )
        raise TypeError("unsupported command scope")

    async def delete(self, scope, remote):
        command_id = int(remote.id)
        if isinstance(scope, GlobalScope):
            return await self.http.delete_global_command(self.application_id, command_id)
        if isinstance(scope, GuildScope):
            return await delete_guild_command(
                self.http, self.application_id, scope.guild_id, command_id,
            )
        raise TypeError("unsupported command scope")
