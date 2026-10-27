"""
Unit tests for LogTailer.
"""
from sysflow.monitors.logs import LogTailer

def test_log_tailer_text_and_regex(tmp_path):
    log_file = tmp_path / "app.log"
    content = "INFO 2026-10-20 Service started\nWARN Low memory\nERROR Connection failed\nINFO Heartbeat OK\n"
    log_file.write_text(content)

    # Tail last 2 lines
    res = LogTailer.tail(str(log_file), lines=2)
    assert res["success"] is True
    assert res["lines_returned"] == 2
    assert "INFO Heartbeat OK" in res["lines"][-1]

    # Tail with regex filter
    res_err = LogTailer.tail(str(log_file), lines=10, pattern=r"ERROR|WARN")
    assert res_err["success"] is True
    assert res_err["lines_returned"] == 2
    assert any("ERROR" in l for l in res_err["lines"])

def test_log_tailer_binary_guard(tmp_path):
    bin_file = tmp_path / "test.bin"
    bin_file.write_bytes(b"\x00\x01\x02\x03\x04\xff")
    res = LogTailer.tail(str(bin_file))
    assert res["success"] is False
    assert "binary file" in res["error"]
