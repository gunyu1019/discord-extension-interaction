"""Plan Discord command changes without issuing REST requests."""

from dataclasses import dataclass
from enum import Enum

from discord.ext.interaction.command_comparison import (
    same_command_declaration,
)
from discord.ext.interaction.command_registry import (
    CommandKey,
    CommandRegistry,
)
from discord.ext.interaction.models.command_scope import CommandScope


class SyncOperation(Enum):
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"
    UNCHANGED = "unchanged"


@dataclass(frozen=True)
class SyncPlanItem:
    key: CommandKey
    operation: SyncOperation
    local: object | None = None
    remote: object | None = None


@dataclass(frozen=True)
class SyncPlan:
    scope: CommandScope
    items: tuple[SyncPlanItem, ...]

    def candidates(self, operation: SyncOperation) -> tuple[SyncPlanItem, ...]:
        return tuple(item for item in self.items if item.operation is operation)


def plan_sync(
    scope: CommandScope,
    local: CommandRegistry,
    remote: CommandRegistry,
) -> SyncPlan:
    """Compare complete declared payloads within exactly one scope."""
    local_commands = local.for_scope(scope)
    remote_commands = remote.for_scope(scope)
    items = []
    for key in sorted(
        local_commands.keys() | remote_commands.keys(),
        key=lambda candidate: (int(candidate.type), candidate.name),
    ):
        local_command = local_commands.get(key)
        remote_command = remote_commands.get(key)
        if local_command is None:
            operation = SyncOperation.DELETE
        elif remote_command is None:
            operation = SyncOperation.CREATE
        elif same_command_declaration(local_command, remote_command):
            operation = SyncOperation.UNCHANGED
        else:
            operation = SyncOperation.EDIT
        items.append(SyncPlanItem(key, operation, local_command, remote_command))
    return SyncPlan(scope, tuple(items))
