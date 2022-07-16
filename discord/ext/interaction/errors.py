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
from typing import Optional, Any


class ExtensionInteractionError(discord.DiscordException):
    pass


class ClientException(ExtensionInteractionError):
    pass


class CommandError(ExtensionInteractionError):
    def __init__(self, message: Optional[str] = None, *args: Any) -> None:
        if message is not None:
            # clean-up @everyone and @here mentions
            m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
            super().__init__(m, *args)
        else:
            super().__init__(*args)


class ExtensionError(ExtensionInteractionError):
    def __init__(self, message: Optional[str] = None, *args: Any, name: str) -> None:
        self.name = name
        message = message or f'Extension {name!r} had an error.'
        m = message.replace('@everyone', '@\u200beveryone').replace('@here', '@\u200bhere')
        super().__init__(m, *args)


class ExtensionAlreadyLoaded(ExtensionError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Extension {name!r} is already loaded.', name=name)


class ExtensionNotLoaded(ExtensionError):
    def __init__(self, name: str) -> None:
        super().__init__(f'Extension {name!r} has not been loaded.', name=name)


class NoEntryPointError(ExtensionError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Extension {name!r} has no 'setup' function.", name=name)


class ExtensionFailed(ExtensionError):
    def __init__(self, name: str, original: Exception) -> None:
        self.original: Exception = original
        msg = f'Extension {name!r} raised an error: {original.__class__.__name__}: {original}'
        super().__init__(msg, name=name)


class ExtensionNotFound(ExtensionError):
    def __init__(self, name: str) -> None:
        msg = f'Extension {name!r} could not be loaded.'
        super().__init__(msg, name=name)


class CommandRegistrationError(ClientException):
    def __init__(self, name: str):
        self.name = name
        super(CommandRegistrationError, self).__init__(f'The {name} is already an existing application command.')


class CommandNotFound(CommandError):
    pass


class CheckFailure(CommandError):
    pass


class InvalidArgument(ExtensionInteractionError):
    """
        Occurs when the Argument value is incorrect.
        Typically, a single item and a variety of items are in the same declaration.
    """
    pass


class AlreadyDeferred(ExtensionInteractionError):
    """
        Occurs when a defer is called while a defer is already called.
    """
    pass
