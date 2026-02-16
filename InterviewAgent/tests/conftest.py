import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Ensure project root is importable
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Backward-compat import shim for tests using InterviewAgent.src...
if "InterviewAgent" not in sys.modules:
    pkg = types.ModuleType("InterviewAgent")
    pkg.__path__ = [str(ROOT)]
    sys.modules["InterviewAgent"] = pkg
