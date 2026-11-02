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
from discord.ext import commands


def load_extension_consider_inheritance(name: str):
    try:
        return getattr(commands, name)
    except (ModuleNotFoundError, AttributeError):
        return getattr(discord, name)


class InvalidArgument(discord.DiscordException):
    """
    Occurs when the Argument value is incorrect.
    Typically, a single item and a variety of items are in the same declaration.
    """

    def __init__(self):
        super(InvalidArgument, self).__init__(
            "Single item and multiple item cannot be used for same function."
        )


class ExtensionFailed(load_extension_consider_inheritance("ExtensionFailed")):
    pass


class NoEntryPointError(load_extension_consider_inheritance("NoEntryPointError")):
    pass


class ExtensionNotFound(load_extension_consider_inheritance("ExtensionNotFound")):
    pass


class ExtensionAlreadyLoaded(
    load_extension_consider_inheritance("ExtensionAlreadyLoaded")
):
    pass


class AlreadyDeferred(Exception):
    """Occurs when a defer is called while a defer is already called."""

    pass


class CheckFailure(commands.CheckFailure):
    """Exception raised when the predicates in :attr:`.Command.checks` have failed.

    This inherits from :exc:`CommandError`
    """

    pass


class CommandRegistrationError(commands.CommandRegistrationError):
    """An exception raised when the command can't be added
    because the name is already taken by a different command.

    This inherits from :exc:`discord.ClientException`
    """

    pass


class CommandNotFound(commands.CommandNotFound):
    """Exception raised when a command is attempted to be invoked
    but no command under that name is found.

    This is not raised for invalid subcommands, rather just the
    initial main command that is attempted to be invoked.

    This inherits from :exc:`CommandError`.
    """

    pass
