"""Placement rules for Discord message and modal component trees."""


def validate_message_action_row(row) -> None:
    """Require up to five buttons or exactly one select in a message row."""
    children = row.components
    if not children or len(children) > 5:
        raise ValueError("message ActionRow requires 1 to 5 components")
    types = [getattr(child, "TYPE", None) for child in children]
    if all(component_type == 2 for component_type in types):
        return
    if len(types) == 1 and types[0] in (3, 5, 6, 7, 8):
        return
    raise ValueError("message ActionRow requires buttons or one select menu")
