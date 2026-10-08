"""Her books by the forms that their own titles and subtitles, or the Nobel Committee, name.

Source: the Committee's bio-bibliography, https://www.nobelprize.org/prizes/literature/2026/bio-bibliography/
(accessed 2026-10-08). Its list is headed "Bibliography – a selection", so everything here is a selection too.

Rules for a tag:
  * basis "line":      the evidence is a substring of that work's own bibliography line (title, subtitle or the
                       Committee's bracketed note), stored in data/committee_bibliography.json. Tests check this.
  * basis "committee": the evidence is a short phrase from the Committee's essay on the same page. A test checks it
                       byte for byte against a saved copy of the page when one is given (env LIT_BIO_HTML).
No tag is our own reading of the book. A work with no form named on its line or in the essay gets no tag.
Evidence strings are short facts or Committee phrases, never the author's own text.
"""

# The tag vocabulary. Labels are ours; each tag on a work must rest on its evidence.
TAGS = {
    "verse": "verse / poetry",
    "essay": "essay",
    "fiction": "novel / fiction",
    "translation": "translation / version",
    "drama": "plays / tragedy",
    "opera": "opera / libretto / music",
    "object": "book-object / artists' book / comic",
    "collaboration": "made with another artist",
    "performance": "performance / recording",
    "scholarship": "scholarly thesis",
    "classical": "in dialogue with a classical author",
}
TAG_ORDER = list(TAGS)

L, C = "line", "committee"

