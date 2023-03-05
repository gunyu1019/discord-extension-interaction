from typing import Any, TypeVar, Callable
from collections.abc import Coroutine


T = TypeVar('T')
_Coroutine = Coroutine[Any, Any, T]
CoroutineFunction = Callable[..., _Coroutine[Any]]

UserCheck = Callable[["ContextT"], _Coroutine[bool] | bool]
