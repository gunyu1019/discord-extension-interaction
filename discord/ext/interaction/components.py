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

from discord.ext.interaction.core import BaseCore
from discord.ext.interaction.legacy_components import (
    Components,
    ActionRow,
    Label,
    Button,
    SelectOption,
    Selection,
    TextInput,
    from_payload,
)
from discord.ext.interaction.component_models import Component


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
