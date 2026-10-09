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


def validate_modal_container(container) -> None:
    """Check the child of a modal Label or legacy ActionRow."""
    component_type = getattr(container, "TYPE", None)
    if component_type == 18:
        label = container.label
        if not isinstance(label, str) or not 1 <= len(label) <= 45:
            raise ValueError("modal Label requires a label of 1 to 45 characters")
        if container.description is not None and len(container.description) > 100:
            raise ValueError("modal Label description exceeds 100 characters")
        if getattr(container.component, "TYPE", None) not in (3, 4, 5, 6, 7, 8, 19, 21, 22, 23):
            raise ValueError("modal Label requires one modal input component")
    elif component_type == 1:
        children = container.components
        if children is None or len(children) != 1 or getattr(children[0], "TYPE", None) != 4:
            raise ValueError("modal ActionRow requires exactly one TextInput")
