"""
Unit tests for TaskRunner sandboxing and timeouts.
"""
from sysflow.core.task_runner import TaskRunner

def test_task_runner_success():
    res = TaskRunner.run_command("echo 'SysFlow Test Output'")
    assert res["success"] is True
    assert res["exit_code"] == 0
    assert "SysFlow Test Output" in res["stdout"]
    assert res["timed_out"] is False

def test_task_runner_timeout_kill():
    # Execute a command that sleeps longer than timeout (2s sleep with 1s timeout)
    res = TaskRunner.run_command("sleep 3", timeout_sec=1)
    assert res["success"] is False
    assert res["timed_out"] is True
    assert "timed out after 1 seconds" in res["error"]
