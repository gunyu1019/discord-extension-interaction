from typing import Any, TypeVar, Callable, Coroutine


T = TypeVar('T')
_Coroutine = Coroutine[Any, Any, T]
CoroutineFunction = Callable[..., _Coroutine[Any]]
