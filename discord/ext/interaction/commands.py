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


import asyncio
from typing import List


class Command:
    def __init__(self, func, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')

        self.name = name = kwargs.get('name') or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')
        self.description = kwargs.get("description")

        self.callback = func
        self.aliases: list = kwargs.get('aliases', [])
        self.option_name: list = kwargs.get("option_name", [])
        self.options: list = kwargs.get("options", [])

        self.interaction: bool = kwargs.get('interaction', True)
        self.message: bool = kwargs.get('message', True)

        self.parents = None


def command(
        name: str = None,
        cls: classmethod = None,
        aliases: List[str] = None,
        options: List[str] = None,
        interaction: bool = True,
        message: bool = True
):
    if aliases is None:
        aliases = []

    if cls is None:
        cls = Command

    def decorator(func):
        return cls(
            func,
            name=name,
            aliases=aliases,
            interaction=interaction,
            message=message,
            options=options
        )

    return decorator
