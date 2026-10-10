"""Apply a SyncPlan through an injected command transport."""

from dataclasses import dataclass
from enum import Enum

from .sync_planner import SyncOperation, SyncPlan, SyncPlanItem
from ..domain.sync_command import SyncCommand


class SyncOutcome(Enum):
    APPLIED = "applied"
    SKIPPED = "skipped"
    UNCHANGED = "unchanged"
    FAILED = "failed"


@dataclass(frozen=True)
class SyncItemResult:
    item: SyncPlanItem
    outcome: SyncOutcome
    response: object | None = None
    error: Exception | None = None


@dataclass(frozen=True)
class SyncResult:
    plan: SyncPlan
    items: tuple[SyncItemResult, ...]

    @property
    def failures(self) -> tuple[SyncItemResult, ...]:
        return tuple(item for item in self.items if item.outcome is SyncOutcome.FAILED)


async def apply_sync_plan(
    plan: SyncPlan,
    policy: SyncCommand,
    transport,
) -> SyncResult:
    """Continue after individual API failures and report each attempted action."""
    results = []
    for item in plan.items:
        operation = item.operation
        if operation is SyncOperation.UNCHANGED:
            results.append(SyncItemResult(item, SyncOutcome.UNCHANGED))
            continue
        if not getattr(policy, operation.value):
            results.append(SyncItemResult(item, SyncOutcome.SKIPPED))
            continue
        try:
            if operation is SyncOperation.CREATE:
                response = await transport.create(plan.scope, item.local)
            elif operation is SyncOperation.EDIT:
                response = await transport.edit(plan.scope, item.local, item.remote)
            else:
                response = await transport.delete(plan.scope, item.remote)
        except Exception as error:
            results.append(SyncItemResult(item, SyncOutcome.FAILED, error=error))
        else:
            results.append(SyncItemResult(item, SyncOutcome.APPLIED, response=response))
    return SyncResult(plan, tuple(results))
