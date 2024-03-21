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

import functools
import inspect
from typing import Callable

import discord.utils
from discord.ext.commands.errors import *

from .core import BaseCommand
from .interaction import InteractionContext


def check(predicate):
    def decorator(func):
        if isinstance(func, BaseCommand):
            func.checks.append(predicate)
        else:
            if not hasattr(func, "__commands_checks__"):
                func.__commands_checks__ = []

            func.__commands_checks__.append(predicate)

        return func

    if inspect.iscoroutinefunction(predicate):
        decorator.predicate = predicate
    else:

        @functools.wraps(predicate)
        async def wrapper(ctx):
            return predicate(ctx)  # type: ignore

        decorator.predicate = wrapper

    return decorator


def check_any(*checks) -> Callable:
    """A :func:`check` that is added that checks if any of the checks passed
    will pass, i.e. using logical OR.

    If all checks fail then :exc:`.CheckAnyFailure` is raised to signal the failure.
    It inherits from :exc:`.CheckFailure`.

    .. note::

        The ``predicate`` attribute for this function **is** a coroutine.

    Parameters
    ------------
    checks: Callable[[:class:`Context`], :class:`bool`]
        An argument list of checks that have been decorated with
        the :func:`check` decorator.

    Raises
    -------
    TypeError
        A check passed has not been decorated with the :func:`check`
        decorator.

    Examples
    ---------

    Creating a basic check to see if it's the bot owner or
    the server owner:

    .. code-block:: python3

        def is_guild_owner():
            def predicate(ctx):
                return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id
            return commands.check(predicate)

        @bot.command()
        @commands.check_any(commands.is_owner(), is_guild_owner())
        async def only_for_owners(ctx):
            await ctx.send('Hello mister owner!')
    """

    unwrapped = []
    for wrapped in checks:
        try:
            pred = wrapped.predicate
        except AttributeError:
            raise TypeError(
                f"{wrapped!r} must be wrapped by commands.check decorator"
            ) from None
        else:
            unwrapped.append(pred)

    async def predicate(ctx: InteractionContext) -> bool:
        errors = []
        for func in unwrapped:
            try:
                value = await func(ctx)
            except CheckFailure as e:
                errors.append(e)
            else:
                if value:
                    return True
        # if we're here, all checks failed
        raise CheckAnyFailure(unwrapped, errors)

    return check(predicate)


def has_role(item: int | str) -> Callable:
    """A :func:`.check` that is added that checks if the member invoking the
    command has the role specified via the name or ID specified.

    If a string is specified, you must give the exact name of the role, including
    caps and spelling.

    If an integer is specified, you must give the exact snowflake ID of the role.

    If the message is invoked in a private message context then the check will
    return ``False``.

    This check raises one of two special exceptions, :exc:`.MissingRole` if the user
    is missing a role, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.

    Parameters
    -----------
    item: Union[:class:`int`, :class:`str`]
        The name or ID of the role to check.
    """

    def predicate(ctx: InteractionContext) -> bool:
        if ctx.guild is None:
            raise NoPrivateMessage()

        # ctx.guild is None doesn't narrow ctx.author to Member
        if isinstance(item, int):
            role = discord.utils.get(ctx.author.roles, id=item)  # type: ignore
        else:
            role = discord.utils.get(ctx.author.roles, name=item)  # type: ignore
        if role is None:
            raise MissingRole(item)
        return True

    return check(predicate)


def has_any_role(*items: int | str) -> Callable:
    """A :func:`.check` that is added that checks if the member invoking the
    command has **any** of the roles specified. This means that if they have
    one out of the three roles specified, then this check will return `True`.

    Similar to :func:`.has_role`, the names or IDs passed in must be exact.

    This check raises one of two special exceptions, :exc:`.MissingAnyRole` if the user
    is missing all roles, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.

    Parameters
    -----------
    items: list[Union[:class:`str`, :class:`int`]]
        An argument list of names or IDs to check that the member has roles wise.

    Example
    --------

    .. code-block:: python3

        @bot.command()
        @commands.has_any_role('Library Devs', 'Moderators', 492212595072434186)
        async def cool(ctx):
            await ctx.send('You are cool indeed')
    """

    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        # ctx.guild is None doesn't narrow ctx.author to Member
        getter = functools.partial(discord.utils.get, ctx.author.roles)  # type: ignore
        if any(
            (
                getter(id=item) is not None
                if isinstance(item, int)
                else getter(name=item) is not None
            )
            for item in items
        ):
            return True
        raise MissingAnyRole(list(items))

    return check(predicate)


def bot_has_role(item: int) -> Callable:
    """Similar to :func:`.has_role` except checks if the bot itself has the
    role.

    This check raises one of two special exceptions, :exc:`.BotMissingRole` if the bot
    is missing the role, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.
    """

    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        me = ctx.me
        if isinstance(item, int):
            role = discord.utils.get(me.roles, id=item)
        else:
            role = discord.utils.get(me.roles, name=item)
        if role is None:
            raise BotMissingRole(item)
        return True

    return check(predicate)


