from __future__ import annotations
import sys
from pathlib import Path

def get_data_folder() -> Path:
    """Return the path to the external `data/` folder.

    - If running as a frozen executable (PyInstaller/py2exe), return the folder
      next to the executable: Path(sys.executable).parent / 'data'.
    - Otherwise return the repository-level `data/` relative to this file.
    """
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        return exe_dir / "data"
    # running from source; project layout expects repo/data next to src/
    return Path(__file__).parent.parent.resolve() / "data"
