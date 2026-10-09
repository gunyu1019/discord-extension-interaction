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


def _validate_unique_custom_ids(components) -> None:
    seen = set()
    for component in components:
        custom_id = getattr(component, "custom_id", None)
        if custom_id is None:
            continue
        if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
            raise ValueError("component custom_id must contain 1 to 100 characters")
        if custom_id in seen:
            raise ValueError(f"duplicate component custom_id: {custom_id}")
        seen.add(custom_id)


def validate_legacy_message_components(components) -> None:
    """Validate top-level rows and interaction IDs in a legacy message."""
    if len(components) > 5:
        raise ValueError("legacy message accepts at most 5 ActionRows")
    children = []
    for row in components:
        if getattr(row, "TYPE", None) != 1:
            raise ValueError("legacy message requires top-level ActionRows")
        validate_message_action_row(row)
        children.extend(row.components)
    _validate_unique_custom_ids(children)


def validate_modal_components(components) -> None:
    """Validate modal container placement and interaction IDs."""
    if not 1 <= len(components) <= 5:
        raise ValueError("modal requires 1 to 5 top-level components")
    children = []
    for container in components:
        component_type = getattr(container, "TYPE", None)
        if component_type not in (1, 18, 10):
            raise ValueError("modal requires top-level Labels, Text Displays, or legacy ActionRows")
        if component_type in (1, 18):
            validate_modal_container(container)
            children.extend(container.components)
    _validate_unique_custom_ids(children)


def validate_v2_message_fields(*, content: bool, embeds: bool, poll: bool, stickers: bool) -> None:
    """Reject message fields disabled by IS_COMPONENTS_V2."""
    disabled = [
        name for name, present in (
            ("content", content), ("embeds", embeds),
            ("poll", poll), ("stickers", stickers),
        ) if present
    ]
    if disabled:
        raise ValueError("Components V2 cannot include " + ", ".join(disabled))


def _component_count(component) -> int:
    children = getattr(component, "components", None) or ()
    total = 1 + sum(_component_count(child) for child in children)
    accessory = getattr(component, "accessory", None)
    if accessory is not None:
        total += _component_count(accessory)
    return total


def validate_v2_component_count(components) -> None:
    """Count containers and their nested components against Discord's limit."""
    if sum(_component_count(component) for component in components) > 40:
        raise ValueError("Components V2 allows at most 40 total components")


def validate_v2_component_layout(payloads: list[dict]) -> None:
    """Check V2 placement and unique component/id identifiers."""
    component_ids = set()
    custom_ids = set()

    def visit(payload: dict, allowed: set[int]) -> None:
        component_type = payload.get("type")
        if component_type not in allowed:
            raise ValueError(f"component type {component_type} is invalid in this V2 position")

        component_id = payload.get("id")
        if component_id not in (None, 0):
            if type(component_id) is not int or not 0 <= component_id <= 0xFFFFFFFF:
                raise ValueError("component id must be a 32-bit unsigned integer")
            if component_id in component_ids:
                raise ValueError(f"duplicate component id: {component_id}")
            component_ids.add(component_id)

        custom_id = payload.get("custom_id")
        if custom_id is not None:
            if not isinstance(custom_id, str) or not 1 <= len(custom_id) <= 100:
                raise ValueError("component custom_id must contain 1 to 100 characters")
            if custom_id in custom_ids:
                raise ValueError(f"duplicate component custom_id: {custom_id}")
            custom_ids.add(custom_id)

        if component_type == 1:
            children = payload.get("components", [])
            child_types = [child.get("type") for child in children]
            if not (1 <= len(children) <= 5 and (
                all(item == 2 for item in child_types)
                or len(children) == 1 and child_types[0] in (3, 5, 6, 7, 8)
            )):
                raise ValueError("V2 ActionRow requires buttons or one select menu")
            for child in children:
                visit(child, {2, 3, 5, 6, 7, 8})
        elif component_type == 9:
            children = payload.get("components", [])
            if not 1 <= len(children) <= 3:
                raise ValueError("V2 Section requires 1 to 3 children")
            for child in children:
                visit(child, {10})
            visit(payload["accessory"], {2, 11})
        elif component_type == 17:
            children = payload.get("components", [])
            if not children:
                raise ValueError("V2 Container requires children")
            for child in children:
                visit(child, {1, 9, 10, 12, 13, 14})

    for payload in payloads:
        visit(payload, {1, 9, 10, 12, 13, 14, 17})


def validate_attachment_references(payloads: list[dict], filenames: set[str]) -> None:
    """Require every attachment:// media URL to name an attached file."""
    def visit(value) -> None:
        if isinstance(value, dict):
            url = value.get("url")
            if isinstance(url, str) and url.startswith("attachment://"):
                filename = url[len("attachment://"):]
                if not filename or filename not in filenames:
                    raise ValueError(f"missing file for attachment reference: {url}")
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(payloads)
