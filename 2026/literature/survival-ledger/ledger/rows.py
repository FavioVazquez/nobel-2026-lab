"""The survival ledger: every number, its range and its sources.

Rules (from the folder README):
  * Only authors the Nobel Committee names in its 2026 bio-bibliography (phrase stored per row, checked in tests).
  * Ancient testimony and modern estimates are kept apart, as ranges where sources disagree.
  * Every number has at least one source; most have two. A number we could not confirm on an opened page is listed
    under "unverified" and is not used in any figure.
  * No percentage of loss as a single number. The Sappho grid shows two estimates side by side, labelled "estimate".

Source checks: every quote below (and, for the paraphrased entries, every key word) was found in the text of its
page, fetched on 2026-10-08, by
ledger/check_sources.py (network; results in results/source_check.json). The pages themselves are not committed.
"""

ACCESSED = "2026-10-08"

# ------------------------------------------------------------------------------------------------ sources
# key: (short name, url, anchor in the source, exact quote (<= 30 words), how checked)
# For the sources in PARAPHRASED (the Suda On Line entries and the World History Encyclopedia article) the fourth field
# is OUR paraphrase, not a quote: those texts are under a Creative Commons Attribution-NonCommercial-ShareAlike
# licence, which does not fit this MIT repository. One rule for every NC-licensed source: we cite them and say what
# they say in our own words. check_sources.py checks their key words instead.
SOURCES = {
    # --- the Nobel Committee (who is named)
    "BIO": ("Nobel Committee for Literature, bio-bibliography 2026 (Anders Olsson)",
            "https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/", "essay and bibliography",
            "", "opened"),
    # --- the Suda (Suda On Line, English translations; the Suda is a 10th-century Byzantine encyclopedia).
    # Paraphrased in our words (see PARAPHRASED below), cited with entry and translator where the page names one.
    "SUDA_SAPPHO": ("Suda σ 107 (Sappho), Suda On Line, tr. E. Vandiver",
                    "https://www.cs.uky.edu/~raphael/sol/sol-entries/sigma/107", "Adler σ 107",
                    "The Suda credits Sappho with nine books of lyric poetry.", "opened; paraphrased"),
    "SUDA_STES": ("Suda σ 1095 (Stesichoros), Suda On Line",
                  "https://www.cs.uky.edu/~raphael/sol/sol-entries/sigma/1095", "Adler σ 1095",
                  "The Suda says his poems, in Doric Greek, filled 26 books.", "opened; paraphrased"),
    "SUDA_SIM": ("Suda σ 439 (Simonides), Suda On Line, tr. R. Dyer",
                 "https://www.cs.uky.edu/~raphael/sol/sol-entries/sigma/439", "Adler σ 439",
                 "The Suda lists the kinds of poem he wrote (laments, praise poems, epigrams, paeans, tragedies and "
                 "more) but gives no count.", "opened; paraphrased"),
    "SUDA_AESCH": ("Suda αι 357 (Aeschylus), Suda On Line",
                   "https://www.cs.uky.edu/~raphael/sol/sol-entries/alphaiota/357", "Adler αι 357",
                   "The Suda credits him with elegies and 90 tragedies.", "opened; paraphrased"),
    "SUDA_SOPH": ("Suda σ 815 (Sophocles), Suda On Line, tr. W. B. Tyrrell",
                  "https://www.cs.uky.edu/~raphael/sol/sol-entries/sigma/815", "Adler σ 815",
                  "The Suda gives 123 plays and adds that some put the number higher.", "opened; paraphrased"),
    "SUDA_EUR": ("Suda ε 3695 (Euripides), Suda On Line",
                 "https://www.cs.uky.edu/~raphael/sol/sol-entries/epsilon/3695", "Adler ε 3695",
                 "The Suda reports two counts, 75 plays and 92, and says 77 survived.", "opened; paraphrased"),
    # --- the 1914 papyrus edition
    "GH1914": ("B. P. Grenfell and A. S. Hunt, The Oxyrhynchus Papyri X (1914), no. 1231, introduction",
               "https://archive.org/details/oxyrhynchuspapyr10gren", "p. 20 (and Fr. 56, the end-title, p. 39)",
               "The number of verses comprised in it, we now learn, was 1320, i.e. 330 stanzas.", "opened"),
    "GH1914_TOTAL": ("B. P. Grenfell and A. S. Hunt, The Oxyrhynchus Papyri X (1914), no. 1231, introduction",
                     "https://archive.org/details/oxyrhynchuspapyr10gren", "p. 20",
                     "Sappho’s entire works may well have extended to something like 9,000 verses.", "opened"),
    # --- Wikipedia (CC BY-SA; facts only, cited)
    "WP_SAPPHO": ("Wikipedia, 'Sappho' (citing Rayor & Lardinois 2014, p. 7)", "https://en.wikipedia.org/wiki/Sappho",
                  "section 'Works'", "Sappho probably wrote around 10,000 lines of poetry; today, only about 650 survive.",
                  "opened"),
    "WP_SAPPHO_BOOKS": ("Wikipedia, 'Sappho' (citing Yatromanolakis 1999, p. 181)", "https://en.wikipedia.org/wiki/Sappho",
                        "section 'Ancient editions'",
                        "was divided into at least eight books, though the exact number is uncertain.", "opened"),
    "WP_SAPPHO_ODE": ("Wikipedia, 'Sappho'", "https://en.wikipedia.org/wiki/Sappho", "lead",
                      "only the Ode to Aphrodite is certainly complete.", "opened"),
    "GREEN2015": ("Peter Green, 'What we know', London Review of Books 37.22 (2015)",
                  "https://www.lrb.co.uk/the-paper/v37/n22/peter-green/what-we-know", "review of Sappho editions",
                  "if we estimate an overall total of some 10,000 lines we are unlikely to be far off.", "opened"),
    "GREEN2015_BOOK1": ("Peter Green, 'What we know', London Review of Books 37.22 (2015)",
                        "https://www.lrb.co.uk/the-paper/v37/n22/peter-green/what-we-know", "review of Sappho editions",
                        "the first book alone, consisting entirely of poems written in the Sapphic stanza, totalled 1320 lines",
                        "opened"),
    "MIZZOU": ("University of Missouri Libraries, Special Collections exhibit 'Sappho'",
               "https://library.missouri.edu/specialcollections/exhibits/show/lh2arts/sappho", "exhibit page",
               "out of an estimated 10,000 lines of poetry attributed to her, only 650 lines have survived.", "opened"),
    "ILLINOIS": ("University of Illinois Rare Book & Manuscript Library exhibit 'Sappho's lyrics'",
                 "https://exhibits.library.illinois.edu/s/rbml/page/sappho-lyrics", "exhibit page",
                 "some 650 lines and precisely one complete poem survives.", "opened"),
    # --- Stesichoros / Geryoneis
    "MAHONEY2009": ("A. Mahoney, review of M. Lazzeri, Studi sulla Gerioneide di Stesicoro, BMCR 2009.06.20 (archived copy)",
                    "https://web.archive.org/web/2024id_/https://bmcr.brynmawr.edu/?p=26633",
                    "original https://bmcr.brynmawr.edu/?p=26633",
                    "One of the papyrus fragments (S27, P. Oxy. 2617 frag. 7) includes a marginal line number, 1300",
                    "opened"),
    "MAHONEY2009_180": ("A. Mahoney, BMCR 2009.06.20 (archived copy)",
                        "https://web.archive.org/web/2024id_/https://bmcr.brynmawr.edu/?p=26633", "same review",
                        "only about 180 remain in any sort of readable form.", "opened"),
    "FINGLASS2022": ("P. J. Finglass, 'Of centaurs and satyrs: Stesichorus' Geryoneis and satyr-drama', Acta Linguistica Petropolitana 18.1 (2022)",
                     "https://cyberleninka.ru/article/n/of-centaurs-and-satyrs-stesichorus-geryoneis-and-satyrdrama",
                     "p. 1 and n. 3 (citing Davies & Finglass 2014 on fr. 25)", "was at least 1,300 lines long",
                     "opened"),
    "WEST1971": ("M. L. West, 'Stesichorus', Classical Quarterly 21 (1971) 302-314 (free first-page extract)",
                 "https://www.cambridge.org/core/journals/classical-quarterly/article/stesichorus/9FECE1F4E45300B708861156CBB11FED",
                 "first page", "contained at least 1,300 verses, the total being perhaps closer to two thousand.",
                 "opened"),
    "WP_GERYONEIS": ("Wikipedia, 'Geryoneis' (citing West 1993, p. xvi)", "https://en.wikipedia.org/wiki/Geryoneis",
                     "lead", "The length of the complete poem is estimated to 1300 lines.", "opened"),
    "WP_STES": ("Wikipedia, 'Stesichorus' (citing Pavese 1972 via Segal)", "https://en.wikipedia.org/wiki/Stesichorus",
                "section 'Poetry'", "a poem such as the Geryoneis included some 1500 lines", "opened"),
    # --- tragedians
    "WP_AESCH": ("Wikipedia, 'Aeschylus'", "https://en.wikipedia.org/wiki/Aeschylus", "section 'Works'",
                 "Aeschylus wrote an estimated 70 to 90 plays, of which only seven have survived in complete form.",
                 "opened"),
    "WHE_AESCH": ("M. Cartwright, 'Aeschylus', World History Encyclopedia (2015)", "https://www.worldhistory.org/Aeschylus/",
                  "section 'Aeschylus' Works'",
                  "It puts his output at 70 to 90 plays and says six or seven survive complete.",
                  "opened; paraphrased"),
    "IRELAND1986": ("S. Ireland, Aeschylus (New Surveys in the Classics 18, CUP 1986), ch. II abstract",
                    "https://www.cambridge.org/core/journals/new-surveys-in-the-classics/article/abs/ii-aeschylus-the-man-his-plays-and-times/651F06E9F4788A651C1C3CAAE855F56D",
                    "abstract", "70 tragedies, 5 satyr plays (Life), 73 dramas (Catalogue of Plays), 90 (Suda)",
                    "opened"),
    "DURHAM_AESCH": ("S. Burges Watson, 'Aeschylus: A Guide to Selected Sources', Living Poets, Durham University",
                     "https://livingpoets.awh.durham.ac.uk/w/index.php/Aeschylus:_A_Guide_to_Selected_Sources", "guide",
                     "whose attribution to Aeschylus is no longer accepted (see Griffith 1977)", "opened"),
    "WP_SOPH": ("Wikipedia, 'Sophocles' (citing Lloyd-Jones 2003, p. 3)", "https://en.wikipedia.org/wiki/Sophocles", "lead",
                "Sophocles wrote more than 120 plays", "opened"),
    "WP_SOPH_7": ("Wikipedia, 'Sophocles'", "https://en.wikipedia.org/wiki/Sophocles", "lead",
                  "but only seven have survived in a complete form", "opened"),
    "SMITH_SOPH": ("W. Smith (ed.), Dictionary of Greek and Roman Biography and Mythology (1867), 'Sophocles', via Perseus",
                   "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0104:entry=sophocles-bio-1",
                   "§4 The Works of Sophocles",
                   "The number of plays ascribed to Sophocles was 130, of which, however, according to Aristophanes of Byzantium, seventeen were spurious.",
                   "opened"),
    "DURHAM_SOPH": ("S. Burges Watson, 'Sophocles: A Guide to Selected Sources', Living Poets, Durham University",
                    "https://livingpoets.awh.durham.ac.uk/w/index.php/Sophocles:_A_Guide_to_Selected_Sources", "guide",
                    "He wrote over a hundred and twenty plays", "opened"),
    "WP_ICHN": ("Wikipedia, 'Ichneutae'", "https://en.wikipedia.org/wiki/Ichneutae", "lead",
                "more than four hundred lines surviving in their entirety or in part", "opened"),
    "WP_EUR": ("Wikipedia, 'Euripides'", "https://en.wikipedia.org/wiki/Euripides", "lead",
               "Some ancient scholars attributed ninety-five plays to him, but the Suda says it was ninety-two at most.",
               "opened"),
    "WP_EUR_19": ("Wikipedia, 'Euripides'", "https://en.wikipedia.org/wiki/Euripides", "lead",
                  "Nineteen plays attributed to Euripides have survived more or less complete", "opened"),
    "SMITH_EUR": ("W. Smith (ed.), Dictionary of Greek and Roman Biography and Mythology (1867), 'Euripides', via Perseus",
                  "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0104:entry=euripides-bio-2",
                  "on the number of plays (Varro in Aulus Gellius 17.4)",
                  "he wrote 75 tragedies and gained the prize only five times", "opened"),
    "SMITH_EUR_18": ("W. Smith (ed.), Dictionary of Greek and Roman Biography and Mythology (1867), 'Euripides', via Perseus",
                     "https://www.perseus.tufts.edu/hopper/text?doc=Perseus:text:1999.04.0104:entry=euripides-bio-2",
                     "on the extant plays", "18 are extant, if we omit the Rhesus", "opened"),
    "FURMAN_EUR": ("Furman University, Dramaturgy pages, 'Euripides: Rhesus'",
                   "https://folio.furman.edu/dramaturg/Euripides/Rhesus", "introduction",
                   "he produced approximately 92 plays over a career spanning from his debut in 455 BC until his death, with 18 or 19 surviving intact today.",
                   "opened"),
    "COLLARD1981": ("C. Collard, Euripides (New Surveys in the Classics 14, CUP 1981), ch. I",
                    "https://www.cambridge.org/core/journals/new-surveys-in-the-classics/article/i-the-extant-work/72E0DE7E22AD826146C172DD5D9AA398",
                    "ch. I", "Twenty-two performances give a total of 66 tragedies", "opened"),
    # --- Catullus
    "WP_POC": ("Wikipedia, 'Poetry of Catullus'", "https://en.wikipedia.org/wiki/Poetry_of_Catullus", "section on manuscripts",
               "V was the sole source of nearly all of the poet's surviving work.", "opened"),
    "WP_POC_DATE": ("Wikipedia, 'Poetry of Catullus'", "https://en.wikipedia.org/wiki/Poetry_of_Catullus",
                    "section on manuscripts", "clearly available to various Paduan and Veronese humanists in the period 1290–1310",
                    "opened"),
    "WP_POC_18": ("Wikipedia, 'Poetry of Catullus'", "https://en.wikipedia.org/wiki/Poetry_of_Catullus",
                  "section on the numbering", "Three of the poems, however—18, 19 and 20—are excluded from most modern editions",
                  "opened"),
    "LOEB1921": ("F. W. Cornish, Catullus, Loeb Classical Library (1913/1921), Introduction, archive.org text",
                 "https://archive.org/details/catullustibullus00catu", "Introduction, pp. vi-vii",
                 "designated V (Veronensis), which is known to have been at Verona early in the fourteenth century, and which disappeared before the end of the century.",
                 "opened"),
    "LOEB1921_T": ("F. W. Cornish, Catullus, Loeb Classical Library (1913/1921), Introduction",
                   "https://archive.org/details/catullustibullus00catu", "Introduction, p. vii",
                   "with the exception of Cod. Thuaneus of the ninth century, containing only Carm. lxii.", "opened"),
    "KISS2015": ("D. Kiss, 'Isaac Vossius, Catullus and the Codex Thuaneus', Classical Quarterly 65 (2015), abstract",
                 "https://www.cambridge.org/core/journals/classical-quarterly/article/isaac-vossius-catullus-and-the-codex-thuaneus/83969A9B6D530363CE53DE9002938DC0",
                 "abstract", "the earliest complete manuscripts of Catullus to survive today were written in the fourteenth century",
                 "opened"),
    "NSC2021": ("New Surveys in the Classics 51, Catullus (CUP 2021), ch. I, n. 11",
                "https://www.cambridge.org/core/journals/new-surveys-in-the-classics/article/i-catullus-and-his-cultural-milieu/FD152820160CD10EA9BCCDB4F8A7A507",
                "n. 11", "The figure of 113 is necessarily approximate", "opened"),
    "WP_CAT": ("Wikipedia, 'Catullus'", "https://en.wikipedia.org/wiki/Catullus", "infobox and §Sources and organization",
               "Catullus's poems have been preserved in an anthology of 116 carmina", "opened"),
    "POETS_CAT": ("Academy of American Poets, 'Gaius Valerius Catullus'", "https://poets.org/poet/gaius-valerius-catullus",
                  "biography", "born in Verona in 84 BC", "opened"),
    # --- Simonides
    "WP_SIM": ("Wikipedia, 'Simonides of Ceos'", "https://en.wikipedia.org/wiki/Simonides_of_Ceos", "lead",
               "c. 556 – 468 BC", "opened"),
    "WP_SIM_FR": ("Wikipedia, 'Simonides of Ceos'", "https://en.wikipedia.org/wiki/Simonides_of_Ceos", "section on the poetry",
                  "Today only glimpses of his poetry remain, either in the form of papyrus fragments or quotations by ancient literary figures",
                  "opened"),
    "AGNI_SIM": ("AGNI (Boston University), author page 'Simonides'", "https://agnionline.bu.edu/about/our-people/authors/simonides",
                 "author note", "only a small portion of the considerable output attributed to Simonides remains.",
                 "opened"),
    # --- Thucydides
    "WP_THUC": ("Wikipedia, 'Thucydides'", "https://en.wikipedia.org/wiki/Thucydides", "section on the History",
                "After his death, Thucydides's History was subdivided into eight books", "opened"),
    "WP_HPW": ("Wikipedia, 'History of the Peloponnesian War'", "https://en.wikipedia.org/wiki/History_of_the_Peloponnesian_War",
               "lead", "The account, apparently unfinished, does not cover the full war, ending mid-sentence in 411 BC.",
               "opened"),
    "EB1911_THUC": ("Encyclopaedia Britannica (1911), 'Thucydides', Wikisource",
                    "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Thucydides", "on the History",
                    "breaks off abruptly—in the middle of a sentence, indeed—in the year 411.", "opened"),
    "DIOD13": ("Diodorus Siculus 13.42, Loeb translation (C. H. Oldfather), LacusCurtius",
               "https://penelope.uchicago.edu/Thayer/E/Roman/Texts/Diodorus_Siculus/13C*.html", "13.42.5",
               "having included a period of twenty-two years in eight Books, although some divide it into nine", "opened"),
    "MARCELLINUS": ("Marcellinus, Life of Thucydides §58, tr. T. Burns, ToposText", "https://topostext.org/work/763", "§58",
                    "some men cut his work up into thirteen histories, others otherwise.", "opened"),
}

