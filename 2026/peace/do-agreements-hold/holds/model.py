"""From agreements and active conflict-years to (years observed, fighting resumed?) per agreement, on two clocks,
and the groups of linked conflicts that agreements share."""
import csv

from . import constants as C


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load():
    return _read(C.AGREEMENTS), _read(C.ACTIVE)


def conflict_ids(cell):
    return [c.strip() for c in cell.replace(";", ",").split(",") if c.strip()]


def active_years(active_rows):
    out = {}
    for r in active_rows:
        out.setdefault(r["conflict_id"], set()).add(int(r["year"]))
    return out


def is_active(agreement, active, year):
    return any(year in active.get(c, ()) for c in conflict_ids(agreement["conflict_id"]))


def first_quiet_year(agreement, active, last_year=C.LAST_YEAR):
    """The first calendar year after signing in which no conflict id the agreement lists is active (fewer than
    25 battle-related deaths); None if that never happens by the last year of data."""
    y = int(agreement["year"])
    return next((t for t in range(y + 1, last_year + 1) if not is_active(agreement, active, t)), None)


def quiet_spell(agreement, active, last_year=C.LAST_YEAR):
    """Main clock: the agreement first has to bring the fighting below the threshold. Counted from the year before
    its first quiet year q, to the first later active year (event = 1) or to the last year of data (event = 0), so
    "holding at 5 years" means 5 or more quiet years in a row. Returns (years, event, q - signing year), or None if
    the conflict never got below the threshold."""
    q = first_quiet_year(agreement, active, last_year)
    if q is None:
        return None
    nxt = next((t for t in range(q + 1, last_year + 1) if is_active(agreement, active, t)), None)
    t, e = (nxt - (q - 1), 1) if nxt else (last_year - (q - 1), 0)
    return t, e, q - int(agreement["year"])


def linked_groups(agreements):
    """{paid: group}: agreements whose conflict ids overlap, directly or through other agreements, share a group."""
    parent = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for r in agreements:
        ids = conflict_ids(r["conflict_id"])
        for c in ids[1:]:
            parent[find(c)] = find(ids[0])
    return {r["paid"]: find(conflict_ids(r["conflict_id"])[0]) for r in agreements}


def spell(agreement, active, last_year=C.LAST_YEAR):
    """Strict clock: years from signing to the first later calendar year in which the same conflict (any of its ids)
    is active (event = 1), or to the last year of data (event = 0, still holding when the data stop)."""
    y = int(agreement["year"])
    later = [t for c in conflict_ids(agreement["conflict_id"]) for t in active.get(c, ()) if t > y]
    return (min(later) - y, 1) if later else (last_year - y, 0)
