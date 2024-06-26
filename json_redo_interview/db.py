class FakeDB:
    """
    Fake DB storing data in memory.

    Storing failed events here currently serves not purpose other than debugging,
    but if this was a real database it would be useful to be able to address failed events
    via and admin panel for example.
    """

    def __init__(self) -> None:
        self.tot_processed = 0
        self._rows: list[dict] = []

    def insert_failed(self, data: dict, reason: str) -> int:
        self._rows.append({"status": "failed", "reason": reason, "data": data})
        self.increase_processed()
        return len(self._rows) - 1

    def increase_processed(self) -> None:
        self.tot_processed += 1

    @property
    def row_count(self) -> int:
        return len(self._rows)


db_session = FakeDB()
