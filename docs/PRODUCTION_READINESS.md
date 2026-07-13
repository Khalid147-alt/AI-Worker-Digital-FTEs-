# Production Readiness Snapshot

## Current verified status
This repository now has a verified regression test covering the scheduler race condition and the missing-Claude hard-block behavior.

## Verified regression coverage
-   Test file: `tests/test_orchestrator.py`
-   Command: `python -m pytest -q tests/test_orchestrator.py`
-   Result: `2 passed in 0.10s`

## Root-cause fixes implemented
1. **Claim-first task ownership**
   -   The orchestrator now moves a markdown task into `In_Progress/<worker_id>` before starting the Ralph loop.
2. **Bounded background execution**
   -   The scheduler tracks active futures explicitly and only finalizes tasks when the worker has returned.
3. **Hard-block runtime failures**
   -   Missing Claude CLI is treated as a blocked task rather than a silent success.
4. **Portable config bootstrap**
   -   Runtime paths are resolved from `.env` with a repo-root fallback instead of machine-specific absolute paths.

## Known production follow-ups
-   Continue moving the remaining watcher and integration modules to the same env-driven bootstrap pattern.
-   Expand coverage around watchdog restart behavior, audit tamper evidence, and approval workflow transitions.
