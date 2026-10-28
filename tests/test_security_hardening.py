"""
Security and correctness regression tests for SysFlow MCP.
"""

import os
import pytest
from sysflow.core.task_runner import TaskRunner
from sysflow.core.systemd_generator import SystemdGenerator
from sysflow.monitors.logs import LogTailer


def test_task_runner_blocks_shell_chaining_and_scrubs_secrets(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_should_not_leak")
    blocked = TaskRunner.run_command("echo ok; uname -a")
    assert blocked["success"] is False
    assert "disabled" in blocked["error"]

    res = TaskRunner.run_command("env")
    assert res["success"] is True
    assert "ghp_should_not_leak" not in res["stdout"]


def test_log_tailer_blocks_sensitive_files_and_filters_before_slicing(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=123\n", encoding="utf-8")
    denied = LogTailer.tail(str(env_file))
    assert denied["success"] is False
    assert "denied" in denied["error"].lower()

    outside = LogTailer.tail("/etc/passwd")
    assert outside["success"] is False

    log_file = tmp_path / "service.log"
    lines = ["ERROR early failure"] + [f"INFO noise {i}" for i in range(120)]
    log_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    filtered = LogTailer.tail(str(log_file), lines=5, pattern="ERROR")
    assert filtered["success"] is True
    assert filtered["lines_returned"] == 1
    assert "ERROR early failure" in filtered["lines"][0]


def test_systemd_generator_oncalendar_vs_interval_and_injection_guard():
    hourly = SystemdGenerator.generate_unit("cleanup-job", "/usr/bin/true", timer_schedule="hourly")
    assert "OnCalendar=hourly" in hourly["timer_content"]

    interval = SystemdGenerator.generate_unit("poll-job", "/usr/bin/true", timer_schedule="15min")
    assert "OnUnitActiveSec=15min" in interval["timer_content"]

    with pytest.raises(ValueError):
        SystemdGenerator.generate_unit("../bad", "/usr/bin/true")

    with pytest.raises(ValueError):
        SystemdGenerator.generate_unit("good", "/usr/bin/true\nExecStartPost=/bin/sh")
