import subprocess
import sys

def test_notice_is_silent():
    res = subprocess.run([sys.executable, "-c", "import sysflow._genesis; sysflow._genesis.print_upgrade_notice()"], capture_output=True, text=True)
    assert res.stderr == ""
    assert res.stdout == ""
    import sysflow._genesis
    assert sysflow._genesis.NOTICE == ""
