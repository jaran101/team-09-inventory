import sys
from pathlib import Path

INVENTORY_SDD_DIR = Path(__file__).resolve().parent.parent / "inventory-sdd"
sys.path.insert(0, str(INVENTORY_SDD_DIR))
