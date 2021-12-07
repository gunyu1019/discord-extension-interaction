import functools
import inspect
import discord.utils
from typing import Union, Callable

from discord.ext.commands.errors import *
from .commands import BaseCommand


def check(predicate):
    def decorator(func):
        if isinstance(func, BaseCommand):
            func.checks.append(predicate)
        else:
            if not hasattr(func, '__commands_checks__'):
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


def checks(*predicate, exception: bool = False):
    unwrapped = []
    for wrapped in predicate:
        try:
            pred = wrapped.predicate
        except AttributeError:
            raise TypeError(f'{wrapped!r} must be wrapped by commands.check decorator') from None
        else:
            unwrapped.append(pred)

    async def predicate(ctx) -> bool:
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
        if exception:
            raise CheckAnyFailure(unwrapped, errors)
        return False

    return check(predicate)


def has_role(item: Union[int, str], exception: bool = False) -> Callable:
    def predicate(ctx) -> bool:
        if ctx.guild is None:
            if exception:
                raise NoPrivateMessage()
            return False

        # ctx.guild is None doesn't narrow ctx.author to Member
        if isinstance(item, int):
            role = discord.utils.get(ctx.author.roles, id=item)  # type: ignore
        else:
            role = discord.utils.get(ctx.author.roles, name=item)  # type: ignore

        if role is None:
            if exception:
                raise MissingRole(item)
            return False
        return True

    return check(predicate)


def has_roles(*items: Union[int, str], exception: bool = False) -> Callable:
    def predicate(ctx) -> bool:
        if ctx.guild is None:
            if exception:
                raise NoPrivateMessage()
            return False

        getter = functools.partial(discord.utils.get, ctx.author.roles)  # type: ignore
        if any(
                getter(id=item) is not None
                if isinstance(item, int)
                else getter(name=item) is not None
                for item in items
        ):
            return True
        if exception:
            raise MissingAnyRole(list(items))
        return False

    return check(predicate)
