from typing import Any, TypeVar, Callable, Coroutine, Union


T = TypeVar('T')
_Coroutine = Coroutine[Any, Any, T]
CoroutineFunction = Callable[..., _Coroutine[Any]]

UserCheck = Callable[["ContextT"], Union[_Coroutine[bool], bool]]
