"""Discord User Select component."""

from .auto_select import AutoSelect


class UserSelect(AutoSelect):
    TYPE = 5
    DEFAULT_TYPES = ("user",)
