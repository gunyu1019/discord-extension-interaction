"""Discord PRIMARY_ENTRY_POINT application command."""

from enum import IntEnum

from discord.ext.interaction.models.commands import ApplicationCommand
from discord.ext.interaction.models.enums import ApplicationCommandType


class ActivityHandler(IntEnum):
    APP_HANDLER = 1
    DISCORD_LAUNCH_ACTIVITY = 2


class ActivityCommand(ApplicationCommand):
    """A global Activity entry point with an explicit handler strategy."""

    def __init__(
        self,
        name: str,
        description: str,
        *,
        handler: ActivityHandler | int = ActivityHandler.DISCORD_LAUNCH_ACTIVITY,
        **kwargs,
    ):
        if kwargs.get("guild_id") is not None:
            raise ValueError("PRIMARY_ENTRY_POINT cannot be a guild command")
        if not isinstance(name, str) or not 1 <= len(name) <= 32:
            raise ValueError("Activity command name requires 1 to 32 characters")
        if not isinstance(description, str) or not 1 <= len(description) <= 100:
            raise ValueError(
                "Activity command description requires 1 to 100 characters"
            )
        try:
            self.handler = ActivityHandler(handler)
        except ValueError as error:
            raise ValueError("invalid Activity command handler") from error
        super().__init__(
            name=name,
            description=description,
            command_type=ApplicationCommandType.PRIMARY_ENTRY_POINT,
            **kwargs,
        )

    def to_register_dict(self) -> dict:
        return {**super().to_register_dict(), "handler": int(self.handler)}

    @classmethod
    def from_payload(cls, data: dict) -> "ActivityCommand":
        result = super().from_payload(data)
        result.handler = ActivityHandler(data.get("handler", 2))
        return result
