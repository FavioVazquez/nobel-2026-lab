"""One command: python -m sapphofrag.run_all  (build results/fragments.json, then every figure, light and dark)."""
from . import build, figures


def main() -> None:
    data = build.main()
    figures.main()
    st = data["stats"]
    print("fragments.json written: %d Wharton numbers, %d verse entries, median %g words, %d (%.1f%%) <= 5 words"
          % (st["n_numbers"], st["n_entries_verse"], st["median_words"], st["count_le_5"], 100 * st["share_le_5"]))


if __name__ == "__main__":
    main()
