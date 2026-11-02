"""Serialize application command metadata shared by command types."""


def to_register_fields(command) -> dict:
    """Return Discord API metadata fields from an existing command model."""
    fields = {}
    if command.nsfw:
        fields["nsfw"] = True
    if command.default_member_permissions is not None:
        fields["default_member_permissions"] = command.default_member_permissions
    if command.contexts:
        fields["contexts"] = [int(context) for context in command.contexts]
    if command.integration_types:
        fields["integration_types"] = [int(kind) for kind in command.integration_types]
    return fields
