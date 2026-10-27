"""
Unit tests for ResourceMonitor.
"""
from sysflow.monitors.resources import ResourceMonitor

def test_resource_monitor_stats():
    stats = ResourceMonitor.get_system_stats()
    assert "cpu" in stats
    assert "memory" in stats
    assert "disk" in stats
    assert stats["cpu"]["cores"] >= 1
    assert "load_average_1m" in stats["cpu"]
    assert stats["disk"]["total_gb"] > 0
