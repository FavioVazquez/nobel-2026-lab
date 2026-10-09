"""Every input: the two UCDP files, their versions and citations, and our definition of "holding"."""
from pathlib import Path

LABEL = "Educational demos made to show an open-source tool. Not research."
PRIZE = "Nobel Peace Prize 2026, Navanethem Pillay, \"for her efforts to promote peace and international law\" (nobelprize.org)"

HERE = Path(__file__).resolve().parent.parent
RAW_DIR = HERE / "data" / "raw"

# Newest versions on https://ucdp.uu.se/downloads/ (checked 9 October 2026).
PA_URL = "https://ucdp.uu.se/downloads/peace/ucdp-peace-agreements-222.xlsx"
PA_SHA256 = "9a5666173defffe4c2937d96c5201b8e8891f289b1c32e0e24f45f517abc161a"
PA_RAW = RAW_DIR / "ucdp-peace-agreements-222.xlsx"
PA_VERSION = "22.2"
PA_ROWS = 374
PA_CODEBOOK = "UCDP Peace Agreement Dataset Codebook v 22.1, Stina Högbladh, 2022 (the newest codebook on the page)"
PA_CITATION = ("Pettersson, Therese; Stina Högbladh & Magnus Öberg (2019) Organized violence, 1989-2018 and peace "
               "agreements. Journal of Peace Research 56(4).")
PA_CODEBOOK_CITATION = ("Högbladh, Stina (2022) UCDP Peace Agreement Dataset Codebook v 22.1 "
                        "(https://ucdp.uu.se/downloads/)")
TERM_URL = "https://ucdp.uu.se/downloads/monadterm/UCDPConflictTerminationDataset_v4_2024_Conflict.csv"
TERM_SHA256 = "6f3a739fa5c6e23ab3dde169d0d06f139677b7a9cf5ce5b2dcb3bf3ab39f9b7d"
TERM_RAW = RAW_DIR / "UCDPConflictTerminationDataset_v4_2024_Conflict.csv"
TERM_VERSION = "v.4 2024"
TERM_ROWS = 2752
TERM_CITATION = ("Kreutz, Joakim, 2010. How and When Armed Conflicts End: Introducing the UCDP Conflict Termination "
                 "Dataset. Journal of Peace Research 47(2): 243-250.")
ACD_VERSION = "25.1"
LICENCE = "CC BY 4.0"

AGREEMENTS = HERE / "data" / "agreements.csv"
ACTIVE = HERE / "data" / "active_years.csv"
AGREEMENT_COLUMNS = ("paid", "conflict_id", "year", "pa_type")  # ids, years, codes: no names, no free text
ACTIVE_COLUMNS = ("conflict_id", "year")
AGREEMENTS_SHA256 = "dc3a5e4cf7dc553ea52473813981c971b896683d521154bbbfd302c7ff0cbaaf"
ACTIVE_SHA256 = "5c3d755be0568ddbfb2bd55d268b879913ac8f83ee1da7a392004d75365e9a8f"

PA_TYPES = {"1": "Full", "2": "Partial", "3": "Peace process"}  # codebook, pa_type
LAST_YEAR = 2024  # last year of conflict activity in the Termination file (UCDP/PRIO ACD 25.1)
HORIZONS = (5, 10)
SETTLED_LATE_YEARS = 5  # a first quiet year this many years or more after signing is hard to credit to the agreement
BOOT_REPS, BOOT_SEED = 2000, 2026  # cluster bootstrap over linked conflict groups
FIGURE_YEARS = 20  # curves are drawn to here; few agreements are still observed later
Z95 = 1.959963984540054
