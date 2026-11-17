import json
import sqlite3
import subprocess
import sys

from sysflow.server import SysFlowServer


def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import sysflow._genesis; sysflow._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import sysflow._genesis
    assert sysflow._genesis.NOTICE == ""


def test_blackbox_bridge_records_subprocess_event(monkeypatch, tmp_path):
    wal_db = tmp_path / "wal.sqlite"
    monkeypatch.setenv("BLACKBOX_DB_PATH", str(wal_db))

    server = SysFlowServer()
    res = server.handle_tool_call("run_sandboxed_task", {"command": "echo hello"})
    assert res["success"] is True

    wal_conn = sqlite3.connect(str(wal_db))
    rows = wal_conn.execute(
        "SELECT event_type, source, status, payload FROM blackbox_events ORDER BY id ASC;"
    ).fetchall()
    wal_conn.close()

    assert len(rows) == 1
    assert rows[0][0] == "SUBPROCESS"
    assert rows[0][1] == "sysflow-mcp"
    assert rows[0][2] == "ok"
    payload = json.loads(rows[0][3])
    assert payload["tool"] == "run_sandboxed_task"
    assert payload["command"] == "echo hello"
    assert payload["returncode"] == 0
