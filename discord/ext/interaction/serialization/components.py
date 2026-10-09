"""Map Discord component type numbers to their payload models."""

import inspect
from typing import Any

from ..domain.component import Component
from ..domain.unknown_component import UnknownComponent


class ComponentRegistry:
    """An instance-scoped registry for parsing component payloads."""

    def __init__(self):
        self._models: dict[int, type[Component]] = {}

    def register(self, model: type[Component]) -> None:
        if not isinstance(model, type) or not issubclass(model, Component):
            raise TypeError("component model must inherit Component")
        if inspect.isabstract(model):
            raise TypeError("component model must implement payload methods")
        component_type = getattr(model, "TYPE", None)
        if type(component_type) is not int or component_type <= 0:
            raise ValueError("component type must be a positive integer")
        previous = self._models.get(component_type)
        if previous is not None and previous is not model:
            raise ValueError(f"component type {component_type} is already registered")
        self._models[component_type] = model

    def from_payload(self, payload: dict[str, Any]) -> Component:
        component_type = payload["type"]
        model = self._models.get(component_type)
        if model is None:
            return UnknownComponent.from_payload(payload)
        return model.from_payload(payload)
