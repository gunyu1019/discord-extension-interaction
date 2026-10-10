"""Identify application commands by Discord scope, type and name."""

from dataclasses import dataclass

from ..domain.command_scope import CommandScope, GlobalScope
from ..enums import ApplicationCommandType


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

    def get(
        self, scope: CommandScope, command_type: ApplicationCommandType,
        name: str, *, fallback_global: bool = False,
    ):
        result = self._commands.get(CommandKey(scope, command_type, name))
        if result is None and fallback_global and not isinstance(scope, GlobalScope):
            result = self._commands.get(CommandKey(GlobalScope(), command_type, name))
        return result

    def remove(self, command) -> None:
        del self._commands[CommandKey.from_command(command)]

    def for_scope(self, scope: CommandScope) -> dict[CommandKey, object]:
        return {key: value for key, value in self._commands.items() if key.scope == scope}

    def all(self) -> list[object]:
        return list(self._commands.values())
