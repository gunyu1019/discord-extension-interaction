"""Per-scope in-memory command synchronization policies."""

from discord.ext.interaction.models.command_scope import (
    CommandScope,
    GlobalScope,
    GuildScope,
)
from discord.ext.interaction.models.sync_command import SyncCommand


class SyncPolicyStore:
    """Hold only explicitly configured policies for the current process."""

    def __init__(self):
        self._policies: dict[CommandScope, SyncCommand] = {}

    def set(self, scope: CommandScope, policy: SyncCommand) -> None:
        if not isinstance(scope, (GlobalScope, GuildScope)):
            raise TypeError("scope must be GlobalScope or GuildScope")
        if not isinstance(policy, SyncCommand):
            raise TypeError("policy must be SyncCommand")
        self._policies[scope] = policy

    def get(self, scope: CommandScope) -> SyncCommand | None:
        return self._policies.get(scope)

    def remove(self, scope: CommandScope) -> None:
        self._policies.pop(scope, None)

    def items(self) -> tuple[tuple[CommandScope, SyncCommand], ...]:
        return tuple(self._policies.items())
