"""Resolve selected menu IDs using an interaction's resolved payload."""

from discord.ext.interaction.resolved_objects import resolve_target


def resolve_select_values(context, component_type: int, values: list[str]) -> list:
    """Return Discord objects for auto-select menus and strings otherwise."""
    if component_type == 3:
        return list(values)
    result = []
    for value in values:
        if component_type == 5:
            resolved = resolve_target(context, "members", value) or resolve_target(
                context, "users", value
            )
        elif component_type == 6:
            resolved = resolve_target(context, "roles", value)
        elif component_type == 7:
            resolved = (
                resolve_target(context, "members", value)
                or resolve_target(context, "users", value)
                or resolve_target(context, "roles", value)
            )
        elif component_type == 8:
            resolved = resolve_target(context, "channels", value)
        else:
            resolved = None
        result.append(resolved if resolved is not None else value)
    return result
