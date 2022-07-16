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
from typing import Coroutine, Any


class Listener:
    def __init__(self, name):
        self.name = self.__name__ = name
        self.func = None
        self.parents = None

    async def __call__(self, *args, **kwargs):
        return await self.callback(*args, **kwargs)

    async def callback(self, *args, **kwargs) -> Coroutine[Any, Any, Any]:
        if self.parents is None:
            return await self.func(*args, **kwargs)
        return await self.func(self.parents, *args, **kwargs)


def listener(cls=None, name: str = None):
    if cls is None:
        cls = Listener

    def decorator(func):
        _function = func
        if isinstance(func, staticmethod):
            _function = func.__func__

        if not inspect.iscoroutinefunction(_function):
            raise TypeError('Listener function must be a coroutine function.')

        new_cls = cls(name=name or _function.__name__)
        new_cls.func = _function
        return new_cls
    return decorator
