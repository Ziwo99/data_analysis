#!/usr/bin/env python3
"""
Simple script to launch the Streamlit app.py
"""
import os
import subprocess
import sys
from pathlib import Path

# Path to project root
project_root = Path(__file__).parent
src_dir = project_root / "src"

# Add src to PYTHONPATH so imports work
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Path to directory containing app.py
app_dir = project_root / "src" / "data_analysis" / "ui"

# Check that the file exists
app_file = app_dir / "app.py"
if not app_file.exists():
    print(f"❌ Error: File {app_file} does not exist!")
    sys.exit(1)

# Launch streamlit with PYTHONPATH set
print(f"🚀 Launching application from: {app_dir}")
env = dict(os.environ)
env["PYTHONPATH"] = str(src_dir) + (os.pathsep + env.get("PYTHONPATH", ""))
subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"], cwd=app_dir, env=env)