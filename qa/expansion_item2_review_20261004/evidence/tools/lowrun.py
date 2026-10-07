"""Run a command at BELOW_NORMAL priority and pass its output and exit code through.

A bounded owned child: after LOWRUN_TIMEOUT seconds (default 200; 0 = no limit) the child's own process tree is stopped and
the exit code is 124, so a test that crashes without reaching quit() cannot hold a review matrix forever."""
import os
import subprocess
import sys

limit = float(os.environ.get("LOWRUN_TIMEOUT", "200"))
proc = subprocess.Popen(sys.argv[1:], creationflags=0x00004000)
try:
    code = proc.wait(timeout=limit if limit > 0 else None)
except subprocess.TimeoutExpired:
    # only the tree of the child started above
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(proc.pid)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait()
    print("LOWRUN_TIMEOUT: stopped after %d s" % int(limit), flush=True)
    code = 124
sys.exit(code)
