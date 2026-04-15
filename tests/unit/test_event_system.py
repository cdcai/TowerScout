"""
Unit tests for the current TowerScout event system API.
"""

from concurrent.futures import ThreadPoolExecutor

from ts_events import ExitEvents


def test_event_lifecycle():
    events = ExitEvents()
    session_id = 'session-1'

    assert events.query(session_id) is None

    events.alloc(session_id)
    assert events.query(session_id) is False

    events.signal(session_id)
    assert events.query(session_id) is True

    events.free(session_id)
    assert events.query(session_id) is None


def test_alloc_replaces_existing_event_state():
    events = ExitEvents()
    session_id = 'session-2'

    events.alloc(session_id)
    events.signal(session_id)
    assert events.query(session_id) is True

    events.alloc(session_id)
    assert events.query(session_id) is False


def test_free_missing_session_is_noop():
    events = ExitEvents()

    events.free('missing-session')

    assert events.query('missing-session') is None


def test_sessions_are_isolated():
    events = ExitEvents()
    session_a = 'session-a'
    session_b = 'session-b'

    events.alloc(session_a)
    events.alloc(session_b)
    events.signal(session_a)

    assert events.query(session_a) is True
    assert events.query(session_b) is False


def test_thread_safe_alloc_signal_and_free():
    events = ExitEvents()
    session_ids = [f'session-{i}' for i in range(20)]

    def worker(session_id):
        events.alloc(session_id)
        before_signal = events.query(session_id)
        events.signal(session_id)
        after_signal = events.query(session_id)
        events.free(session_id)
        after_free = events.query(session_id)
        return before_signal, after_signal, after_free

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(worker, session_ids))

    assert all(before is False for before, _, _ in results)
    assert all(after is True for _, after, _ in results)
    assert all(final is None for _, _, final in results)
