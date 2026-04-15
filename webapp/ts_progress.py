"""
Lightweight in-memory progress tracking for active detection runs.
"""

import copy
import threading
import time
from datetime import datetime, timezone


TERMINAL_STATUSES = {"completed", "cancelled", "error"}


def _utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class DetectionProgressTracker:
    def __init__(self, terminal_ttl_seconds=30):
        self._terminal_ttl_seconds = terminal_ttl_seconds
        self._lock = threading.Lock()
        self._states = {}

    def _prune_expired_locked(self):
        now = time.time()
        expired_session_ids = [
            session_id
            for session_id, state in self._states.items()
            if state.get("expires_at") is not None and state["expires_at"] <= now
        ]
        for session_id in expired_session_ids:
            self._states.pop(session_id, None)

    def _copy_locked(self, state, include_internal=False):
        payload = copy.deepcopy(state)
        if not include_internal:
            payload.pop("run_token", None)
            payload.pop("expires_at", None)
        return payload

    def _mark_terminal_locked(self, state, status):
        if status in TERMINAL_STATUSES:
            state["expires_at"] = time.time() + self._terminal_ttl_seconds
        else:
            state["expires_at"] = None

    def start(
        self,
        session_id,
        run_token,
        provider,
        engine,
        tile_count=0,
        status="running",
        phase="preparing_tiles",
        title="Preparing tiles",
        detail="Starting detection request...",
        counts=None,
        cancel_requested=False,
    ):
        now_iso = _utc_now_iso()
        state = {
            "status": status,
            "phase": phase,
            "title": title,
            "detail": detail,
            "provider": provider,
            "engine": engine,
            "tile_count": tile_count,
            "counts": copy.deepcopy(counts) if counts else {},
            "cancel_requested": cancel_requested,
            "started_at": now_iso,
            "updated_at": now_iso,
            "run_token": run_token,
            "expires_at": None,
        }

        with self._lock:
            self._prune_expired_locked()
            self._states[session_id] = state
            self._mark_terminal_locked(state, status)
            return self._copy_locked(state, include_internal=True)

    def update(
        self,
        session_id,
        run_token=None,
        status=None,
        phase=None,
        title=None,
        detail=None,
        counts=None,
        cancel_requested=None,
        tile_count=None,
    ):
        with self._lock:
            self._prune_expired_locked()
            state = self._states.get(session_id)
            if state is None:
                return None
            if run_token is not None and state.get("run_token") != run_token:
                return None

            if status is not None:
                state["status"] = status
            if phase is not None:
                state["phase"] = phase
            if title is not None:
                state["title"] = title
            if detail is not None:
                state["detail"] = detail
            if cancel_requested is not None:
                state["cancel_requested"] = cancel_requested
            if tile_count is not None:
                state["tile_count"] = tile_count
            if counts:
                merged_counts = dict(state.get("counts", {}))
                merged_counts.update(copy.deepcopy(counts))
                state["counts"] = merged_counts

            state["updated_at"] = _utc_now_iso()
            self._mark_terminal_locked(state, state["status"])
            return self._copy_locked(state, include_internal=True)

    def mark_cancel_requested(self, session_id):
        with self._lock:
            self._prune_expired_locked()
            state = self._states.get(session_id)
            if state is None:
                return None
            if state.get("status") in TERMINAL_STATUSES:
                return self._copy_locked(state, include_internal=True)

            state["status"] = "cancel_requested"
            state["phase"] = "cancel_requested"
            state["title"] = "Cancelling detection"
            state["detail"] = "Waiting for the active detection run to stop..."
            state["cancel_requested"] = True
            state["updated_at"] = _utc_now_iso()
            self._mark_terminal_locked(state, state["status"])
            return self._copy_locked(state, include_internal=True)

    def finish(self, session_id, status, run_token=None, **fields):
        return self.update(session_id, run_token=run_token, status=status, **fields)

    def get(self, session_id, include_internal=False):
        with self._lock:
            self._prune_expired_locked()
            state = self._states.get(session_id)
            if state is None:
                return {
                    "status": "idle",
                    "phase": "idle",
                    "title": "No active detection",
                    "detail": "No tower-detection run is currently active.",
                    "counts": {},
                    "cancel_requested": False,
                    "tile_count": 0,
                }
            return self._copy_locked(state, include_internal=include_internal)

    def clear(self, session_id, run_token=None):
        with self._lock:
            self._prune_expired_locked()
            state = self._states.get(session_id)
            if state is None:
                return False
            if run_token is not None and state.get("run_token") != run_token:
                return False
            self._states.pop(session_id, None)
            return True
