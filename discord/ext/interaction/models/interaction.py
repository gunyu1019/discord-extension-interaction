"""Transport-neutral fields shared by all Discord interaction types."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


def _snowflake(value: str | int | None) -> int | None:
    return int(value) if value is not None else None


@dataclass(frozen=True)
class InteractionEnvelope:
    """A snapshot of the received Discord Interaction Object.

    ``data`` stays optional because PING has no interaction data. Unknown top-level
    fields and future interaction types remain available through ``raw_payload``.
    """

    id: int
    application_id: int
    type: int
    token: str
    version: int
    data: dict[str, Any] | None
    guild_id: int | None
    channel_id: int | None
    guild: dict[str, Any] | None
    channel: dict[str, Any] | None
    member: dict[str, Any] | None
    user: dict[str, Any] | None
    message: dict[str, Any] | None
    app_permissions: str | None
    locale: str | None
    guild_locale: str | None
    entitlements: tuple[dict[str, Any], ...]
    authorizing_integration_owners: dict[str, str]
    context: int | None
    attachment_size_limit: int | None
    raw_payload: dict[str, Any]

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "InteractionEnvelope":
        snapshot = deepcopy(payload)
        return cls(
            id=int(snapshot["id"]),
            application_id=int(snapshot["application_id"]),
            type=int(snapshot["type"]),
            token=snapshot["token"],
            version=int(snapshot["version"]),
            data=snapshot.get("data"),
            guild_id=_snowflake(snapshot.get("guild_id")),
            channel_id=_snowflake(snapshot.get("channel_id")),
            guild=snapshot.get("guild"),
            channel=snapshot.get("channel"),
            member=snapshot.get("member"),
            user=snapshot.get("user"),
            message=snapshot.get("message"),
            app_permissions=snapshot.get("app_permissions"),
            locale=snapshot.get("locale"),
            guild_locale=snapshot.get("guild_locale"),
            entitlements=tuple(snapshot.get("entitlements") or ()),
            authorizing_integration_owners=dict(
                snapshot.get("authorizing_integration_owners") or {}
            ),
            context=snapshot.get("context"),
            attachment_size_limit=snapshot.get("attachment_size_limit"),
            raw_payload=snapshot,
        )
