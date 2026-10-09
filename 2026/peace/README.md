# Peace 2026: two rooms, courts and agreements

> **Educational demos made to show an open-source tool. Not research.**

**Status:** facts: done · claims ledger: done (checked 2026-10-09) · how conflicts end: done · do agreements hold: done · independent review of both toys: done, findings fixed · page: done · video: done

The Norwegian Nobel Committee awarded the Nobel Peace Prize 2026 to Navanethem "Navi" Pillay on 9 October 2026, "for her efforts to promote peace and international law". (P01, P02) She is the sole laureate and the 21st woman to receive the Peace Prize. (P03, P11) Back to the [front page](../../README.md).

Numbers like (P01) point to rows in [CLAIMS.md](CLAIMS.md), where each sentence has its source. Rows P61 to P84 are our toys' numbers, each equal to a field of the toy's results JSON.

**Two rooms.** This folder looks at the prize in two rooms, as the film does. In the first, the courtroom: her career and the court record of the cases she sat on, each from the judgments themselves. In the second, the field: what open conflict data say about how armed conflicts end and whether peace agreements hold. The committee's words are always quoted as its own, credited; our data are never placed as a verdict on them. No conflict, country or party from the data is named.

## The story in four steps

1. **The lawyer.** Born on 23 September 1941 in Durban, she founded her own law firm in 1967. (P19, P22) The committee cites "her early work defending Nelson Mandela and others who stood up against apartheid". (P21)
2. **The judge.** She was a judge of the International Criminal Tribunal for Rwanda from 1995, and its President from 4 June 1999. (P27) In *Prosecutor v. Akayesu* (judgment 2 September 1998) she was one of three judges, with Laïty Kama presiding; the Chamber found that rape and sexual violence constitute genocide when committed with intent to destroy a group. (P45, P46) The committee says "her influence was a significant factor". (P43) In the Media case (judgment 3 December 2003) she presided; the Chamber convicted a founder of the radio station RTLM, a founding member of the CDR party and the founder of the newspaper Kangura, and on appeal in 2007 several convictions were reversed and the sentences reduced to 30, 32 and 35 years. (P52, P53, P54, P56)
3. **The courts after Rwanda.** She was a judge of the International Criminal Court from 2003 until 31 August 2008, then UN High Commissioner for Human Rights from 1 September 2008 to 31 August 2014. (P29, P30) Since 2019 she has sat as a judge ad hoc of the International Court of Justice, chosen by The Gambia, in the Genocide Convention case it brought against Myanmar. (P31)
4. **The field.** UCDP records 507 endings of armed-conflict episodes from 1946 to 2023; 127 of them, 25.0 %, were a peace agreement or a ceasefire agreement. (P61, P63) More conflicts now fade out: low activity was 17.4 % of endings in the 1940s and 65.0 % in the 2010s. (P64) Among endings with a clear outcome, an agreement or ceasefire was at least 61.0 % in every complete decade since 1990, against at most 38.5 % in each decade before; the 2020s are 55.6 % and incomplete. (P66, P67, P68) Of 374 peace agreements signed from 1975 to 2021, 352 were followed by a quiet year; counted from it, 52.3 % were still quiet 5 years on (95 % interval 37.4 to 68.1, allowing for 72 groups of linked conflicts), and the median is 6 years. (P72, P73, P74, P75, P76, P81)

The committee's own line joins the two rooms: "Peace requires justice." (P40)

## The stations

Four stops, as in a museum. Each says what it is made of and whether it is ready.

