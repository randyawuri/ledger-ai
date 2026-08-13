from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass(slots=True)
class DomainEvent:

    occurred_at: datetime = datetime.now(UTC)