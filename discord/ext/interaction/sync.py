"""Register, compare, plan, and synchronize application commands."""

from dataclasses import dataclass
from enum import Enum

from discord.ext.interaction.enums import ApplicationCommandType
from discord.ext.interaction.command_scope import (
    CommandScope,
    GlobalScope,
    GuildScope,
)
from discord.ext.interaction.sync_command import SyncCommand

# Command Registry


@dataclass(frozen=True)
class CommandKey:
    scope: CommandScope
    type: ApplicationCommandType
    name: str

    @classmethod
    def from_command(cls, command) -> "CommandKey":
        return cls(command.scope, ApplicationCommandType(command.type), command.name)


class CommandRegistry:
    """Store commands without colliding across guilds or command types."""

    def __init__(self):
        self._commands: dict[CommandKey, object] = {}

    def add(self, command) -> CommandKey:
        key = CommandKey.from_command(command)
        if key in self._commands:
            raise ValueError(f"command already registered: {key}")
        self._commands[key] = command
        return key

    def upsert(self, command) -> CommandKey:
        key = CommandKey.from_command(command)
        self._commands[key] = command
        return key

    def get(
        self,
        scope: CommandScope,
        command_type: ApplicationCommandType,
        name: str,
        *,
        fallback_global: bool = False,
    ):
        result = self._commands.get(CommandKey(scope, command_type, name))
        if result is None and fallback_global and not isinstance(scope, GlobalScope):
            result = self._commands.get(CommandKey(GlobalScope(), command_type, name))
        return result

    def remove(self, command) -> None:
        del self._commands[CommandKey.from_command(command)]

    def for_scope(self, scope: CommandScope) -> dict[CommandKey, object]:
        return {
            key: value for key, value in self._commands.items() if key.scope == scope
        }

    def replace_scope(self, scope: CommandScope, commands) -> None:
        """Refresh one remote scope without discarding other guild caches."""
        replacement = {
            key: value for key, value in self._commands.items() if key.scope != scope
        }
        for command in commands:
            if command.scope != scope:
                raise ValueError("remote command scope does not match requested scope")
            key = CommandKey.from_command(command)
            if key in replacement:
                raise ValueError(f"duplicate remote command: {key}")
            replacement[key] = command
        self._commands = replacement

    def all(self) -> list[object]:
        return list(self._commands.values())


# Sync Policy Store


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


# Command Comparison


def same_command_declaration(local, remote) -> bool:
    """Ignore Discord-assigned ID/version while keeping scope and payload fields."""
    return (str(local.guild_id) if local.guild_id is not None else None) == (
        str(remote.guild_id) if remote.guild_id is not None else None
    ) and local.to_register_dict() == remote.to_register_dict()


# Sync Planner


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


# Sync Executor


class SyncOutcome(Enum):
    APPLIED = "applied"
    SKIPPED = "skipped"
    UNCHANGED = "unchanged"
    FAILED = "failed"


@dataclass(frozen=True)
class SyncItemResult:
    item: SyncPlanItem
    outcome: SyncOutcome
    response: object | None = None
    error: Exception | None = None


@dataclass(frozen=True)
class SyncResult:
    plan: SyncPlan
    items: tuple[SyncItemResult, ...]

    @property
    def failures(self) -> tuple[SyncItemResult, ...]:
        return tuple(item for item in self.items if item.outcome is SyncOutcome.FAILED)


async def apply_sync_plan(
    plan: SyncPlan,
    policy: SyncCommand,
    transport,
) -> SyncResult:
    """Continue after individual API failures and report each attempted action."""
    results = []
    for item in plan.items:
        operation = item.operation
        if operation is SyncOperation.UNCHANGED:
            results.append(SyncItemResult(item, SyncOutcome.UNCHANGED))
            continue
        if not getattr(policy, operation.value):
            results.append(SyncItemResult(item, SyncOutcome.SKIPPED))
            continue
        try:
            if operation is SyncOperation.CREATE:
                response = await transport.create(plan.scope, item.local)
            elif operation is SyncOperation.EDIT:
                response = await transport.edit(plan.scope, item.local, item.remote)
            else:
                response = await transport.delete(plan.scope, item.remote)
        except Exception as error:
            results.append(SyncItemResult(item, SyncOutcome.FAILED, error=error))
        else:
            results.append(SyncItemResult(item, SyncOutcome.APPLIED, response=response))
    return SyncResult(plan, tuple(results))
