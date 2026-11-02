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

from abc import ABCMeta, abstractmethod
from typing import Any

import discord
import inspect

from discord.ext.interaction.core import BaseCore
from discord.ext.interaction.enums import get_enum
from discord.ext.interaction.component_codec import parse_component_model
from discord.ext.interaction.component_models import Component, UnknownComponent

# Legacy Component Models


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
    """Represents a select menu's option."""

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


class Button(Components):
    """Represents a Button with style, label, emoji and an action target."""

    TYPE = 2

    def __init__(
        self,
        style: int | discord.ButtonStyle,
        label: str = None,
        emoji: discord.PartialEmoji | str | dict = None,
        custom_id: str = None,
        url: str = None,
        disabled: bool = None,
        sku_id: int | str = None,
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
        self.sku_id = sku_id
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
        if int(self.style) == 6 and self.sku_id is not None:
            base["sku_id"] = str(self.sku_id)

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
        sku_id = payload.get("sku_id")
        disabled = payload.get("disabled", False)
        return cls(
            style=style,
            label=label,
            emoji=emoji,
            custom_id=custom_id,
            url=url,
            sku_id=sku_id,
            disabled=disabled,
        )

    def __eq__(self, other):
        return self.custom_id == other.custom_id and super().__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)


class TextInput(Components):
    """Represents an interactive text input rendered on a modal."""

    TYPE = 4

    def __init__(
        self,
        custom_id: str,
        style: int,
        label: str | None = None,
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
            "required": self.required,
        }
        if self.label is not None:
            base["label"] = self.label
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


class Selection(Components):
    """Represents a Select Menu."""

    TYPE = 3

    def __init__(
        self,
        custom_id: str,
        options: list[dict | SelectOption],
        disabled: bool = False,
        placeholder: str = None,
        min_values: int = None,
        max_values: int = None,
        required: bool | None = None,
        values: list[str] | None = None,
    ):
        super().__init__(components_type=discord.ComponentType.select)

        self.disabled = disabled
        self.custom_id = custom_id
        self.options = options
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.required = required
        self.values = list(values) if values is not None else []

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
        if self.required is not None:
            base["required"] = self.required

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
        required = payload.get("required")
        values = payload.get("values")
        return cls(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values,
            required=required,
            values=values,
        )


class ActionRow(Components):
    """A non-interactive row containing existing component objects."""

    TYPE = 1

    def __init__(self, components: list[Components] = None):
        super().__init__(components_type=discord.ComponentType.action_row)
        self.components: list = components

    def to_dict(self) -> dict:
        return {"type": 1, "components": self.components}

    def to_all_dict(self) -> dict:
        return {
            "type": 1,
            "components": [
                i.to_dict() if isinstance(i, Components) else i.to_payload()
                for i in self.components
            ],
        }

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


class Label(Components):
    """A modal-only container around one interactive component."""

    TYPE = 18

    def __init__(
        self,
        component: Components,
        label: str | None = None,
        description: str | None = None,
    ):
        super().__init__(components_type=discord.ComponentType.label)
        self.label = label
        self.description = description
        self.component = component

    @property
    def components(self) -> list:
        """Expose the wrapped child with the ActionRow list shape."""
        return [self.component] if self.component is not None else []

    def to_dict(self) -> dict:
        base = {"type": 18, "component": self.component}
        if self.label is not None:
            base["label"] = self.label
        if self.description is not None:
            base["description"] = self.description
        return base

    def to_all_dict(self) -> dict:
        base = self.to_dict()
        child = (
            self.component.to_dict()
            if isinstance(self.component, Components)
            else self.component.to_payload()
        )
        # The Label carries the label/description; Discord rejects them on the child.
        child.pop("label", None)
        child.pop("description", None)
        child.pop("disabled", None)
        base["component"] = child
        return base

    @classmethod
    def from_dict(cls, payload: dict):
        return cls(
            component=payload.get("component"),
            label=payload.get("label"),
            description=payload.get("description"),
        )

    @classmethod
    def from_payload(cls, payload: dict):
        child = from_payload([payload["component"]]) if payload.get("component") else []
        return cls(
            component=child[0] if child else None,
            label=payload.get("label"),
            description=payload.get("description"),
        )

    def __eq__(self, other):
        return (
            self.component == other.component
            and self.label == other.label
            and super().__eq__(other)
        )

    def __ne__(self, other):
        return not self.__eq__(other)


def from_payload(
    payload: list[dict[str, Any]],
) -> list[ActionRow | Button | Selection | TextInput | Label | UnknownComponent]:
    components = []

    for item in payload:
        if item.get("type") == 1:
            components.append(ActionRow.from_payload(item))
        elif item.get("type") == 2:
            components.append(Button.from_dict(item))
        elif item.get("type") == 3:
            components.append(Selection.from_dict(item))
        elif item.get("type") == 4:
            components.append(TextInput.from_dict(item))
        elif item.get("type") == 18:
            components.append(Label.from_payload(item))
        elif item.get("type") in (
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            17,
            19,
            21,
            22,
            23,
        ):
            components.append(parse_component_model(item))
        else:
            components.append(UnknownComponent.from_payload(item))
    return components


# For Decorator
class DetectComponent(BaseCore):
    def __init__(
        self,
        func,
        custom_id,
        component_type: type[Components | Component] = None,
        checks=None,
    ):
        self.custom_id = custom_id
        self.type = component_type
        self.func = func
        super().__init__(func=func, checks=checks)

    @property
    def type_id(self) -> int | None:
        if isinstance(self.type, type) and issubclass(
            self.type, (Components, Component)
        ):
            return self.type.TYPE
        return None


def detect_component(
    cls: classmethod = None,
    custom_id: str = None,
    component_type: type[Components | Component] = None,
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
