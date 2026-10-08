import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

INVENTORY_SDD_DIR = PROJECT_ROOT / "inventory-sdd"
sys.path.insert(0, str(INVENTORY_SDD_DIR))
