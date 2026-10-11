"""Discord Role Select component."""

from discord.ext.interaction.models.auto_select import AutoSelect


class RoleSelect(AutoSelect):
    TYPE = 6
    DEFAULT_TYPES = ("role",)
