# Peace 2026: two rooms (video, 2:35)

> **Educational demos made to show an open-source tool. Not research.** Made with [showtime](https://github.com/FavioVazquez/showtime), an open-source video studio for coding agents.

A two-and-a-half-minute explainer of this year's Nobel Peace Prize, in two rooms side by side. On the left, the courtroom: Navi Pillay's path from Durban to the Rwanda tribunal, the two cases she sat on there (Akayesu, 1998, one of three judges; the Media case, 2003, which she presided), the International Criminal Court, her years as UN High Commissioner for Human Rights (with a short excerpt of her own voice) and her seat at the International Court of Justice since 2019. On the right, the field: how 507 armed-conflict episodes ended from 1946 to 2023, and whether 374 peace agreements held, from the open data of the Uppsala Conflict Data Program. The rooms meet on the committee's line "Peace requires justice." The film asks the viewer no questions. The two experiments behind it are [how-conflicts-end](../how-conflicts-end/README.md) and [do-agreements-hold](../do-agreements-hold/README.md), and you can try them on [the page](https://faviovazquez.github.io/nobel-2026-lab/2026/peace/page/).

| File | What it is |
|---|---|
| [`exports/nobel-2026-peace.mp4`](exports/nobel-2026-peace.mp4) | The video: 1920x1080, 2:35, 18.1 MB (the GitHub-size copy of the master), -13.9 LUFS integrated; the narration is not captioned in the picture (use the .srt), her words in the footage carry an English caption plate |
| [`exports/nobel-2026-peace.srt`](exports/nobel-2026-peace.srt) | The captions as a separate file (59 cues: the narration, and her words in the footage as the film's English caption, marked [Navi Pillay, 2013]) |
| [`exports/poster.jpg`](exports/poster.jpg) | The thumbnail frame: "Navi Pillay, Nobel Peace Prize 2026" and the citation on the warm left room, the 507 conflict endings as dots on the cool right room |

Only the finished film, its poster and its captions are kept here. The film's source (HTML scenes, timing, audio plan) and the critics' reports are not in this folder.

## How it was made

With [showtime](https://github.com/FavioVazquez/showtime): the scenes are HTML and canvas drawings that showtime renders frame by frame on one computer, with a local voice, music, captions and checks. The footage excerpt was cut from its transcript, cleaned and captioned in English with showtime; her words are shown as she says them. The look: a split screen throughout, warm brass light for the courtroom and cool steel for the field, merging to white on the committee's last line. The voice is synthetic (Kokoro, voice bf_isabella), made locally. There is no Nobel logo, medal or Nobel illustration of the laureate. The only likeness of her is the credited 2012 photo and the credited 2013 footage below.

## Credits

The full credits block, as in the film's description (the UCDP citations are required by CC BY 4.0, the footage and photo credits by CC BY 3.0 and CC BY 2.0):

```text
--- Credits (keep in the video description) ---
Footage audio: "Após 20 anos da Conferência de Viena, direitos humanos são mais importantes do que nunca, diz ONU" by ONU Brasil, CC BY 3.0, via Wikimedia Commons (excerpt 119.22-128.87 s, speech-cleaned with DeepFilterNet)
--- end credits ---

Credits
Quotes: Norwegian Nobel Committee, press release, 9 October 2026,
  https://www.nobelprize.org/prizes/peace/2026/press-release/
Prize data: Nobel Prize API (api.nobelprize.org), CC0. No endorsement by Nobel Prize Outreach or the Norwegian
  Nobel Committee is implied.
Footage: "Após 20 anos da Conferência de Viena, direitos humanos são mais importantes do que nunca, diz ONU",
  ONU Brasil / UN Human Rights (2013), CC BY 3.0 Unported, via Wikimedia Commons; excerpts, English captions ours.
Photo: "U.S. Ambassador Betty E. King, Reverend Jesse Jackson, High Commissioner Navi Pillay" (21 March 2012),
  U.S. Mission photo by Eric Bridiers, United States Mission Geneva, CC BY 2.0, via Wikimedia Commons; cropped.
Data: Uppsala Conflict Data Program (ucdp.uu.se), CC BY 4.0. UCDP Conflict Termination Dataset v.4 2024: Kreutz,
  Joakim (2010) How and When Armed Conflicts End: Introducing the UCDP Conflict Termination Dataset. Journal of
  Peace Research 47(2): 243-250. UCDP Peace Agreement Dataset 22.2: Pettersson, Therese; Stina Högbladh & Magnus
  Öberg (2019) Organized violence, 1989-2018 and peace agreements. Journal of Peace Research 56(4); codebook:
  Högbladh, Stina (2022) UCDP Peace Agreement Dataset Codebook v 22.1.
Court record: ICTR judgments (Akayesu 1998; the Media case 2003; appeals 2001 and 2007), unictr.irmct.org; cited,
  not reproduced.
Music: "Holberg Suite, Op. 40 - IV. Air" (Grieg), United States Marine Band (Marine Chamber Orchestra, cond. Jason K. Fettig), public domain. Voice: synthetic, Kokoro-82M (bf_isabella), Apache-2.0.
Educational demos made to show an open-source tool. Not research.
```

Made with [showtime](https://github.com/FavioVazquez/showtime).

## What it says, and where each fact comes from

Every factual sentence is a row of the [claims ledger](../CLAIMS.md) (ids in the last column): P01 to P60 are the prize, her career, the court record and the committee's words; P61 to P84 are the toys' numbers, each equal to a field of the toy's results JSON; P85 to P95 are the footage, the photo, the credits and our one bridge. Times are when the voice starts each beat.

| Time | Scene | Narration (and what is on screen) | Claims |
|---|---|---|---|
| 0:00 | 1 open | The Peace Prize went to Navi Pillay. The committee names two things: peace and international law. Left, the courtroom. Right, the field, where conflicts end. (On screen: "Navi Pillay", "Nobel Peace Prize 2026", the citation quoted and credited to the Norwegian Nobel Committee; 507 dots, one per conflict ending.) | P01, P02, P32, P31, P61 |
| 0:11 | 2 Durban | Born in Durban in 1941, she opened her own law firm in 1967. The committee cites her early work defending Nelson Mandela. (Timeline ticks "Durban, 1941" and "1967 · her own law firm"; the committee's sentence quoted in full, credited.) | P19, P22, P21 |
| 0:21 | 3 Rwanda | In 1998, at the Rwanda tribunal, she was one of three judges who found that rape and sexual violence can be genocide. The committee says her influence was a significant factor. ("Rwanda tribunal (ICTR) · judge from 1995 · President from 1999"; the card "Prosecutor v. Akayesu · 2 September 1998" with the three judges, Laïty Kama presiding; "Rape and sexual violence can constitute genocide"; the committee's words quoted.) | P27, P45, P46, P43 |
| 0:33 | 4 the Media case | In 2003 she presided over the Media case: three men tied to a radio station, a party and a newspaper. All three were convicted of inciting genocide; on appeal, several convictions were reversed; the sentences became 30 to 35 years. (Card "The Media case · 3 December 2003", Navanethem Pillay presiding, with Erik Møse and Asoka de Zoysa Gunawardana; tags RTLM radio, CDR party, Kangura newspaper; verdict and appeal on one card: "sentences 30, 32 and 35 years".) | P52, P53, P54, P56 |
| 0:51 | 5 how conflicts end | On the right, Uppsala's data record five hundred and seven conflict endings, from 1946 to 2023. One in four ended in a peace agreement or a ceasefire. More of them now simply fade out. Yet among clear outcomes, since 1990, most are agreements or ceasefires. (Decade columns of dots; "Agreement or ceasefire: 25.0 % of all endings"; "Fading out: 17.4 % (1940s) → 65.0 % (2010s)", "fighting fell below 25 battle deaths a year"; "at least 61.0 % of clear endings in every complete decade since 1990", "clear ending = agreement, ceasefire or victory"; source line with "2020s incomplete: 61 conflicts still active in 2024".) | P61, P62, P63, P64, P65, P66, P67, P68, P79, P60, P93 |
| 1:10 | 6 the commissioner | Then came the International Criminal Court, and six years as United Nations High Commissioner for Human Rights. ("ICC judge · 2003-2008"; the 2012 photo with "UN High Commissioner for Human Rights · 2008-2014".) | P29, P30, P87 |
| 1:18 | 6 her voice | Her own words, from the 2013 footage, with our English caption: "That rights are indivisible. We need civil and political rights as much as we need economic, social and cultural rights." (Source tag "ONU Brasil / UN Human Rights · 2013 · CC BY 3.0".) | P85, P86 |
| 1:28 | 7 do agreements hold | Uppsala also lists three hundred and seventy-four peace agreements, signed from 1975 to 2021. They come from seventy-two groups of linked conflicts, so they aren't three hundred and seventy-four separate tests. Where the fighting went quiet, about half were still quiet five years later. The data can't say whether any type of agreement causes peace. ("374 peace agreements · signed 1975-2021"; "72 groups of linked conflicts"; "52.3 % of the 352 that went quiet were still quiet at 5 years", "95 % interval 37.4-68.1 % (allows for linked conflicts) · 22 never went quiet by 2024"; the curve from the first quiet year and the three type curves close together; source line "the clock starts at the first year below 25 battle deaths".) | P72, P73, P74, P75, P76, P77, P78, P79, P80, P93 |
| 1:51 | 8 today | In the committee's words, the greatest powers have often evaded responsibility. Since 2019 she has sat at the International Court of Justice, chosen as a judge for one case. The committee writes: the judges, those who guard the thin red line between order and chaos, as these same judges are sanctioned, and their institutions are attacked. (Three beats on plain ground, each alone: the first quote; the card "International Court of Justice · judge ad hoc since 2019 · chosen by The Gambia · The Gambia v. Myanmar"; the second quote. The right room stays dark.) | P34, P31, P42, P35 |
| 2:15 | 9 together | One room records what courts did; the other, how conflicts end. The committee joins them in one line: Peace requires justice. ("Peace requires justice." / "Norwegian Nobel Committee · 9 October 2026".) | P95, P40, P01 |
| 2:28 | 10 end card | This film was made with showtime, a local video studio for your coding agent. (The lab's address and the credits above.) | P91, P92, P94, P88, P89, P90, P18 |

### The film's own claim list, mapped to the ledger

The film was planned with its own list of claim ids (the draft ledger's numbers). Screen and voice wording shorten a row, never extend it. This is how that list maps to the [ledger](../CLAIMS.md):

| Film id | Ledger |
|---|---|
| P01 | P01 |
| P02 | P02 |
| P31 | P31 |
| P32 | P32 |
| P19 | P19 |
| P22 | P22 |
| P21 | P21 |
| P27 | P27 |
| P45a | P45 |
| P45b | P46 |
| P43 | P43 |
| P45h | P52 |
| P45i | P53 |
| P45j | P54 |
| P45l | P56 |
| P29 | P29 |
| P30 | P30 |
| P34 | P34 |
| P42 | P42 |
| P35 | P35 |
| P40 | P40 |
| P18 | P18 |
| P52 | P60 |
| H01 | P61 |
| H02 | P62 |
| H03 | P63 |
| H04 | P64 |
| H05 | P65 |
| H06 | P66 |
| H07 | P67 |
| H08 | P68 |
| H09 | P69 |
| A01 | P72 |
| A02 | P73 |
| A03 | P74 |
| A04 | P75 |
| A05 | P76 |
| A06 | P77 |
| A07 | P78 |
| A08 | P79 |
| F01 | P85 |
| F03 | P86 |
| F04 | P87 |
| F06 | P88 |
| F07 | P89 |
| F08 | P90 |
| S01 | P91 |
| S02 | P92 |
| S03 | P93 |
| S04 | P94 |
| B01 | P95 |

## Honest notes

- **The two cases.** The committee's press release says one case brought both breakthroughs. The court record shows rape and sexual violence as genocide in Akayesu (1998), where she was one of three judges and Laïty Kama presided, and media incitement in the Media case (2003), which she presided. The film states the record in our voice and quotes the committee only where it speaks of "her influence"; it never says which case the committee meant, and it uses no "first" of its own (P43, P44, P45-P107, P102-P104).
- **The Media case appeal.** In 2007 several convictions were reversed and the sentences cut to 30, 32 and 35 years; the film says so on the same card as the 2003 verdict (P56).
- **Her ICJ seat.** She is a judge ad hoc, chosen by The Gambia for one case, not one of the Court's elected members; the film gives no stage or outcome of the case (P31, P99).
- **The committee's lines** about the greatest powers and about sanctioned judges are quoted as the committee wrote them, credited, on plain ground, with no image, music hit or data of ours beside them, and never next to her photo (P34, P35, P42).
- **The conflict data** count every armed conflict from 25 battle-related deaths a year, so the film says "conflicts", not "wars". The 2020s are incomplete: 61 conflicts were still active in 2024 (P79, P68). The share of all endings that were an agreement or ceasefire shows no steady rise (P69, P70); the film shows the bars without calling them a rise or a fall and places no committee line next to them.
- **"About half" holding** is counted from the first quiet year after signing; counted from the signature, 31.5 % held at 5 years, because fighting that never stopped counts as resumed (P75, P83). The 374 agreements are not independent, so the interval allows for 72 groups of linked conflicts (P73, P76). The data cannot rank the agreement types (P78).
- **Her words in the footage** come from a machine transcript, checked against the frames with her on camera; the caption leaves out a false start (P86).
- **What the film leaves out on purpose:** the Nobel illustration of the laureate, nomination numbers, anecdotes from a single outlet, and any conflict, country or party from the data (P105-P107).
