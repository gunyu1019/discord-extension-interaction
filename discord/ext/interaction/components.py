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


import discord
import inspect

from .commands import BaseCore
from abc import *
from typing import Union, Optional, List, Type, Dict, Any


class Components(metaclass=ABCMeta):
    TYPE: Optional[int] = None

    def __init__(self, components_type: int):
        self.type = components_type

    @abstractmethod
    def to_dict(self) -> dict:
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, payload: dict) -> dict:
        pass


class Options:
    def __init__(
        self,
        label: str,
        value: str,
        description: Optional[str] = None,
        emoji: Union[discord.PartialEmoji, dict] = None,
        default: bool = False,
    ):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

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
        description: Optional[str] = payload.get("description")
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
    TYPE = 1

    def __init__(self, components: list = None):
        super().__init__(components_type=1)

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


class Button(Components):
    TYPE = 2

    def __init__(
        self,
        style: int,
        label: str = None,
        emoji: Union[discord.PartialEmoji, str, dict] = None,
        custom_id: str = None,
        url: str = None,
        disabled: bool = None,
    ):
        super().__init__(components_type=2)

        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self) -> dict:
        base = {"type": 2, "style": self.style}

        if self.label is not None:
            base["label"] = self.label
        if self.emoji is not None and isinstance(self.emoji, discord.PartialEmoji):
            base["emoji"] = self.emoji.to_dict()
        elif self.emoji is not None and isinstance(self.emoji, str):
            base["emoji"] = {"name": self.emoji}
        elif self.emoji is not None:
            base["emoji"] = self.emoji

        if 0 < self.style < 5 and self.custom_id is not None:
            base["custom_id"] = self.custom_id
        if self.style == 5 and self.url is not None:
            base["url"] = self.url
        if self.disabled is not None:
            base["disabled"] = self.disabled

        return base

    @classmethod
    def from_dict(cls, payload: dict):
        style = payload["style"]
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


class Selection(Components):
    TYPE = 3

    def __init__(
        self,
        custom_id: str,
        options: List[Union[dict, Options]],
        disabled: bool = False,
        placeholder: str = None,
        min_values: int = None,
        max_values: int = None,
    ):
        super().__init__(components_type=3)

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
                option.to_dict() if isinstance(option, Options) else option
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

    @classmethod
    def from_dict(cls, payload: dict):
        custom_id = payload["custom_id"]
        options = [Options.from_dict(x) for x in payload.get("options", [])]
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
    TYPE = 4

    def __init__(
        self,
        custom_id: str,
        style: int,
        label: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        required: bool = False,
        value: Optional[str] = None,
        placeholder: Optional[str] = None,
    ):
        super().__init__(components_type=4)

        self.custom_id = custom_id
        self.style = style
        self.label = label
        self.placeholder = placeholder
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value

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
    payload: List[Dict[str, Any]]
) -> List[Union[ActionRow, Button, Selection, TextInput]]:
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
        self, func, custom_id, component_type: Type[Components] = None, checks=None
    ):
        self.custom_id = custom_id
        self.type = component_type
        self.func = func
        super().__init__(func=func, checks=checks)

    @property
    def type_id(self) -> Optional[int]:
        if isinstance(self.type, Components):
            return self.type.TYPE
        return


def detect_component(
    cls: classmethod = None,
    custom_id: str = None,
    component_type: Type[Components] = None,
    checks=None,
):
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