# (n, short title, year, [(tag, basis, evidence), ...], note)
# n is the entry number in data/committee_bibliography.json (1-33 "Works in English", 34-49 "Other").
WORKS = [
    (1, "Odi et Amo Ergo Sum", 1981, [
        ("scholarship", L, "Thesis (Ph.D.)"),
        ("scholarship", C, "doctoral thesis in Classics"),
    ], ""),
    (2, "Eros the Bittersweet", 1986, [
        ("essay", L, "An Essay"),
        ("essay", C, "In her long essay Eros the Bittersweet"),
        ("classical", C, "a compound adjective from Sappho"),
    ], "The Committee: the book 'lays the foundation for her subsequent authorship'."),
    (3, "Short Talks", 1992, [], "No form named on its line or in the essay."),
    (4, "Plainwater", 1995, [
        ("essay", L, "Essays and Poetry"),
        ("verse", L, "Essays and Poetry"),
    ], ""),
    (5, "Glass, Irony, and God", 1995, [
        ("verse", C, "the potential of the long poem"),
        ("essay", C, "transformed into an essay about abandonment"),
    ], "Both Committee phrases are about 'The Glass Essay', a long poem in this book."),
    (6, "Wild Workshop", 1997, [], "A shared volume (three authors on the line); the Committee notes it holds 'The Glass Essay'."),
    (7, "Autobiography of Red", 1998, [
        ("fiction", L, "A Novel in Verse"),
        ("verse", L, "A Novel in Verse"),
        ("classical", C, "poem fragments by the sixth century BC Greek poet Stesichoros"),
    ], "The Committee: 'often heralded as Carson’s greatest' (its words, not ours)."),
    (8, "Glass and God", 1998, [], "A London edition; no form named."),
    (9, "Economy of the Unlost", 1999, [
        ("essay", C, "the essay Economy of the Unlost"),
        ("classical", L, "Reading Simonides of Keos with Paul Celan"),
    ], ""),
    (10, "Men in the Off Hours", 2000, [
        ("classical", C, "she aligns the historian Thucydides with Virginia Woolf"),
    ], "No form named; the Committee names the pairing only."),
    (11, "Electra (Sophocles)", 2001, [
        ("translation", L, "translated by Anne Carson"),
        ("drama", C, "tragedies such as Sophocles’s Electra (2001) and Antigone (2015) and Euripides’s Bakkhai (2015)"),
        ("classical", L, "Electra / Sophocles"),
    ], ""),
    (12, "The Beauty of the Husband", 2001, [
        ("essay", L, "A Fictional Essay in 29 Tangos"),
        ("fiction", L, "A Fictional Essay in 29 Tangos"),
    ], "The Committee: 'twenty-nine episodes'."),
    (13, "If Not, Winter (Sappho)", 2002, [
        ("translation", L, "translated by Anne Carson"),
        ("classical", L, "Fragments of Sappho"),
    ], "The Committee: 'her interpretation of Sappho’s poem fragments'."),
    (14, "Wonderwater", 2004, [
        ("object", L, "Artists’ books"),
        ("collaboration", L, "Roni Horn, annotated by Anne Carson"),
    ], ""),
    (15, "Decreation", 2005, [
        ("verse", L, "Poetry, Essays, Opera"),
        ("essay", L, "Poetry, Essays, Opera"),
        ("opera", L, "Poetry, Essays, Opera"),
    ], ""),
    (16, "Grief Lessons (Euripides)", 2006, [
        ("translation", L, "translated by Anne Carson"),
        ("drama", L, "Four Plays"),
        ("classical", L, "Grief Lessons: Four Plays / Euripides"),
    ], ""),
    (17, "An Oresteia", 2009, [
        ("translation", L, "translated by Anne Carson"),
        ("classical", L, "Agamemnon by Aiskhylos, Elektra by Sophocles, Orestes by Euripides"),
    ], ""),
    (18, "Nox", 2010, [
        ("object", C, "a box containing an accordion-fold-out"),
        ("object", C, "a creation as sculptural as it is literary"),
        ("translation", C, "translation of the poem"),
        ("classical", C, "the Roman poet Catullus, with his famous elegy 101"),
    ], "The Committee calls it 'an epitaph'; the translated poem is Catullus 101."),
    (19, "“Electra” and other plays (Sophocles)", 2010, [
        ("translation", L, "translated by Anne Carson"),
        ("drama", L, "and other plays"),
        ("classical", L, "“Electra” and other plays / Sophocles"),
    ], ""),
    (20, "Antigonick (Sophokles)", 2012, [
        ("translation", L, "translated by Anne Carson"),
        ("collaboration", L, "illustrated by Bianca Stone"),
        ("object", L, "illustrated by Bianca Stone"),
        ("classical", L, "Antigonick / Sophokles"),
    ], ""),
    (21, "Red Doc>", 2013, [], "No form named on its line or in the essay."),
    (22, "Nay Rather", 2013, [], "No form named on its line or in the essay."),
    (23, "Iphigenia among the Taurians (Euripides)", 2014, [
        ("translation", L, "translated by Anne Carson"),
        ("classical", L, "Iphigenia among the Taurians / Euripides"),
    ], ""),
    (24, "The Albertine Workout", 2014, [], "No form named on its line or in the essay."),
    (25, "Hack wit", 2015, [
        ("collaboration", L, "Roni Horn; with hack gloss by Anne Carson"),
    ], ""),
    (26, "Short Talks (new edition)", 2015, [], "A new edition of the 1992 book; no form named."),
    (27, "Antigone (Sophokles)", 2015, [
        ("translation", L, "translated by Anne Carson"),
        ("drama", C, "tragedies such as Sophocles’s Electra (2001) and Antigone (2015) and Euripides’s Bakkhai (2015)"),
        ("classical", L, "Antigone by Sophokles"),
    ], ""),
    (28, "Bakkhai (Euripides)", 2015, [
        ("translation", L, "a new version by Anne Carson"),
        ("drama", C, "tragedies such as Sophocles’s Electra (2001) and Antigone (2015) and Euripides’s Bakkhai (2015)"),
        ("classical", L, "Bakkhai by Euripides"),
    ], ""),
    (29, "Float", 2016, [
        ("object", C, "twenty-two chapbooks on different subjects, capable of being read in any order"),
    ], "See the 22! card."),
    (30, "Norma Jean Baker of Troy", 2019, [
        ("translation", L, "a version of Euripides’ Helen"),
        ("classical", L, "a version of Euripides’ Helen"),
    ], ""),
    (31, "H of H playbook", 2021, [], "No form named in the essay; we do not read a form into the word 'playbook'."),
    (32, "Wrong Norma", 2024, [
        ("performance", C, "a strongly performative aspect"),
    ], "The Committee: 'a diverse combination of texts'."),
    (33, "The Gender of Sound", 2025, [], "First published in Glass, Irony, and God (1995), per the line; no form named."),
    # ---- "Other"
    (34, "“Kinds of Water”", 1988, [("essay", L, "The Best American Essays 1988")], "A piece in an anthology."),
    (35, "“Chez l’Oxymoron”", 1989, [("essay", L, "essays from Grand street")], "A piece in an anthology."),
    (36, "“The Life of Towns”", 1990, [("verse", L, "The Best American Poetry of 1990")], "A piece in an anthology."),
    (37, "“Water Margins”", 1994, [("fiction", L, "Short fiction")], "A piece in an anthology."),
    (38, "Cassandra: voix intérieures", 1998, [
        ("object", L, "Exhibition catalog"),
        ("essay", L, "three essays"),
        ("collaboration", L, "Freda Guttman; Sandra L. Buckley; Anne Carson; Annie Martin"),
    ], ""),
    (39, "The Mirror of Simple Souls (recording)", 1999, [("performance", L, "[sound recording]")], ""),
    (40, "The Mirror of Simple Souls: An Opera Installation", 2003, [
        ("opera", L, "An Opera Installation (libretto)"),
        ("performance", L, "live performance"),
        ("collaboration", L, "images by Kim Anno"),
    ], "Performed in San Francisco, New York, Toronto and Ann Arbor, per the line."),
    (41, "It (Inger Christensen), introduction", 2006, [], "An introduction to another poet's book; no form tag."),
    (42, "Troyjam", 2008, [
        ("opera", L, "for Narrator and Orchestra"),
        ("collaboration", L, "Michael Daugherty; text by Anne Carson"),
    ], ""),
    (43, "At the 92nd Street Y (audio)", 2009, [
        ("performance", L, "Audible Audio Edition"),
        ("verse", L, "in the form of 15 Sonnets"),
    ], ""),
    (44, "Spaces of Blank; Mask; Imprint (Michel van der Aa)", 2010, [
        ("collaboration", L, "Text of the 1st work by Anne Carson, Emily Dickinson, and Rozalie Hirs"),
    ], "Her text for another artist's work."),
    (45, "Uendelig konstant = Wildly Constant", 2012, [
        ("collaboration", L, "Anne Carson, Robert Currie"),
    ], ""),
    (46, "The Blue of Distance", 2015, [], "A shared volume; no form named."),
    (47, "If I’m Scared We Can’t Win", 2016, [], "A shared volume; no form named."),
    (48, "The Mile-Long Opera", 2018, [
        ("opera", L, "libretto by Anne Carson"),
        ("collaboration", L, "Composer David Lang"),
    ], ""),
    (49, "The Trojan Women: A Comic", 2021, [
        ("object", L, "A Comic"),
        ("collaboration", L, "by Rosanna Bruno; text by Anne Carson"),
        ("classical", L, "Euripides, The Trojan Women"),
    ], ""),
]

# The only line of hers allowed anywhere in the Literature folder (the Committee quotes it). Not used in this folder's
# figures; kept here so the tests can make sure no other line of hers slips in.
COMMITTEE_QUOTED_LINE = "hold in equipoise two perspectives at once"
