from enum import Enum
from typing import Any


class ApplicationCommandType(Enum):
    CHAT_INPUT = 1
    USER = 2
    MESSAGE = 3

    # def __eq__(self, other):
    #     if isinstance(other, ApplicationCommandType):
    #         return self._value_ == other.value
    #     return self._value_ == other

    # def __ne__(self, other):
    #     return not self.__eq__(other)

    @property
    def value(self) -> int:
        return super(ApplicationCommandType, self).value


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

    @property
    def value(self) -> str:
        return super(Locale, self).value

    @staticmethod
    def from_payload(original_data: dict[str, str]) -> dict["Locale", str]:
        result = dict()
        for local in Locale:
            if local.value not in original_data.keys():
                continue
            result[local] = original_data[local.value]
        return result
