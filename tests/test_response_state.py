"""Initial interaction responses advance only after successful transport calls."""

import pytest

from discord.ext.interaction.response_state import ResponsePhase, ResponseState
from discord.ext.interaction.errors import AlreadyDeferred


def test_response_state_allows_defer_then_edit_and_rejects_duplicate_initial():
    state = ResponseState()
    assert state.phase is ResponsePhase.NEW
    state.deferred()
    with pytest.raises(AlreadyDeferred):
        state.deferred()
    state.responded()
    assert state.phase is ResponsePhase.RESPONDED
    with pytest.raises(RuntimeError, match="already responded"):
        state.ensure_initial_available()
