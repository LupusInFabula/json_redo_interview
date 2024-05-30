from contextlib import suppress

from json_redo_interview.crash_recovery import CrashRecovery
from json_redo_interview.db import db_session


def test_crash_recovery() -> None:
    tot_events = 20
    crash_after = 7

    with suppress(ValueError), CrashRecovery("test.json", db_session) as cr:
        assert cr.event_source == "test.json"
        assert cr.db_session == db_session
        assert not cr.restore_point

        db_session.tot_processed = crash_after
        raise ValueError("Test")

    assert cr.crash_recovery_file.exists()
    with cr.crash_recovery_file.open() as f:
        assert f.read() == f"event_source,tot_processed\ntest.json,{crash_after}\n"

    with CrashRecovery("test.json", db_session) as cr:
        assert cr.restore_point == {"test.json": crash_after}
        items = cr.resume_if_needed(iter(range(tot_events)))
        assert db_session.tot_processed == crash_after
        assert len(list(items)) == tot_events - crash_after
