"""Explicit Discord application command registration scopes."""

from dataclasses import dataclass


@dataclass(frozen=True)
class GlobalScope:
    """Application-wide command scope."""


@dataclass(frozen=True)
class GuildScope:
    """Scope for a single Discord guild."""

    guild_id: int

    def __post_init__(self):
        if type(self.guild_id) is not int or self.guild_id <= 0:
            raise ValueError("GuildScope guild_id must be a positive snowflake")


CommandScope = GlobalScope | GuildScope


def resolve_scope(
    scope: CommandScope | None, guild_id: int | str | None,
) -> CommandScope:
    """Keep legacy ``guild_id`` and the new ``scope`` declaration consistent."""
    if scope is not None and not isinstance(scope, (GlobalScope, GuildScope)):
        raise TypeError("scope must be GlobalScope or GuildScope")
    legacy = None if guild_id is None else GuildScope(int(guild_id))
    if scope is not None and legacy is not None and scope != legacy:
        raise ValueError("scope and guild_id refer to different command scopes")
    return scope or legacy or GlobalScope()
