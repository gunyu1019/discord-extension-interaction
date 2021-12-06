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

from typing import Union, Optional, List


class Components:
    def __init__(self, components_type: int):
        self.type = components_type


class Options:
    def __init__(
            self,
            label: str,
            value: str,
            description: Optional[str] = None,
            emoji: Union[discord.PartialEmoji, dict] = None,
            default: bool = False
    ):
        self.label = label
        self.value = value
        self.description = description
        self.emoji = emoji
        self.default = default

    def to_dict(self) -> dict:
        data = {
            "label": self.label,
            "value": self.value
        }

        if self.description is not None:
            data["description"] = self.description
        if self.emoji is not None:
            data["emoji"] = self.emoji.to_dict() if isinstance(self.emoji, discord.PartialEmoji) else self.emoji
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
            default=default
        )


class ActionRow(Components):
    def __init__(self, components: list = None):
        super().__init__(components_type=1)

        self.components: list = components

    def to_dict(self) -> dict:
        return {
            "type": 1,
            "components": self.components
        }

    def to_all_dict(self) -> dict:
        return {
            "type": 1,
            "components": [i.to_dict() for i in self.components]
        }

    @classmethod
    def from_dict(cls, payload: dict):
        components = payload.get("components")
        return cls(components=components)

    @classmethod
    def from_payload(cls, payload: dict):
        components = from_payload(
            payload.get("components")
        )
        return cls(components=components)


class Button(Components):
    def __init__(self,
                 style: int,
                 label: str = None,
                 emoji: Union[discord.PartialEmoji, str, dict] = None,
                 custom_id: str = None,
                 url: str = None,
                 disabled: bool = None):
        super().__init__(components_type=2)

        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def to_dict(self) -> dict:
        base = {
            "type": 2,
            "style": self.style
        }

        if self.label is not None:
            base["label"] = self.label
        if self.emoji is not None and isinstance(self.emoji, discord.PartialEmoji):
            base["emoji"] = self.emoji.to_dict()
        elif self.emoji is not None and isinstance(self.emoji, str):
            base["emoji"] = {
                "name": self.emoji
            }
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
            disabled=disabled
        )


class Selection(Components):
    def __init__(self,
                 custom_id: str,
                 options: List[Union[dict, Options]],
                 disabled: bool = False,
                 placeholder: str = None,
                 min_values: int = None,
                 max_values: int = None):
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
                option.to_dict()
                if isinstance(option, Options)
                else option
                for option in self.options
            ]
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
        options = [
            Options.from_dict(payload.get("options", []))
        ]
        placeholder = payload.get("placeholder")
        min_values = payload.get("min_values")
        max_values = payload.get("max_values")
        return cls(
            custom_id=custom_id,
            options=options,
            placeholder=placeholder,
            min_values=min_values,
            max_values=max_values
        )


def from_payload(payload: dict) -> list:
    components = []

    for i in payload:
        if i.get("type") == 1:
            components.append(ActionRow.from_payload(i))
        elif i.get("type") == 2:
            components.append(Button.from_dict(i))
        elif i.get("type") == 3:
            components.append(Selection.from_dict(i))
    return components


# For Decorator
class DetectComponent:
    def __init__(self, custom_id, component_type: Components = None):
        self.custom_id = custom_id
        self.type = component_type
        self.callback = None

    @classmethod
    def detect_component(
            cls,
            custom_id: str = None,
            component_type: Components = None
    ):
        def decorator(func):
            _function = func
            if isinstance(func, staticmethod):
                _function = func.__func__

            if not inspect.iscoroutinefunction(_function):
                raise TypeError('Detect Component function must be a coroutine function.')

            new_cls = cls(custom_id=custom_id or _function.__name__)
            new_cls.callback = _function
            return new_cls
        return decorator
