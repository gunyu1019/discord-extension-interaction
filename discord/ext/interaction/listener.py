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
