from typing import TYPE_CHECKING, Optional

from .enums import Locale

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
            locale: Locale,
            name: str,
            description: str = "No Description",
            choices: list[CommandOptionChoice] = None
    ):
        if choices is None:
            choices = []
        self.locale = locale
        self.name = name
        self.description = description
        self.choices = choices

        self._original_option: Optional["CommandOption"] = None

    @classmethod
    def option_transition(
            cls,
            original_option: "CommandOption",
            locale: Locale,
            localized_name: str = None,
            localized_description: str = None,
    ):
        if localized_name is None:
            localized_name = original_option.name
        if localized_description is None:
            localized_description = original_option.description
        new_cls = cls(locale, localized_name, localized_description, original_option.choices)
        new_cls._original_option = original_option

        return new_cls

    @property
    def localized_choice(self) -> list["CommandOptionChoice"]:
        return [x.translation_choose(self.locale) for x in self.choices]

    @property
    def autocomplete(self):
        return self._original_option.autocomplete

    @property
    def required(self):
        return self._original_option.required

    @property
    def type(self):
        return self._original_option.type

    @property
    def min_value(self):
        return self._original_option.min_value

    @property
    def max_value(self):
        return self._original_option.max_value

    @property
    def channel_type(self):
        return self._original_option.channel_type
