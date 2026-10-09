"""Discord API localization dictionary conversion."""


def read_localizations(payload: dict, field: str) -> dict[str, str]:
    """Keep the full locale map when present, without retaining payload ownership."""
    return dict(payload.get(field) or {})


def add_localizations(
    payload: dict,
    name_localizations: dict[str, str],
    description_localizations: dict[str, str] | None = None,
) -> None:
    """Add only declared localization maps to a registration payload."""
    if name_localizations:
        payload["name_localizations"] = dict(name_localizations)
    if description_localizations:
        payload["description_localizations"] = dict(description_localizations)
