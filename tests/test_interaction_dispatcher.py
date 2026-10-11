"""A transport-independent dispatcher routes known interaction types."""

from types import SimpleNamespace

from discord.ext.interaction.implementation.interaction_dispatcher import InteractionDispatcher


def test_dispatcher_routes_and_gates_commands():
    events = []

    class Context:
        def __init__(self, payload, client):
            self.application_type = payload.get("command_type", 1)

    client = SimpleNamespace(_interactions={1: {}})
    dispatcher = InteractionDispatcher(
        client, lambda event, context: events.append(event),
        {kind: Context for kind in (2, 3, 4, 5)},
    )
    assert dispatcher.route({"type": 1}) is None
    dispatcher.route({"type": 2, "command_type": 1})
    assert events == []
    client._interactions[1]["hello"] = object()
    for kind in (2, 3, 4, 5):
        dispatcher.route({"type": kind, "command_type": 1})
    assert events == ["interaction_command", "components", "autocomplete", "modal"]
