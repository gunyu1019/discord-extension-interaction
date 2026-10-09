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

import inspect
from typing import Any
import discord

from .core import BaseCore
from .legacy_components.base import Components
from .legacy_components.action_row import ActionRow
from .legacy_components.label import Label
from .legacy_components.button import Button
from .legacy_components.select_option import SelectOption
from .legacy_components.selection import Selection
from .legacy_components.text_input import TextInput


def from_payload(
    payload: list[dict[str, Any]],
) -> list[ActionRow | Button | Selection | TextInput | Label]:
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
        elif i.get("type") == 18:
            components.append(Label.from_payload(i))
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
        if isinstance(self.type, type) and issubclass(self.type, Components):
            return self.type.TYPE
        return None


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
