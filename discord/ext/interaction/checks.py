import functools
import inspect
from typing import Union, Callable

from discord.ext.commands.errors import NoPrivateMessage
from .commands import Command, MessageApplicationCommand
from .message import MessageCommand
from .interaction import ApplicationContext


def check(predicate):
    def decorator(func: Union[
        MessageApplicationCommand,
        Command,
        Callable
    ]) -> Union[
        MessageApplicationCommand,
        Command,
        Callable
    ]:
        if isinstance(func, Command) or isinstance(func, MessageApplicationCommand):
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


def has_role(item: Union[int, str]) -> Callable:
    def predicate(ctx: Union[ApplicationContext, MessageCommand]) -> bool:
        if ctx.guild is None:
            raise NoPrivateMessage()

        # ctx.guild is None doesn't narrow ctx.author to Member
        if isinstance(item, int):
            role = discord.utils.get(ctx.author.roles, id=item)  # type: ignore
        else:
            role = discord.utils.get(ctx.author.roles, name=item)  # type: ignore

        if role is None:
            return False
        return True

    return check(predicate)
