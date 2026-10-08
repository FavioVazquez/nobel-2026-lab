"""Counts for the forms shelf, the 22! card and the prize's own history. Pure arithmetic, no models."""
import json
import math
from collections import Counter, OrderedDict
from pathlib import Path

from . import works as W

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BIB_FILE = DATA / "committee_bibliography.json"
API_FILE = DATA / "nobel_api_lit_2026-10-08.json"

BIO_URL = "https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/"
PR_2026 = "https://www.nobelprize.org/prizes/literature/2026/press-release/"
PR_2013 = "https://www.nobelprize.org/prizes/literature/2013/press-release/"
PR_1976 = "https://www.nobelprize.org/prizes/literature/1976/press-release/"
WOMEN_URL = "https://www.nobelprize.org/prizes/lists/nobel-prize-awarded-women/"

FLOAT_CHAPBOOKS = 22  # Committee: Float (2016), "a work consisting of twenty-two chapbooks ... capable of being read in any order"
JULIAN_YEAR_S = 365.25 * 24 * 3600  # seconds in a Julian year (IAU definition)
# Age of the universe, for scale only: 13.787 +/- 0.020 billion years, Planck 2018 results VI, Table 2
# (Planck Collaboration, A&A 641, A6, 2020, arXiv:1807.06209).
UNIVERSE_AGE_YEARS = 13.787e9


def load_bibliography():
    return json.loads(BIB_FILE.read_text(encoding="utf-8"))


