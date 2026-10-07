"""Run a command at BELOW_NORMAL priority and pass its output and exit code through."""
import subprocess
import sys

sys.exit(subprocess.run(sys.argv[1:], creationflags=0x00004000).returncode)
