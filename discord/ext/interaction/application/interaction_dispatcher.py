"""Route Discord interaction payloads without depending on a receive transport."""

from collections.abc import Callable, Mapping


class InteractionDispatcher:
    """Build contexts and publish framework events for a received interaction."""

    EVENTS = {
        2: "interaction_command",
        3: "components",
        4: "autocomplete",
        5: "modal",
    }

    def __init__(
        self, client, dispatch: Callable, context_types: Mapping[int, type],
    ):
        self.client = client
        self.dispatch = dispatch
        self.context_types = context_types

    def route(self, payload: dict, *, publish: bool = True) -> object | None:
        """Return the parsed context, dispatching it when a handler is eligible."""
        interaction_type = payload.get("type")
        context_type = self.context_types.get(interaction_type)
        if context_type is None:
            return None
        context = context_type(payload, self.client)
        if interaction_type == 2 and publish:
            command_type = context.application_type
            if not self.client._interactions.get(command_type):
                return context
        if publish:
            self.dispatch(self.EVENTS[interaction_type], context)
        return context
