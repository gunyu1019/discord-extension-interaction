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
from typing import List, Optional


class OptionChoice:
    def __init__(
            self,
            name: str,
            value: str
    ):
        self.name = name
        self.value = value

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "value": self.value
        }


class Option:
    SUB_COMMAND = 1
    SUB_COMMAND_GROUP = 2
    STRING = 3
    INTEGER = 4
    BOOLEAN = 5
    USER = 6
    CHANNEL = 7
    ROLE = 8
    MENTIONABLE = 9
    NUMBER = 10

    def __init__(
            self,
            name: str,
            type: int,
            description: str = None,
            required: bool = False,
            choices: List[OptionChoice] = None,
            autocomplete: bool = False,
            options: list = None
    ):
        self.name = name
        self.type = type
        self.description = description
        self.required = required
        self.choices = choices
        self.autocomplete = autocomplete
        self.options = options

    def to_dict(self) -> dict:
        data = {
            "name": self.name,
            "type": self.type
        }
        return data


class ApplicationCommand:
    def __init__(
            self,
            name: str,
            description: str = None,
            options: List[Option] = None,
            **kwargs
    ):
        self.name = name
        self.description = description
        self.options = options

        self.id: Optional[int] = kwargs.pop("id")

    def to_dict(self) -> dict:
        data = {
            'name': self.name
        }
        if self.description is not None:
            data['description'] = self.description
        if self.options is not None:
            data['optins'] = [
                option.to_dict() if isinstance(option, Option)
                else option
                for option in self.options
            ]

        return data

    @classmethod
    def from_payload(cls, data: dict):
        name = data.pop("name")
        description = data.pop("description")
        if "options" in data:
            options = data.pop("options")
        else:
            options = None

        return cls(
            name=name,
            description=description,
            options=options,
            **data
        )


class Command(ApplicationCommand):
    def __init__(self, func, **kwargs):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError('Callback must be a coroutine.')
        if "options" in kwargs.keys() and "option_name" in kwargs.keys():
            raise TypeError('Add one of "option_name" and "options".')

        super().__init__(**kwargs)
        self.name = name = kwargs.get('name') or func.__name__
        if not isinstance(name, str):
            raise TypeError('Name of a command must be a string.')

        self.callback = func
        self.aliases: list = kwargs.get('aliases', [])

        self.option_name: List[str] = kwargs.get("option_name") or [
            option.name for option in kwargs.get("options", []) if isinstance(option, Option)
        ]

        self.sync_command: bool = kwargs.get("sync_command", None)
        self.interaction: bool = kwargs.get('interaction', True)
        self.message: bool = kwargs.get('message', True)

        self.parents = None


def command(
        name: str = None,
        description: str = None,
        cls: classmethod = None,
        aliases: List[str] = None,
        options: List[str] = None,
        interaction: bool = True,
        message: bool = True,
        sync_command: bool = None
):
    if aliases is None:
        aliases = []

    if cls is None:
        cls = Command

    def decorator(func):
        return cls(
            func,
            name=name,
            description=description,
            aliases=aliases,
            interaction=interaction,
            message=message,
            options=options,
            sync_command=sync_command
        )

    return decorator
