"""Discord Unfurled Media Item used by visual components."""

from copy import deepcopy
from typing import Any


class UnfurledMediaItem:
    """Media URL plus optional fields returned by Discord."""

    def __init__(self, url: str, *, response_fields: dict[str, Any] | None = None):
        if not isinstance(url, str) or not url:
            raise ValueError("Unfurled Media Item requires a URL")
        self.url = url
        self.response_fields = deepcopy(response_fields or {})

    def to_payload(self) -> dict[str, Any]:
        return {"url": self.url, **deepcopy(self.response_fields)}

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "UnfurledMediaItem":
        return cls(
            payload["url"],
            response_fields={key: value for key, value in payload.items() if key != "url"},
        )