<table>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-endings.svg" alt="Icon: bars by decade with a dashed line rising above them" width="72"></td>
    <td valign="top"><b>1. How conflicts end</b> <i>(ready)</i><br>
    How the 507 armed-conflict episodes in the UCDP Conflict Termination Dataset ended, decade by decade, from 1946 to 2023: across all endings the share that was a peace agreement or a ceasefire shows no steady rise (it rose to 35.5 % in the 2000s, then fell to 17.5 % in the 2010s); more conflicts fade out; and among clear outcomes, agreements and ceasefires gained. With Wilson intervals, trend tests and the censoring of the 2020s. Folder: <a href="how-conflicts-end/README.md">how-conflicts-end</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-hold.svg" alt="Icon: a falling step curve with a dot marking one point on it" width="72"></td>
    <td valign="top"><b>2. Do agreements hold?</b> <i>(ready)</i><br>
    Kaplan-Meier curves of how long the 374 agreements of the UCDP Peace Agreement Dataset stayed quiet: counted from the first quiet year, 52.3 % held at 5 years; counted from the signature, 31.5 %, because fighting that never stopped counts as resumed. Intervals from a cluster bootstrap over 72 groups of linked conflicts. The data cannot rank full, partial and process agreements. Folder: <a href="do-agreements-hold/README.md">do-agreements-hold</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-page.svg" alt="Icon: a web page with a slider" width="72"></td>
    <td valign="top"><b>3. The interactive page</b> <i>(ready)</i><br>
    Guess first, then see: what share of conflict endings were an agreement or a ceasefire, with a switch to clear outcomes only; and what share of agreements were still quiet five years on, with a switch between the two clocks. One file, no network, light and dark. <a href="https://faviovazquez.github.io/nobel-2026-lab/2026/peace/page/">Try it online</a>. Folder: <a href="page/README.md">page</a>.</td>
  </tr>
  <tr>
    <td width="96" valign="top"><img src="../../assets/icons/station-video.svg" alt="Icon: a video frame with a play button" width="72"></td>
    <td valign="top"><b>4. The video</b> <i>(ready)</i><br>
    A 2:35 explainer in two rooms side by side: on the left her courtroom, from Durban to the Rwanda tribunal, the ICC, the UN and the ICJ, with a short excerpt of her own voice; on the right the field, how conflicts end and whether agreements hold. It asks no questions. <a href="video/exports/nobel-2026-peace.mp4">Watch the MP4</a>. Every fact in it comes from the <a href="CLAIMS.md">claims ledger</a>. Made with <a href="https://github.com/FavioVazquez/showtime">showtime</a>. Files and how it was made: <a href="video/README.md">video</a>.</td>
  </tr>
</table>

## The pictures

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="how-conflicts-end/results/agreement_share_dark.png">
    <img alt="Two panels by decade, 1940s to 2020s, each with a 95 per cent band. Left: the share of all conflict endings that were a peace agreement or ceasefire, between about 16 and 36 per cent with no steady rise, and a dashed line for low activity (faded out) climbing from about 17 per cent to about 65 per cent. Right: the same share among endings with a clear outcome, under 40 per cent in every decade before 1990 and above 60 per cent in every complete decade since; the incomplete 2020s at about 56 per cent." src="how-conflicts-end/results/agreement_share_light.png" width="720">
  </picture>
</p>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="do-agreements-hold/results/km_by_type_dark.png">
    <img alt="Kaplan-Meier step curves of the share of peace agreements with no fighting yet in the same conflict, over 20 years. Left: full, partial and process agreements counted from the first quiet year, with overlapping bands, between about 49 and 59 per cent at 5 years. Right: all agreements three ways: the main clock near 52 per cent at 5 years, the main clock without the settled-late agreements a little higher, and the strict clock from the signing year, which drops below 50 per cent in the first year and is near 32 per cent at 5 years." src="do-agreements-hold/results/km_by_type_light.png" width="720">
  </picture>
</p>

## What is real, and what is ours

<table>
  <tr>
    <th width="50%">Real</th>
    <th width="50%">Ours</th>
  </tr>
  <tr>
    <td valign="top">The prize, the date, the citation and the committee's words, quoted and credited. Her career and the court record, from the ICTR's judgments, UN documents and the ICJ's reports. Every sentence is sourced in <a href="FACTS.md">FACTS.md</a> and checked in <a href="CLAIMS.md">CLAIMS.md</a>.</td>
    <td valign="top">The way the court record is said: in our voice, with no "first" of our own, no "her ruling" (the Chambers decided unanimously) and no claim about which case the committee meant.</td>
  </tr>
  <tr>
    <td valign="top">The UCDP datasets (CC BY 4.0): how each conflict episode ended, and the peace agreements with their types and years, as UCDP coded them.</td>
    <td valign="top">The groupings and the clocks: agreement and ceasefire counted together, "clear outcome", the first-quiet-year clock, the groups of linked conflicts. Our choices, each stated in the toy's README. Correlation, not cause.</td>
  </tr>
  <tr>
    <td valign="top">Her words in the film's footage excerpt (ONU Brasil, 2013, CC BY 3.0) and the 2012 photo (U.S. Mission Geneva, CC BY 2.0), credited.</td>
    <td valign="top">The English captions of the footage, the drawings, the charts and the narration.</td>
  </tr>
