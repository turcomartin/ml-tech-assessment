import uuid
from app.server.models import AnalysisRecord


class InMemoryStorage:
    def __init__(self) -> None:
        self._store: dict[uuid.UUID, AnalysisRecord] = {}

    def save(self, record: AnalysisRecord) -> None:
        self._store[record.id] = record

    def get(self, record_id: uuid.UUID) -> AnalysisRecord | None:
        return self._store.get(record_id)
