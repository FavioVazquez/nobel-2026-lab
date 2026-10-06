"""Heat budget: how many neurons can one degree of warming buy? Educational demo, toy model.

Builds on the light-and-heat simulator in ../../simulator (imported as `simulator`, not copied).
"""
import sys
from pathlib import Path

_MEDICINE = Path(__file__).resolve().parents[2]  # 2026/medicine, which holds the `simulator` package
if str(_MEDICINE) not in sys.path:
    sys.path.insert(0, str(_MEDICINE))