</table>

## Folder map

| Path | What it is | Status |
|---|---|---|
| [FACTS.md](FACTS.md) | The sourced fact sheet: the prize, its history from the Nobel API, her career, the committee's own words, the two Rwanda tribunal cases from the judgments, the data the toys use, and what not to say | done |
| [CLAIMS.md](CLAIMS.md) | The ledger of claims we use, with sources and the check date: the prize and her career (P), the toys' numbers with their JSON fields, the film's footage, photo and credits, and the rows that stop a sentence | done |
| [how-conflicts-end](how-conflicts-end/README.md) | Toy 1: how armed-conflict episodes ended, by decade, 1946-2023 | done |
| [do-agreements-hold](do-agreements-hold/README.md) | Toy 2: how long peace agreements stayed quiet, two clocks, linked conflicts allowed for | done |
| [review](review/REVIEW.md) | The independent review of both toys, its own checks and numbers; its findings are fixed in the toys | done |
| [page](page/README.md) | Guess first, then see ([online](https://faviovazquez.github.io/nobel-2026-lab/2026/peace/page/)) | done |
| [video](video/README.md) | A 2:35 explainer in two rooms ([the MP4](video/exports/nobel-2026-peace.mp4)), its poster and captions, the credits, and which claims it uses | done |

## Rerun and check

Everything runs on an ordinary laptop processor in seconds, with no GPU and no accounts. Each folder's README has its exact steps.

- **How conflicts end**, from `2026/peace/how-conflicts-end/` ([steps](how-conflicts-end/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m ends.run_all
  ```

- **Do agreements hold?**, from `2026/peace/do-agreements-hold/` ([steps](do-agreements-hold/README.md)):

  ```bash
  python3.11 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt && python -m holds.run_all
  ```

- `python -m ends.fetch_data` and `python -m holds.fetch_data` download the pinned UCDP files (network) and check their sha256; without them, the raw-file tests are skipped.
- **The page** needs nothing: open `2026/peace/page/index.html` in a browser. `python3 -m page.run_all` from `2026/peace/` rebuilds its data from the two toys and refreshes its screenshots ([steps](page/README.md)).
- Tests: `python -m pytest -q tests` in each toy folder and in `page/`.

These are teaching demos. They count endings and agreements as UCDP coded them; they do not say why a conflict ended or what any agreement, court or person caused.

## Glossary

| Term | In plain English |
|---|---|
| ICTR | The International Criminal Tribunal for Rwanda, a UN court that tried those responsible for the genocide in Rwanda. Its records are kept by the IRMCT. |
| ICC | The International Criminal Court, a permanent court for genocide, crimes against humanity and war crimes. |
| ICJ | The International Court of Justice, the UN's court for disputes between states. |
| Judge ad hoc | A judge chosen by one party for one case at the ICJ, beside the Court's 15 elected members. |
| Trial chamber | The bench of judges who hear a case and give the judgment; an appeals chamber reviews it. |
| UCDP | The Uppsala Conflict Data Program, which records armed conflicts worldwide. It counts an armed conflict from 25 battle-related deaths in a year. |
| Episode | A run of active years of one conflict; a conflict can have several episodes. |
| Low activity | UCDP's outcome when the fighting falls below 25 battle-related deaths a year with no agreement and no victory. |
| Kaplan-Meier | A way to draw how many items "survive" over time when some are still being watched when the data stop. |
| Cluster bootstrap | Resampling whole groups of linked cases, so the interval does not pretend they are independent. |
