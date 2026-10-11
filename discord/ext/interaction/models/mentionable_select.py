"""Discord Mentionable Select component."""

from discord.ext.interaction.models.auto_select import AutoSelect


class MentionableSelect(AutoSelect):
    TYPE = 7
    DEFAULT_TYPES = ("user", "role")
