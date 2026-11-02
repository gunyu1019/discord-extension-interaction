"""Bind a PRIMARY_ENTRY_POINT declaration to an optional app callback."""

import inspect

from discord.ext.interaction.commands import (
    ActivityCommand,
    ActivityHandler,
)


class ActivityBinding:
    """Adapter exposing the existing command dispatch protocol."""

    def __init__(self, command: ActivityCommand, callback=None):
        if not isinstance(command, ActivityCommand):
            raise TypeError("command must be an ActivityCommand")
        if (
            command.handler is ActivityHandler.APP_HANDLER
            and not inspect.iscoroutinefunction(callback)
        ):
            raise TypeError("APP_HANDLER requires an async callback")
        self.command = command
        self._callback = callback
        self.cog = None

    def __getattr__(self, name):
        return getattr(self.command, name)

    async def can_run(self, context) -> bool:
        return True

    async def callback(self, context):
        if self._callback is not None:
            await self._callback(context)
