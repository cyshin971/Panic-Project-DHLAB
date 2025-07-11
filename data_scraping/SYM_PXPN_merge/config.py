import sys
from pathlib import Path

# Get the parent directory and add it to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent.parent)
sys.path.insert(0, parent_dir)