# Sources whose fourth field is our paraphrase, not a quote (Suda On Line and World History Encyclopedia: CC BY-NC-SA,
# cited, not copied: the rule is "we paraphrase NC-licensed sources", stated in the folder README).
# Each maps to the key words check_sources.py must find on the page: the facts the paraphrase rests on.
PARAPHRASED = {
    "SUDA_SAPPHO": ["9 books", "lyric"],
    "SUDA_STES": ["Doric", "26 books"],
    "SUDA_SIM": ["threnoi", "epigrams", "paeans", "tragedies"],
    "SUDA_AESCH": ["elegiac", "90 tragedies"],
    "SUDA_SOPH": ["123 plays", "many more"],
    "SUDA_EUR": ["75 plays", "92", "77 survive"],
    "WHE_AESCH": ["70 and 90", "six or seven"],
}

# Hosts whose licence is Creative Commons NonCommercial: every source on one of them must be in PARAPHRASED (tested).
NC_LICENSED = ("/~raphael/sol/", "worldhistory.org/")

# ------------------------------------------------------------------------------------------------ rows
ROWS = [
    {
        "id": "sophocles", "author": "Sophocles", "language": "Greek",
        "committee_phrase": "tragedies such as Sophocles’s Electra (2001) and Antigone (2015)",
        "dates": {"text": "c. 497/496 – 406/405 BC", "sources": ["WP_SOPH"]},
        "unit": "plays",
        "ancient_count": {"range": [113, 130], "unit": "plays",
                          "text": "123, or more by some counts (Suda); 130 ascribed, 17 of them spurious, so 113 "
                                  "(Aristophanes of Byzantium, as reported in the ancient tradition)",
                          "sources": ["SUDA_SOPH", "SMITH_SOPH"]},
        # Open-ended: both modern sources say "more than 120" / "over a hundred and twenty". The 130 ceiling is the
        # ancient ascription (Smith 1867, in ancient_count), not a modern estimate; the shelf's dashed 120-130 is only
        # a drawing range.
        "modern_estimate": {"value": 120, "open_ended": True, "unit": "plays",
                            "text": "more than 120; no exact number is possible",
                            "sources": ["WP_SOPH", "DURHAM_SOPH"]},
        "survives": {"value": 7, "unit": "complete plays",
                     "notes": "plus about half of the satyr play Ichneutae, from a papyrus (more than 400 lines in whole or part)",
                     "sources": ["WP_SOPH_7", "DURHAM_SOPH", "WP_ICHN"]},
        "shelf": {"total": [120, 130], "survive": [7, 7], "label": "7 complete plays of more than 120"},
    },
    {
        "id": "euripides", "author": "Euripides", "language": "Greek",
        "committee_phrase": "Euripides’s Bakkhai (2015)",
        "dates": {"text": "c. 480 – c. 406 BC", "sources": ["WP_EUR"]},
        "unit": "plays",
        "ancient_count": {"range": [75, 95], "unit": "plays",
                          "text": "75 or 92, and 77 surviving in the Suda's day (Suda); 75 (Varro, in Aulus Gellius); "
                                  "95 (some ancient scholars)",
                          "sources": ["SUDA_EUR", "SMITH_EUR", "WP_EUR"]},
        "modern_estimate": {"range": [88, 95], "unit": "plays",
                            "text": "about 90: 'approximately 92'; 22 productions of 4 plays give about 88",
                            "sources": ["FURMAN_EUR", "COLLARD1981", "WP_EUR"]},
        "survives": {"range": [18, 19], "unit": "complete plays",
                     "notes": "19 attributed to him, 18 if the Rhesus (authorship disputed) is left out; includes the "
                              "satyr play Cyclops",
                     "sources": ["WP_EUR_19", "SMITH_EUR_18", "FURMAN_EUR"]},
        "shelf": {"total": [88, 95], "survive": [18, 19], "label": "18 or 19 plays of about 90"},
    },
    {
        "id": "aeschylus", "author": "Aeschylus", "language": "Greek",
        "committee_phrase": "Agamemnon by Aiskhylos",
        "committee_phrase_where": "bibliography (An Oresteia, 2009)",
        "dates": {"text": "c. 525/524 – c. 456/455 BC", "sources": ["WP_AESCH"]},
        "unit": "plays",
        "ancient_count": {"range": [73, 90], "unit": "plays",
                          "text": "90 tragedies (Suda); 70 tragedies and 5 satyr plays (ancient Life) and 73 dramas "
                                  "(ancient catalogue), as summarised by Ireland 1986",
                          "sources": ["SUDA_AESCH", "IRELAND1986"]},
        "modern_estimate": {"range": [70, 90], "unit": "plays", "text": "an estimated 70 to 90",
                            "sources": ["WP_AESCH", "WHE_AESCH"]},
        "survives": {"range": [6, 7], "unit": "complete plays",
                     "notes": "7 survive complete; one of them, Prometheus Bound, is of disputed authorship, so 6 or 7",
                     "sources": ["WP_AESCH", "WHE_AESCH", "DURHAM_AESCH"]},
        "shelf": {"total": [70, 90], "survive": [6, 7], "label": "7 plays (one disputed) of 70 to 90"},
    },
    {
        "id": "stesichoros", "author": "Stesichoros", "language": "Greek",
        "committee_phrase": "poem fragments by the sixth century BC Greek poet Stesichoros",
        "dates": {"text": "c. 630 – c. 555 BC (Suda: born in the 37th Olympiad, died in the 56th)",
                  "sources": ["SUDA_STES", "WP_STES"]},
        "unit": "books",
        "ancient_count": {"value": 26, "unit": "books", "text": "26 books (Suda)", "sources": ["SUDA_STES"]},
        "modern_estimate": None,
        "modern_estimate_note": "No modern estimate of his whole output in lines was found; we give none.",
        "survives": {"value": 0, "unit": "complete poems", "notes": "only fragments, from quotations and papyri",
                     "sources": ["MAHONEY2009_180", "WP_STES"]},
        "shelf": {"total": [26, 26], "survive": [0, 0], "fragments": True, "label": "26 books, fragments only"},
    },
    {
        "id": "geryoneis", "author": "Stesichoros: the Geryon poem (Geryoneis)", "language": "Greek",
        "committee_phrase": "concerning the winged red monster Geryon",
        "dates": {"text": "6th century BC", "sources": ["BIO"]},
        "unit": "lines",
        "ancient_count": {"value": 1300, "unit": "lines (at least)",
                          "text": "a line number, 1300, written in the margin of the papyrus (P.Oxy. 2617 fr. 7 = S27): "
                                  "the poem had at least 1,300 lines",
                          "sources": ["MAHONEY2009", "FINGLASS2022"]},
        "modern_estimate": {"range": [1300, 2000], "unit": "lines",
                            "text": "at least 1,300; about 1,500 (Pavese); 'perhaps closer to two thousand' (West 1971)",
                            "sources": ["WEST1971", "WP_GERYONEIS", "WP_STES"]},
        "survives": {"value": 180, "unit": "readable lines (about)",
                     "notes": "about 180 lines in any sort of readable form; one source only, so shown as 'about'",
                     "sources": ["MAHONEY2009_180"]},
        "shelf": None,
    },
    {
        "id": "sappho", "author": "Sappho", "language": "Greek",
        "committee_phrase": "her interpretation of Sappho’s poem fragments",
        "dates": {"text": "c. 630 – c. 570 BC (Suda: born in the 42nd Olympiad, 612–609 BC)",
                  "sources": ["SUDA_SAPPHO", "WP_SAPPHO"]},
        "unit": "lines",
        "ancient_count": {"range": [8, 9], "unit": "books",
                          "text": "nine books (Suda); the Alexandrian edition had at least eight books, "
                                  "the exact number uncertain",
                          "sources": ["SUDA_SAPPHO", "WP_SAPPHO_BOOKS"]},
        "ancient_book1": {"value": 1320, "unit": "verses",
                          "text": "Book I held 1,320 verses (330 stanzas): the number written on the roll's own "
                                  "end-title, P.Oxy. 1231 fr. 56",
                          "sources": ["GH1914", "GREEN2015_BOOK1"]},
        "modern_estimate": {"range": [9000, 10000], "unit": "lines",
                            "text": "'something like 9,000 verses' (Grenfell & Hunt 1914); about 10,000 lines "
                                    "(Green 2015; Wikipedia after Rayor & Lardinois 2014; Missouri exhibit)",
                            "sources": ["GH1914_TOTAL", "GREEN2015", "WP_SAPPHO", "MIZZOU"]},
        "survives": {"value": 650, "unit": "lines (about)",
                     "notes": "about 650 lines; only one poem, fragment 1 (the Ode to Aphrodite), is certainly "
                              "complete. Green (2015) puts the surviving share at 'perhaps 5 per cent'.",
                     "sources": ["WP_SAPPHO", "MIZZOU", "ILLINOIS", "WP_SAPPHO_ODE"]},
        "shelf": {"total": [8, 9], "survive": [0, 0], "fragments": True,
                  "label": "8 or 9 books, fragments and one complete poem"},
        "grid": {"total": 10000, "inked": 650, "book1": 1320, "alt_total": 9000, "label": "estimate"},
    },
    {
        "id": "simonides", "author": "Simonides of Keos", "language": "Greek",
        "committee_phrase": "the sixth century BC Greek poet Simonides of Keos",
        "dates": {"text": "c. 556 – 468 BC (Suda: born in the 56th Olympiad)", "sources": ["WP_SIM", "SUDA_SIM"]},
        "unit": "poems",
        "ancient_count": None,
        "ancient_count_note": "The Suda lists his kinds of poem (laments, odes, epigrams, paeans, tragedies) but gives "
                              "no count.",
        "ancient_count_sources": ["SUDA_SIM"],
        "modern_estimate": None,
        "modern_estimate_note": "No count of his output was found; we give none.",
        "survives": {"value": None, "unit": "fragments",
                     "notes": "only a small part: fragments from papyri and quotations, and some short pieces whole; "
                              "a papyrus published in 1992 (P.Oxy. 3965, the 'New Simonides', an elegy on the battle "
                              "of Plataea) 'quadrupled' what we have (AGNI)",
                     "sources": ["WP_SIM_FR", "AGNI_SIM"]},
        "shelf": None,
    },
    {
        "id": "catullus", "author": "Catullus", "language": "Latin",
        "committee_phrase": "the Roman poet Catullus, with his famous elegy 101",
        "dates": {"text": "c. 84 – c. 54 BC", "sources": ["WP_CAT", "POETS_CAT"]},
        "unit": "poems",
        "ancient_count": None,
        "ancient_count_note": "No ancient count of his poems was found.",
        "ancient_count_sources": [],
        "modern_estimate": {"range": [113, 116], "unit": "poems",
                            "text": "116 numbered poems; 18, 19 and 20 are left out of most modern editions, so about "
                                    "113 ('necessarily approximate'). A few lines quoted by ancient writers are not in "
                                    "the manuscripts, so some poems are lost.",
                            "sources": ["WP_CAT", "WP_POC_18", "NSC2021"]},
        "survives": {"range": [113, 116], "unit": "poems",
                     "notes": "Nearly all of them reached us through one manuscript, V, known at Verona around 1300 "
                              "(c. 1290–1310) and lost before 1400; all complete copies date from the 14th century "
                              "or later. Poem 62 also survives in a 9th-century anthology (the Codex Thuaneus).",
                     "sources": ["WP_POC", "WP_POC_DATE", "LOEB1921", "LOEB1921_T", "KISS2015"]},
        "shelf": {"total": [1, 1], "survive": [1, 1], "label": "one book of about 113 poems, through one lost manuscript"},
    },
    {
        "id": "thucydides", "author": "Thucydides", "language": "Greek",
        "committee_phrase": "she aligns the historian Thucydides with Virginia Woolf",
        "dates": {"text": "c. 460 – c. 400 BC", "sources": ["WP_THUC", "EB1911_THUC"]},
        "unit": "books",
        "ancient_count": {"value": 8, "unit": "books",
                          "text": "8 books by the usual division; some ancient readers divided it into 9 (Diodorus) "
                                  "or 13 (Marcellinus)",
                          "sources": ["DIOD13", "MARCELLINUS"]},
        "modern_estimate": {"value": 8, "unit": "books", "text": "8 books (a later division, not his own)",
                            "sources": ["WP_THUC"]},
        "survives": {"value": 8, "unit": "books",
                     "notes": "all of it, but unfinished: it breaks off mid-sentence in 411 BC, and the war went on to 404 BC",
                     "sources": ["WP_HPW", "EB1911_THUC"]},
        "shelf": {"total": [8, 8], "survive": [8, 8], "label": "all 8 books, but it stops mid-sentence in 411 BC"},
    },
]

