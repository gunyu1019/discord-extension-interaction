"""Discord User Select component."""

from discord.ext.interaction.models.auto_select import AutoSelect


class UserSelect(AutoSelect):
    TYPE = 5
    DEFAULT_TYPES = ("user",)
