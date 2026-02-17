from enum import Enum, IntEnum
from typing import Any


class ApplicationCommandType(IntEnum):
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
    def value(self) -> int:
        return super(ApplicationCommandType, self).value


class ApplicationIntegrationType(IntEnum):
    GUILD_INSTALL = 0
    USER_INSTALL = 1

    def __eq__(self, other):
        if isinstance(other, ApplicationIntegrationType):
            return self._value_ == other.value
        return self._value_ == other

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self) -> int:
        return super(ApplicationIntegrationType, self).value


class ApplicationContextType(IntEnum):
    GUILD = 0
    BOT_DM = 1
    PRIVATE_CHANNEL = 2

    def __eq__(self, other):
        if isinstance(other, ApplicationContextType):
            return self._value_ == other.value
        return self._value_ == other

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def value(self) -> int:
        return super(ApplicationContextType, self).value


class Locale(Enum):
    american_english = "en-US"
    british_english = "en-GB"
    bulgarian = "bg"
    chinese = "zh-CN"
    taiwan_chinese = "zh-TW"
    croatian = "hr"
    czech = "cs"
    indonesian = "id"
    danish = "da"
    dutch = "nl"
    finnish = "fi"
    french = "fr"
    german = "de"
    greek = "el"
    hindi = "hi"
    hungarian = "hu"
    italian = "it"
    japanese = "ja"
    korean = "ko"
    lithuanian = "lt"
    norwegian = "no"
    polish = "pl"
    brazil_portuguese = "pt-BR"
    romanian = "ro"
    russian = "ru"
    spain_spanish = "es-ES"
    swedish = "sv-SE"
    thai = "th"
    turkish = "tr"
    ukrainian = "uk"
    vietnamese = "vi"