# Items we looked for and could not confirm on an opened page. None of them is used in a figure or a sentence.
UNVERIFIED = [
    "Which Greek letter-numeral the Geryoneis papyrus uses for 1,300 (sources say only 'a marginal line number, 1300').",
    "The anonymous ancient Life of Euripides' counts (92 plays, 78 preserved): seen only in a search snippet.",
    "Rayor & Lardinois 2014, p. 7 (the book Wikipedia cites for 10,000 / 650): not opened; Wikipedia's citation only.",
    "An ancient count of Catullus' poems: none found (absence not proven).",
    "The exact day of the Paris manuscript G of Catullus (Loeb 1921 says 29 October 1375; other memory says 19 October): we say 1375.",
    "Who edited P.Oxy. 3965 (the New Simonides): not on any opened page; we give only the number and the year (1992, Oxyrhynchus Papyri vol. LIX).",
    "Encyclopaedia Britannica and Oxford Classical Dictionary figures: both sites refused automated access (HTTP 403).",
    "Smith (1867) elsewhere reports 27, not 17, spurious plays for Sophocles; we use the main entry's 17 and the Suda's 123.",
]

RESOLVED_OPEN_ITEMS = {
    "play counts, Suda vs modern": "Kept apart: ancient testimony (Suda and others) and modern estimates as two ranges per tragedian.",
    "Geryoneis length and its source": "At least 1,300 lines, from a marginal line number in P.Oxy. 2617 fr. 7 (S27); estimates up to about 2,000.",
    "Catullus manuscript history wording": "Nearly all of Catullus reached us through one manuscript (V), known at Verona around 1300 (c. 1290–1310) and lost before 1400; poem 62 also in the 9th-century Codex Thuaneus.",
    "Sappho ~10,000 vs ~650; Book I 1,320": "Estimate 9,000-10,000 lines in all; about 650 survive; Book I 1,320 verses from the roll's end-title (P.Oxy. 1231 fr. 56; Grenfell & Hunt 1914, p. 20).",
}
