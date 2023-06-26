from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .commands import CommandOption, CommandOptionChoice


class LocalizedCommand:
    def __init__(
            self,
            name,
            description,
            option
    ):
        pass


class LocalizedOption:
    def __init__(
            self,
            original_option: "CommandOption",
            name: str,
            choice: list[CommandOptionChoice]
    ):
        pass
