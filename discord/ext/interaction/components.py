"""MIT License

Copyright (c) 2021 gunyu1019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from abc import *
import inspect
from typing import Any
import discord

from .core import BaseCore
from .utils import get_enum


class Components(metaclass=ABCMeta):
    TYPE: int | None = None

    def __init__(self, components_type: discord.ComponentType):
        self.type = components_type

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, payload: dict) -> dict:
        pass

    def __eq__(self, other):
        return self.type == other.type

    def __ne__(self, other):
        return not self.__eq__(other)


class SelectOption:
    """Represents a select menu’s option.

    Attributes
    ----------
    label : str
        The label of option. This is visible to the user; max 100 characters.
    value : str
        The value of option. This is not visible to the user; max 100 characters.
    description : Optional[str]
        Additional description of the option; max 100 characters
    emoji : Optional[discord.PartialEmoji]
        The emoji of the option, if available.
        If ``emoji`` attributes is used as a dict, key requires an id, name, and animation.
    default : Optional[bool]
        Will show this option as selected by default
    """

    def __init__(
        self,
        label: str,
        value: str,
        description: str | None = None,
        emoji: discord.PartialEmoji | dict = None,
        default: bool = False,
    ):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def __str__(self) -> str:
        if self.emoji:
            base = f"{self.emoji} {self.label}"
        else:
            base = self.label

        if self.description:
            return f"{base}\n{self.description}"
        return base

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self) -> dict:
        data = {"label": self.label, "value": self.value}

        if self.description is not None:
            data["description"] = self.description
        if self.emoji is not None:
            data["emoji"] = (
                self.emoji.to_dict()
                if isinstance(self.emoji, discord.PartialEmoji)
                else self.emoji
            )
        if self.default is not None:
            data["default"] = self.default

        return data

    @classmethod
    def from_dict(cls, payload: dict):
        label: str = payload.get("label")
        value: str = payload.get("value")
        description: str | None = payload.get("description")
        emoji: discord.PartialEmoji = payload.get("emoji")
        default: bool = payload.get("default", False)
        return cls(
            label=label,
            value=value,
            description=description,
            emoji=emoji,
            default=default,
        )


class ActionRow(Components):
    """Represents an Action Row.

    An Action Row is a non-interactive container component for other types of components.
    This can contain up to five other Components.
    And, It cannot contain an Action Row.

    Attributes
    ----------
    components : list[Components]
        Contains up to five Components.
    """

    TYPE = 1

    def __init__(self, components: list[Components] = None):
        super().__init__(components_type=discord.ComponentType.action_row)

        self.components: list = components

    def to_dict(self) -> dict:
        return {"type": 1, "components": self.components}

    def to_all_dict(self) -> dict:
        return {"type": 1, "components": [i.to_dict() for i in self.components]}

    @classmethod
    def from_dict(cls, payload: dict):
        components = payload.get("components")
        return cls(components=components)

    @classmethod
    def from_payload(cls, payload: dict):
        components = from_payload(payload.get("components"))
        return cls(components=components)

    def __eq__(self, other):
        return self.components == other.components and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class Button(Components):
    """Represents a Button.

    Attributes
    ----------
    style : Union[:class:`discord.ButtonStyle`, int]
        The style of the button.
    label : Optional[str]
        The label of the button.
    emoji : Optional[Union[:class:`discord.PartialEmoji`, str, dict]]
        The emoji of the button, if available.
        If ``emoji`` attributes is used as a dict, key requires an id, name, and animation.
    custom_id: Optional[str]
        The custom_id of button. This is not visible to the user; max 100 characters.
    url: Optional[str]
        The URl of button for link-style(5).
    disabled: Optional[bool]
        Whether the button is disabled. This default is ``false``
    """

    TYPE = 2

    def __init__(
        self,
        style: int | discord.ButtonStyle,
        label: str = None,
        emoji: discord.PartialEmoji | str | dict = None,
        custom_id: str = None,
        url: str = None,
        disabled: bool = None,
    ):
        super().__init__(components_type=discord.ComponentType.button)

        # Accepting a button's style as an int will be disabled.
        if isinstance(style, int):
            style = get_enum(discord.ButtonStyle, style)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self) -> dict:
        base = {"type": 2, "style": int(self.style)}

        if self.label is not None:
            base["label"] = self.label
        if self.emoji is not None and isinstance(self.emoji, discord.PartialEmoji):
            base["emoji"] = self.emoji.to_dict()
        elif self.emoji is not None and isinstance(self.emoji, str):
            base["emoji"] = {"name": self.emoji}
        elif self.emoji is not None:
            base["emoji"] = self.emoji

        if 0 < int(self.style) < 5 and self.custom_id is not None:
            base["custom_id"] = self.custom_id
        if int(self.style) == 5 and self.url is not None:
            base["url"] = self.url

        if self.disabled is not None:
            base["disabled"] = self.disabled

        return base

    @classmethod
    def from_dict(cls, payload: dict):
        style = get_enum(discord.ButtonStyle, payload["style"])
        label = payload.get("label")
        emoji = payload.get("emoji")
        custom_id = payload.get("custom_id")
        url = payload.get("url")
        disabled = payload.get("disabled", False)
        return cls(
            style=style,
            label=label,
            emoji=emoji,
            custom_id=custom_id,
            url=url,
            disabled=disabled,
        )

    def __eq__(self, other):
        return self.custom_id == other.custom_id and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class Selection(Components):
    """Represents a Select Menu.

    Attributes
    ----------
    custom_id: str
        The custom_id of select menu. This is not visible to the user; max 100 characters.
    options : list[:class:`.Option`]
        The options of the select menu.
    disabled: Optional[bool]
        Whether the select menu is disabled. This default is ``false``
    placeholder : Optional[str]
        The placeholder of the select menu.
    min_values : Optional[int]
        Minimum number of items that can be chosen (defaults to 1); min 0, max 25
    max_values: Optional[int]
        Maximum number of items that can be chosen (defaults to 1); max 25
    """

    TYPE = 3

    def __init__(
        self,
        custom_id: str,
        options: list[dict | SelectOption],
        disabled: bool = False,
        placeholder: str = None,
        min_values: int = None,
        max_values: int = None,
    ):
        super().__init__(components_type=discord.ComponentType.select)

        self.disabled = disabled
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values

    def to_dict(self) -> dict:
        base = {
            "type": 3,
            "custom_id": self.custom_id,
            "disabled": self.disabled,
            "options": [
                option.to_dict() if isinstance(option, SelectOption) else option
                for option in self.options
            ],
        }
        if self.placeholder is not None:
            base["placeholder"] = self.placeholder
        if self.min_values is not None:
            base["min_values"] = self.min_values
        if self.max_values is not None:
            base["max_values"] = self.max_values

        return base

    def __eq__(self, other):
        return (
            self.custom_id == other.custom_id
            and super().__eq__(other)
            and self.options == other.options
        )

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def from_dict(cls, payload: dict):
        custom_id = payload["custom_id"]
        options = [SelectOption.from_dict(x) for x in payload.get("options", [])]
        placeholder = payload.get("placeholder")
        min_values = payload.get("min_values")
        max_values = payload.get("max_values")
        return cls(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
        )


class TextInput(Components):
    """Represents a TextInput.

    Notes
    -----
    Text inputs are an interactive component that render on modals.

    Attributes
    ----------
    custom_id: str
        The custom_id of text input. This is not visible to the user; max 100 characters.
    style : Union[:class:`discord.TextStyle`, int]
        The style of the text input.
    label: str
        The label of text input. This is visible to the user; max 45 characters
    placeholder : Optional[str]
        The placeholder of the text input.
    min_length : Optional[int]
        Minimum input length for a text input; min 0, max 4000
    max_length: Optional[int]
        Maximum input length for a text input; min 1, max 4000
    required: Optional[bool]
        Whether this input text is required to be filled (defaults to ``true``)
    value: Optional[str]
        Pre-filled value for this component; max 4000 characters
    """

    TYPE = 4

    def __init__(
        self,
        custom_id: str,
        style: int,
        label: str,
        min_length: int | None = None,
        max_length: int | None = None,
        required: bool = False,
        value: str | None = None,
        placeholder: str | None = None,
    ):
        super().__init__(components_type=discord.ComponentType.text_input)

        self.custom_id = custom_id
        self.style = style
        self.label = label
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value

    def __eq__(self, other):
        return self.custom_id == other.custom_id and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_dict(self) -> dict:
        base = {
            "type": 4,
            "custom_id": self.custom_id,
            "style": self.style,
            "label": self.label,
            "required": self.required,
        }
        if self.placeholder is not None:
            base["placeholder"] = self.placeholder
        if self.min_length is not None:
            base["min_length"] = self.min_length
        if self.max_length is not None:
            base["max_length"] = self.max_length
        if self.value is not None:
            base["value"] = self.value

        return base

    @classmethod
    def from_dict(cls, payload: dict):
        custom_id = payload["custom_id"]
        style = payload.get("style")
        label = payload.get("label")
        placeholder = payload.get("placeholder")
        min_length = payload.get("min_length")
        max_length = payload.get("max_length")
        required = payload.get("required", False)
        value = payload.get("value")
        return cls(
            custom_id=custom_id,
            style=style,
            label=label,
            placeholder=placeholder,
            min_length=min_length,
            max_length=max_length,
            required=required,
            value=value,
        )


def from_payload(
    payload: list[dict[str, Any]]
) -> list[ActionRow | Button | Selection | TextInput]:
    components = []

    for i in payload:
        if i.get("type") == 1:
            components.append(ActionRow.from_payload(i))
        elif i.get("type") == 2:
            components.append(Button.from_dict(i))
        elif i.get("type") == 3:
            components.append(Selection.from_dict(i))
        elif i.get("type") == 4:
            components.append(TextInput.from_dict(i))
    return components


# For Decorator
class DetectComponent(BaseCore):
    def __init__(
        self, func, custom_id, component_type: type[Components] = None, checks=None
    ):
        self.custom_id = custom_id
        self.type = component_type
        self.func = func
        super().__init__(func=func, checks=checks)

    @property
    def type_id(self) -> int | None:
        if isinstance(self.type, Components):
            return self.type.TYPE
        return


def detect_component(
    cls: classmethod = None,
    custom_id: str = None,
    component_type: type[Components] = None,
    checks=None,
):
    """A decorator that transforms a function into a :class:`.DetectComponent`

    Parameters
    ----------
    cls
        The class to construct with.
        You usually don't change ``cls``.
    custom_id: Optional[str]
        The custom id for detect component.
    component_type: Type[Components]
        The component_type for detect component.
    checks
    """
    if cls is None:
        cls = DetectComponent

    def decorator(func):
        _function = func
        if isinstance(func, staticmethod):
            _function = func.__func__

        if not inspect.iscoroutinefunction(_function):
            raise TypeError("Detect Component function must be a coroutine function.")

        new_cls = cls(
            func=_function,
            custom_id=custom_id or _function.__name__,
            component_type=component_type,
            checks=checks,
        )
        return new_cls

    return decorator
