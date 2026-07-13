from pathlib import Path

import orchestrator


def test_process_needs_action_claims_task_before_running_loop(tmp_path, monkeypatch):
    vault = tmp_path / "AI_Employee_Vault"
    needs_action = vault / "Needs_Action"
    in_progress = vault / "In_Progress" / "orchestrator"
    done = vault / "Done"

    for directory in (needs_action, in_progress, done):
        directory.mkdir(parents=True, exist_ok=True)

    task_file = needs_action / "task_1.md"
    task_file.write_text("status: pending\n", encoding="utf-8")

    calls = []

    monkeypatch.setattr(orchestrator, "VAULT_PATH", vault)
    monkeypatch.setattr(orchestrator, "SCRIPTS_DIR", tmp_path / "scripts")
    monkeypatch.setattr(orchestrator, "update_dashboard", lambda: None)

    def fake_run_ralph_loop(task_id, prompt):
        calls.append(task_id)
        return True

    monkeypatch.setattr(orchestrator, "run_ralph_loop", fake_run_ralph_loop)

    orchestrator.process_needs_action()
    orchestrator.process_needs_action()

    assert len(calls) == 1
    assert not task_file.exists()
    claimed_task = in_progress / "task_1.md"
    assert claimed_task.exists()


def test_run_claude_task_returns_false_when_claude_cli_is_missing(monkeypatch):
    monkeypatch.setattr(orchestrator.shutil, "which", lambda name: None)

    assert orchestrator.run_claude_task("Do useful work") is False
