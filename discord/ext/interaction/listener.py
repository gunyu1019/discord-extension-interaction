import inspect


class Listener:
    def __init__(self, name):
        self.name = self.__name__ = name
        self.callback = None
        self.parents = None

    async def __call__(self, *args, **kwargs):
        if self.parents is not None:
            return await self.callback(self.parents, *args, **kwargs)
        return await self.callback(*args, **kwargs)


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
        new_cls.callback = _function
        return new_cls
    return decorator
