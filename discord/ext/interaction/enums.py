from enum import Enum
from typing import Any


class ApplicationCommandType(Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

    def __eq__(self, other):
        if isinstance(other, ApplicationCommandType):
            return self._value_ == other.value
        return self._value_ == other

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self) -> Any:
        return super(ApplicationCommandType, self).value
