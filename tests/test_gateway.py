"""Gateway event hooks on ConnectionState.parsers."""
import discord
import pytest


class _Ctx:
    """Lightweight stand-in for the interaction context classes."""

    def __init__(self, data, client):
        self.data = data
        inner = data.get("data", {})
        self.name = inner.get("name")
        self.application_type = inner.get("type")


@pytest.fixture
def hooked_client(monkeypatch):
    """An offline client whose parser hooks wrap *recording* stubs.

    The real ``parse_interaction_create`` / ``parse_message_create`` need a full
    gateway payload, so they are replaced before the client is built (that is
    when ``_install_interaction_parsers`` captures them as the "original").
    """
    from discord.ext import interaction
    from discord.ext.interaction.implementation import client as client_mod

    for name in (
        "ApplicationContext",
        "ComponentsContext",
        "AutocompleteContext",
        "ModalSubmitContext",
    ):
        monkeypatch.setattr(client_mod, name, _Ctx)

    orig_calls = []
    monkeypatch.setattr(
        discord.state.ConnectionState,
        "parse_interaction_create",
        lambda self, data: orig_calls.append(("interaction", data.get("type"))),
    )
    monkeypatch.setattr(
        discord.state.ConnectionState,
        "parse_message_create",
        lambda self, data: orig_calls.append(("message", data.get("id"))),
    )

    client = interaction.Client(intents=discord.Intents.none())
    dispatched = []
    # our parsers call state.dispatch, which is bound at ConnectionState
    # construction — patch it there, not on the client.
    monkeypatch.setattr(
        client._connection, "dispatch", lambda ev, *a, **k: dispatched.append(ev)
    )
    return client, orig_calls, dispatched


def test_both_events_are_wrapped(hooked_client):
    client, _, _ = hooked_client
    for event in ("INTERACTION_CREATE", "MESSAGE_CREATE"):
        parser = client._connection.parsers[event]
        assert parser.__qualname__.startswith("ClientBase._chain_parser")


def test_original_parser_still_runs_before_our_handler(hooked_client):
    client, orig_calls, _ = hooked_client
    client._connection.parsers["INTERACTION_CREATE"]({"type": 4, "data": {}})
    assert ("interaction", 4) in orig_calls


@pytest.mark.parametrize(
    "interaction_type, expected_event",
    [(3, "components"), (4, "autocomplete"), (5, "modal")],
)
def test_component_autocomplete_modal_dispatch(
    hooked_client, interaction_type, expected_event
):
    client, _, dispatched = hooked_client
    client._connection.parsers["INTERACTION_CREATE"](
        {"type": interaction_type, "data": {}}
    )
    assert expected_event in dispatched


def test_application_command_dispatch_is_gated_on_registration(hooked_client):
    from discord.ext.interaction import ApplicationCommandType

    client, _, dispatched = hooked_client
    frame = {"type": 2, "name": "x", "data": {"type": 2}}  # command type 2 = USER

    # nothing registered -> suppressed
    client._connection.parsers["INTERACTION_CREATE"](frame)
    assert "interaction_command" not in dispatched

    # register a USER command -> dispatched
    client._interactions[ApplicationCommandType.USER]["x"] = object()
    client._connection.parsers["INTERACTION_CREATE"](frame)
    assert "interaction_command" in dispatched


def test_message_create_dispatches_interaction_message(hooked_client, monkeypatch):
    from discord.ext.interaction.implementation import client as client_mod

    client, orig_calls, dispatched = hooked_client
    monkeypatch.setattr(
        discord.state.ConnectionState,
        "_get_guild_channel",
        lambda self, data, gid=None: (None, None),
    )
    monkeypatch.setattr(client_mod, "Message", lambda **kw: ("MSG", kw["data"]["id"]))

    client._connection.parsers["MESSAGE_CREATE"]({"id": 7})
    assert ("message", 7) in orig_calls
    assert "interaction_message" in dispatched


def test_exception_in_our_handler_is_isolated():
    from discord.ext.interaction.implementation.client import ClientBase

    seen = []
    chained = ClientBase._chain_parser(
        lambda d: seen.append("original"),
        lambda d: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    chained({"type": 99})  # must not raise
    assert seen == ["original"]
