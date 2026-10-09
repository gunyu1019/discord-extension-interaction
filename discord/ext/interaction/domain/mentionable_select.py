"""Discord Mentionable Select component."""

from .auto_select import AutoSelect


class MentionableSelect(AutoSelect):
    TYPE = 7
    DEFAULT_TYPES = ("user", "role")
