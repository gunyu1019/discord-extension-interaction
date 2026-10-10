"""Inline callback types follow Discord's interaction response matrix."""

import pytest

from discord.ext.interaction.application.response_payload import validate_inline_response


@pytest.mark.parametrize("interaction_type,callback_type", [
    (2, 4), (2, 9), (2, 12), (3, 7), (4, 8), (5, 6),
])
def test_allowed_inline_callbacks(interaction_type, callback_type):
    validate_inline_response(interaction_type, {"type": callback_type})


@pytest.mark.parametrize("interaction_type,callback_type", [
    (2, 7), (3, 8), (4, 4), (5, 9),
])
def test_invalid_inline_callbacks(interaction_type, callback_type):
    with pytest.raises(ValueError, match="invalid inline"):
        validate_inline_response(interaction_type, {"type": callback_type})