def load_api():
    return json.loads(API_FILE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- forms
def forms_table():
    bib = {e["n"]: e for e in load_bibliography()["entries"]}
    rows = []
    for n, title, year, ev, note in W.WORKS:
        entry = bib[n]
        tags = []
        for tag, _, _ in ev:
            if tag not in tags:
                tags.append(tag)
        tags.sort(key=W.TAG_ORDER.index)
        rows.append(OrderedDict(
            n=n, section=entry["section"], title=title, year=year, bibliography_line=entry["line"],
            tags=tags,
            evidence=[{"tag": t, "basis": b, "evidence": e} for t, b, e in ev],
            note=note,
        ))
    return rows


def forms_summary(rows):
    per_tag = Counter(t for r in rows for t in r["tags"])
    form_tags = [t for t in W.TAG_ORDER if t != "classical"]
    multi = [r for r in rows if len([t for t in r["tags"] if t in form_tags]) >= 2]
    eng = [r for r in rows if r["section"] == "Works in English"]
    return OrderedDict(
        entries=len(rows),
        entries_works_in_english=len(eng),
        entries_other=len(rows) - len(eng),
        entries_with_a_form_tag=sum(1 for r in rows if any(t in form_tags for t in r["tags"])),
        entries_with_no_tag=sum(1 for r in rows if not r["tags"]),
        entries_with_two_or_more_form_tags=len(multi),
        entries_with_two_or_more_form_tags_titles=[r["title"] for r in multi],
        works_per_tag=OrderedDict((t, per_tag.get(t, 0)) for t in W.TAG_ORDER),
        tags_from_line_only=sum(1 for r in rows for e in r["evidence"] if e["basis"] == "line"),
        tags_from_committee_essay=sum(1 for r in rows for e in r["evidence"] if e["basis"] == "committee"),
        first_year=min(r["year"] for r in rows),
        last_year=max(r["year"] for r in rows),
    )


def float_card():
    n = math.factorial(FLOAT_CHAPBOOKS)
    years = n / JULIAN_YEAR_S
    mantissa, exp = f"{n:.3e}".split("e")
    return OrderedDict(
        chapbooks=FLOAT_CHAPBOOKS,
        chapbooks_source=f"Nobel Committee bio-bibliography, {BIO_URL}: 'twenty-two chapbooks on different subjects, capable of being read in any order'",
        orderings=str(n),  # string: JavaScript numbers cannot hold it exactly
        orderings_grouped=f"{n:,}",
        orderings_digits=len(str(n)),
        orderings_scientific=f"{mantissa} × 10^{int(exp)}",
        formula="22! = 22 × 21 × ... × 2 × 1 (orderings of 22 distinct items)",
        years_at_one_ordering_per_second=float(f"{years:.4g}"),
        years_note="22! seconds in Julian years (365.25 days); pure arithmetic",
        times_age_of_universe=round(years / UNIVERSE_AGE_YEARS),
        age_of_universe_years=UNIVERSE_AGE_YEARS,
        age_of_universe_source="Planck Collaboration 2018, results VI, A&A 641, A6 (2020), arXiv:1807.06209: 13.787 ± 0.020 Gyr",
        caveat="The number counts orders only. It says nothing about how the book is meant to be read beyond the Committee's 'any order'.",
    )


# ---------------------------------------------------------------- prize history
def decade_label(y):
    return f"{y // 10 * 10}s"


def prize_history():
    api = load_api()
    laur = api["laureates"]
    prizes = api["nobelPrizes"]
    years_no_award = [p["awardYear"] for p in prizes if p["n_laureates"] == 0]
    shared = [p["awardYear"] for p in prizes if p["n_laureates"] > 1]
    women = [r for r in laur if r["gender"] == "female"]

    dec = OrderedDict()
    for p in prizes:
        y = int(p["awardYear"])
        d = dec.setdefault(decade_label(y), {"decade": decade_label(y), "first_year": y, "last_year": y,
                                             "award_years": 0, "years_with_no_award": 0,
                                             "laureates": 0, "women": 0, "women_names": []})
        d["last_year"] = y
        d["award_years"] += 1
        if p["n_laureates"] == 0:
            d["years_with_no_award"] += 1
    for r in laur:
        d = dec[decade_label(int(r["nobelPrizes.awardYear"]))]
        d["laureates"] += 1
        if r["gender"] == "female":
            d["women"] += 1
            d["women_names"].append(f'{r["knownName.en"]} ({r["nobelPrizes.awardYear"]})')

    born_canada = [r for r in laur if r["birth.place.country.en"] == "Canada" or r["birth.place.countryNow.en"] == "Canada"]
    carson = next(r for r in laur if r["id"] == "1067")
    women_sorted = sorted(women, key=lambda r: (int(r["nobelPrizes.awardYear"]), r["id"]))

    return OrderedDict(
        status="final",
        source=api["source"],
        urls=api["urls"],
        fetched=api["fetched"],
        totals=OrderedDict(
            award_years_1901_2026=len(prizes),
            years_awarded=len(prizes) - len(years_no_award),
            years_with_no_award=years_no_award,
            shared_years=shared,
            laureates=len(laur),
            laureates_meta_count=api["meta_counts"]["laureates"],
            women=len(women),
            men=sum(1 for r in laur if r["gender"] == "male"),
            gender_field="API field 'gender', as recorded by the Nobel Prize API",
        ),
        carson=OrderedDict(
            id=carson["id"], name=carson["knownName.en"], year=carson["nobelPrizes.awardYear"],
            motivation=carson["nobelPrizes.motivation.en"],
            woman_number=1 + [r["id"] for r in women_sorted].index("1067"),
            cross_check=f"nobelprize.org list of women laureates: {WOMEN_URL}",
        ),
        by_decade=list(dec.values()),
        women=[{"year": r["nobelPrizes.awardYear"], "name": r["knownName.en"]} for r in women_sorted],
        canada=OrderedDict(
            field_birth_country=OrderedDict(
                field="birth.place.country.en / birth.place.countryNow.en (place of birth, not citizenship)",
                laureates=[{"year": r["nobelPrizes.awardYear"], "name": r["knownName.en"],
                            "birth.place.country.en": r["birth.place.country.en"],
                            "birth.place.countryNow.en": r["birth.place.countryNow.en"]} for r in born_canada],
                count=len(born_canada),
            ),
            field_press_release_wording=OrderedDict(
                field="the Swedish Academy's press release: 'awarded to the Canadian author ...'",
                laureates=[
                    {"year": "2013", "name": "Alice Munro", "wording": "awarded to the Canadian author Alice Munro", "url": PR_2013},
                    {"year": "2026", "name": "Anne Carson", "wording": "awarded to the Canadian author Anne Carson", "url": PR_2026},
                ],
                count=2,
                checked="2026-10-08 (both pages fetched; the phrase is on each)",
            ),
            saul_bellow=("Born in Lachine, Quebec, Canada (API birth country: Canada), grew up in Chicago; the 1976 press "
                         f"release places him in 'American narrative art' ({PR_1976}). So he counts under birth country "
                         "but not under 'Canadian author'."),
            safe_line="Anne Carson is the second Canadian Literature laureate, after Alice Munro (2013).",
            caveat="The API records place of birth, not citizenship or writing language. A Canadian born abroad would not appear in the birth-country field.",
        ),
    )
