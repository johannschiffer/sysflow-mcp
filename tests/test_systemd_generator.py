"""
Unit tests for SystemdGenerator and PortAuditor.
"""
from sysflow.core.systemd_generator import SystemdGenerator
from sysflow.core.port_auditor import PortAuditor

def test_systemd_generator():
    res = SystemdGenerator.generate_unit(
        service_name="my-backup",
        exec_start="/usr/bin/python3 /app/backup.py",
        cwd="/app",
        timer_schedule="12h"
    )
    assert res["service_filename"] == "my-backup.service"
    assert "ExecStart=/usr/bin/python3 /app/backup.py" in res["service_content"]
    assert res["has_timer"] is True
    assert "OnUnitActiveSec=12h" in res["timer_content"]

def test_port_auditor():
    res = PortAuditor.audit_listening_ports()
    assert res["success"] is True
    assert "count" in res
    assert isinstance(res["listening_ports"], list)
