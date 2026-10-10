"""Validate inline Discord interaction callback types by interaction kind."""

ALLOWED_CALLBACKS = {
    2: {4, 5, 9, 12},
    3: {4, 5, 6, 7, 9},
    4: {8},
    5: {4, 5, 6, 7},
}


def validate_inline_response(interaction_type: int, response: dict) -> None:
    if not isinstance(response, dict) or response.get(
        "type"
    ) not in ALLOWED_CALLBACKS.get(interaction_type, ()):
        raise ValueError("invalid inline callback type for interaction")
