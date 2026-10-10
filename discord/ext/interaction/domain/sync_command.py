"""Independent policy switches for Discord command reconciliation."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SyncCommand:
    """Allow create, edit and delete operations in one explicit scope."""

    create: bool = True
    edit: bool = True
    delete: bool = True

    def __post_init__(self):
        if any(
            type(value) is not bool for value in (self.create, self.edit, self.delete)
        ):
            raise TypeError("SyncCommand create, edit and delete must be booleans")
