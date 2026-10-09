"""Every input: the dataset, its version and citation, and the codebook's own outcome names."""
from pathlib import Path

LABEL = "Educational demos made to show an open-source tool. Not research."
PRIZE = "Nobel Peace Prize 2026, Navanethem Pillay, \"for her efforts to promote peace and international law\" (nobelprize.org)"

HERE = Path(__file__).resolve().parent.parent
RAW = HERE / "data" / "raw" / "UCDPConflictTerminationDataset_v4_2024_Conflict.csv"
DERIVED = HERE / "data" / "conflict_years.csv"

# The newest version on https://ucdp.uu.se/downloads/ (checked 9 October 2026): v.4 2024, conflict level.
DATA_URL = "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv"
DATA_SHA256 = "6f3a739fa5c6e23ab3dde169d0d06f139677b7a9cf5ce5b2dcb3bf3ab39f9b7d"
DERIVED_SHA256 = "297fa489bffc5347f8ba9d994ebc17b5a29b34172b655195e7007a0b1a2fed97"
RAW_ROWS = 2752  # conflict-years in the file (one row per active conflict-year, 1946-2024)
VERSION = "v.4 2024"
VERSION_FIELD = "4.2024002"  # the file's own `version` column
CODEBOOK = "UCDP Conflict Termination Dataset Codebook v.4 2024, Joakim Kreutz, 24 June 2025"
CODEBOOK_URL = "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Codebook.pdf"
CITATION = ("Kreutz, Joakim, 2010. How and When Armed Conflicts End: Introducing the UCDP Conflict Termination "
            "Dataset. Journal of Peace Research 47(2): 243-250.")
LICENCE = "CC BY 4.0"
ACD_VERSION = "25.1"  # the codebook: the data corresponds with the UCDP/PRIO Armed Conflict data v 25.1
CODED_FIRST, CODED_LAST = 1946, 2023  # terminations are coded for 1946-2023; 2024 rows have no c_epterm yet
ACTIVE_LAST_YEAR = 2024

# Codebook section "c outcome" (outcome 2 is called "Ceasefire agreement" in the list of outcomes).
OUTCOMES = {
    "1": "Peace agreement",
    "2": "Ceasefire agreement",
    "3": "Victory for Side A (government side)",
    "4": "Victory for Side B (non-state side)",
    "5": "Low activity",
    "6": "Actor ceases to exist",
}
AGREEMENT = ("1", "2")  # choice: "ended in a peace agreement or ceasefire" = outcome 1 or 2
CLEAR = ("1", "2", "3", "4")  # a clear outcome: agreement, ceasefire or victory (not low activity, not actor ceases)
LOW_ACTIVITY = "5"
TREND_CENTRE = 1985  # years are centred here before the trend fit (does not change the slope)
TREND_SINCE = 1989  # a second trend fit from this year on (the end of the Cold War)
LAST_COMPLETE_DECADE_END = 2019  # the 2020s hold only 2020-2023
P_FLOOR = 0.001  # p below this is written "p < 0.001"
DERIVED_COLUMNS = ("c_epid", "year", "c_epterm", "c_outcome")  # numbers only: no names of places or parties
Z95 = 1.959963984540054