def bot_has_any_role(*items: int) -> Callable:
    """Similar to :func:`.has_any_role` except checks if the bot itself has
    any of the roles listed.

    This check raises one of two special exceptions, :exc:`.BotMissingAnyRole` if the bot
    is missing all roles, or :exc:`.NoPrivateMessage` if it is used in a private message.
    Both inherit from :exc:`.CheckFailure`.
    """

    def predicate(ctx):
        if ctx.guild is None:
            raise NoPrivateMessage()

        me = ctx.me
        getter = functools.partial(discord.utils.get, me.roles)
        if any(
            (
                getter(id=item) is not None
                if isinstance(item, int)
                else getter(name=item) is not None
            )
            for item in items
        ):
            return True
        raise BotMissingAnyRole(list(items))

    return check(predicate)


def has_permissions(**perms: bool) -> Callable:
    """A :func:`.check` that is added that checks if the member has all of
    the permissions necessary.

    Note that this check operates on the current channel permissions, not the
    guild wide permissions.

    The permissions passed in must be exactly like the properties shown under
    :class:`.discord.Permissions`.

    This check raises a special exception, :exc:`.MissingPermissions`
    that is inherited from :exc:`.CheckFailure`.

    Parameters
    ------------
    perms
        An argument list of permissions to check for.

    Example
    ---------

    .. code-block:: python3

        @bot.command()
        @commands.has_permissions(manage_messages=True)
        async def test(ctx):
            await ctx.send('You can manage messages.')

    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: InteractionContext) -> bool:
        ch = ctx.channel
        permissions = ch.permissions_for(ctx.author)  # type: ignore

        missing = [
            perm for perm, value in perms.items() if getattr(permissions, perm) != value
        ]

        if not missing:
            return True

        raise MissingPermissions(missing)

    return check(predicate)


def bot_has_permissions(**perms: bool) -> Callable:
    """Similar to :func:`.has_permissions` except checks if the bot itself has
    the permissions listed.

    This check raises a special exception, :exc:`.BotMissingPermissions`
    that is inherited from :exc:`.CheckFailure`.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: InteractionContext) -> bool:
        guild = ctx.guild
        me = guild.me if guild is not None else ctx.client.user
        permissions = ctx.channel.permissions_for(me)  # type: ignore

        missing = [
            perm for perm, value in perms.items() if getattr(permissions, perm) != value
        ]

        if not missing:
            return True

        raise BotMissingPermissions(missing)

    return check(predicate)


def has_guild_permissions(**perms: bool) -> Callable:
    """Similar to :func:`.has_permissions`, but operates on guild wide
    permissions instead of the current channel permissions.

    If this check is called in a DM context, it will raise an
    exception, :exc:`.NoPrivateMessage`.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: InteractionContext) -> bool:
        if not ctx.guild:
            raise NoPrivateMessage

        permissions = ctx.author.guild_permissions  # type: ignore
        missing = [
            perm for perm, value in perms.items() if getattr(permissions, perm) != value
        ]

        if not missing:
            return True

        raise MissingPermissions(missing)

    return check(predicate)


def bot_has_guild_permissions(**perms: bool) -> Callable:
    """Similar to :func:`.has_guild_permissions`, but checks the bot
    members guild permissions.
    """

    invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if invalid:
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: InteractionContext) -> bool:
        if not ctx.guild:
            raise NoPrivateMessage

        permissions = ctx.me.guild_permissions  # type: ignore
        missing = [
            perm for perm, value in perms.items() if getattr(permissions, perm) != value
        ]

        if not missing:
            return True

        raise BotMissingPermissions(missing)

    return check(predicate)


def dm_only() -> Callable:
    """A :func:`.check` that indicates this command must only be used in a
    DM context. Only private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.PrivateMessageOnly`
    that is inherited from :exc:`.CheckFailure`.
    """

    def predicate(ctx: InteractionContext) -> bool:
        if ctx.guild is not None:
            raise PrivateMessageOnly()
        return True

    return check(predicate)


def guild_only() -> Callable:
    """A :func:`.check` that indicates this command must only be used in a
    guild context only. Basically, no private messages are allowed when
    using the command.

    This check raises a special exception, :exc:`.NoPrivateMessage`
    that is inherited from :exc:`.CheckFailure`.
    """

    def predicate(ctx: InteractionContext) -> bool:
        if ctx.guild is None:
            raise NoPrivateMessage()
        return True

    return check(predicate)


def is_owner() -> Callable:
    """A :func:`.check` that checks if the person invoking this command is the
    owner of the bot.

    This is powered by :meth:`.Bot.is_owner`.

    This check raises a special exception, :exc:`.NotOwner` that is derived
    from :exc:`.CheckFailure`.
    """

    async def predicate(ctx: InteractionContext) -> bool:
        if not await ctx.client.is_owner(ctx.author):
            raise NotOwner("You do not own this bot.")
        return True

    return check(predicate)


def is_nsfw() -> Callable:
    """A :func:`.check` that checks if the channel is a NSFW channel.

    This check raises a special exception, :exc:`.NSFWChannelRequired`
    that is derived from :exc:`.CheckFailure`.
    """

    def pred(ctx: InteractionContext) -> bool:
        ch = ctx.channel
        if ctx.guild is None or (
            isinstance(ch, (discord.TextChannel, getattr(discord, "Thread", None)))
            and ch.is_nsfw()
        ):
            return True
        raise NSFWChannelRequired(ch)  # type: ignore

    return check(pred)
