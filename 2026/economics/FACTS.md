# Economic Sciences 2026: Robert E. Hall and Michael Woodford fact sheet

> Educational demos made to show an open-source tool. Not research, and not economic or policy advice.

This is the sourced fact sheet behind the economics folder. Every statement names where it comes from. It was compiled
on 2026-10-12, the day of the announcement. Primary sources first: nobelprize.org (the press release, the popular
information, the scientific background and the summary page) and the Nobel Prize API v2.1. Every quote below is at
most 15 words. The sentences we actually use in the film, the page and the READMEs are listed one by one, with a check
date, in [CLAIMS.md](CLAIMS.md); the ids in brackets (E001, E002, ...) point to that ledger.

Scope: this sheet covers the prize, the two laureates, the work the committee names, what the committee says it
changed and the limits it states. No other sentence of the official pages is used in this folder. The toys' numbers
(US spending data from BEA, and a textbook model) are not facts about the laureates; they are in CLAIMS.md
(sections 20 and 21), each with its own label.

Likeness: no portraits, no medal and no committee illustrations are used anywhere in this folder, the film or the page
(E013, E014). The film draws its own diagrams.

Source keys:
- [PR] https://www.nobelprize.org/prizes/economic-sciences/2026/press-release/ (Royal Swedish Academy of Sciences, 12 October 2026)
- [POP] https://www.nobelprize.org/prizes/economic-sciences/2026/popular-information/ ("Microfoundations deliver macro
  insights", 7 pages; PDF page = printed page)
- [SB] https://www.nobelprize.org/prizes/economic-sciences/2026/advanced-information/ ("Microeconomic foundations of
  macroeconomic stabilization", 57 pages; page numbers in this folder are PDF pages, the printed number is the PDF page minus 2)
- [SUM] https://www.nobelprize.org/prizes/economic-sciences/2026/summary/
- [API] https://api.nobelprize.org/2.1/nobelPrize/eco/2026 ;
  https://api.nobelprize.org/2.1/nobelPrizes?nobelPrizeCategory=eco
- [ECO] https://www.nobelprize.org/prizes/economic-sciences/ (the "Prize in Economic Sciences" page, saved before the announcement)
- [TERMS] https://www.nobelprize.org/about/terms-of-use-for-api-nobelprize-org-and-data-nobelprize-org/
- [BEA-FAQ] https://www.bea.gov/help/faq/147 (BEA: pages are in the public domain; citation "Source: U.S. Bureau of Economic Analysis" appreciated)
- [BEA-BULK] https://apps.bea.gov/national/Release/TXT/ ;
  https://apps.bea.gov/national/Release/TXT/NipaDataQ.txt ;
  https://apps.bea.gov/national/Release/TXT/SeriesRegister.txt
- [BEA-SCHED] https://www.bea.gov/news/schedule/full (BEA's release schedule)
- [CM89] https://www.nber.org/chapters/c10965 (Campbell and Mankiw 1989)
- [DOIs given by the toy READMEs] https://doi.org/10.1257/jel.37.4.1661 (Clarida, Galí, Gertler 1999) ;
  https://doi.org/10.2307/1912186 (Blanchard, Kahn 1980) ; https://doi.org/10.1257/aer.20150063 (McKay, Nakamura,
  Steinsson 2016) ; https://doi.org/10.1086/724214 (Del Negro, Giannoni, Patterson 2023) ;
  https://doi.org/10.1016/s0304-3932(02)00144-7 (Bullard, Mitra 2002)
- [SATIE] https://commons.wikimedia.org/wiki/File:Erik_Satie_-_gymnopedies_-_la_1_ere._lent_et_douloureux.ogg
- [KOKORO] https://huggingface.co/hexgrad/Kokoro-82M
- [SHOWTIME] https://github.com/FavioVazquez/showtime (the open-source video studio the film is made with; also the home of these toys)

## 1. Who and what

- On 12 October 2026 the Royal Swedish Academy of Sciences awarded the Sveriges Riksbank Prize in Economic Sciences in
  Memory of Alfred Nobel 2026 to Robert E. Hall and Michael Woodford (PR; SUM; API) [E001].
- Motivation: "for microeconomic foundations of macroeconomic stabilisation" (PR; SUM; POP p.7; API). The scientific
  background spells it "stabilization" in its title [E002, E003].
- The prize is 12 million Swedish kronor, shared equally (PR; SUM; API) [E004].
- Hall: born 1943 in Palo Alto, California; PhD MIT 1967; professor at Stanford University. Woodford: born 1955 in
  Chicopee, Massachusetts; PhD MIT 1983; professor at Columbia University (PR; POP p.7; API) [E005, E006].
- John Hassler is chair of the Committee for the Prize in Economic Sciences (PR) [E007]. The committee says the two
  contributions were made independently, with years between them (SB PDF p.5) [E009].
- Not used: birthdays (E010), other biography (E011), ages and rankings (E012).

## 2. Core contribution, in the committee's plain words

- Models rebuilt from the bottom up: the economy's totals come from the decisions of households and firms, which look
  forward (PR; POP pp.1-2; SB PDF p.4) [E036, E037].
- Hall: if people spend according to what they expect to earn, changes in spending only follow news, and news cannot be
  forecast; the test is whether anything forecasts changes in consumption (POP p.3; SB PDF pp.5, 17-19) [E039, E040].
  The scientific background calls the 1978 paper "a 'Eureka' moment of sorts" (SB PDF p.5) [E045].
- Hall and Mishkin 1982: food spending of 2,309 US families, 1969 to 1975; about 20 per cent of consumption moved one
  for one with current income, the other 80 per cent followed the theory (SB PDF pp.24-25) [E053, E055].
- Woodford: the 2003 book "Interest and Prices" sets out a complete New Keynesian model; the committee calls it
  "a kind of laboratory for policymakers" (POP p.4) [E063, E064, E066].
- The simplest model has three equations and three variables: the output gap, inflation and the interest rate; the third
  is the central bank's rule (SB PDF pp.7, 29-31) [E069-E072].
- Sticky prices, forward-looking firms, the natural rate (Wicksell, 1898) and the output gap: E081, E082, E089-E099.
- Precursors and co-authors (never imply the pair did it alone): Julio Rotemberg (died 2017), Taylor, Calvo, Lucas,
  Kydland and Prescott, and others (SB PDF pp.5-6, 11-12, 28) [E119-E130].

## 3. Papers named by the committee

- Hall, R. E. (1978), "Stochastic implications of the life cycle-permanent income hypothesis: theory and evidence",
  Journal of Political Economy 86(6), 971-987 (SB PDF p.53) [E038].
- Hall, R. E. and F. S. Mishkin (1982), "The sensitivity of consumption to transitory income: estimates from panel data
  on households", Econometrica 50(2), 461 (SB PDF p.53) [E052].
- Woodford, M. (2003), Interest and Prices: Foundations of a Theory of Monetary Policy, Princeton University Press (SB
  PDF pp.6, 57) [E063]; Woodford (2005) on central bank communication (SB PDF pp.49, 57) [E110].
- Del Negro, Giannoni and Patterson (2023) on the forward guidance puzzle (SB PDF pp.48, 53) [E115].
- The toys also cite Campbell and Mankiw (1989), Galí (2015) and others; those citations are in CLAIMS.md section 22.

## 4. What the committee says it changed

- New Keynesian models are used by central banks and finance ministries around the world (PR; POP pp.1, 6) [E132].
- Forward guidance, proposed by Woodford and others as an extra tool when rates could not be cut further (SB PDF p.40)
  [E111]; the committee dates the US near-zero period "usually" 2008 to 2015 [E112].
- Fiscal and monetary policy can be analysed together (SB PDF p.7) [E080].
- Success claims by the committee (E138, E139, E142 and the charged lines E178-E197) are used only as credited quotes,
  next to its own caveat that it is "hard to prove beyond reasonable doubt" (SB PDF p.50) [E145].

## 5. Limits the committee itself states

- Judging whether the models helped is hard; the framework is for everyday stabilisation and is "not designed to
  prevent shocks from occurring in the first place" (SB PDF p.50) [E144-E147].
- Expectations that are consistent with the model, anchored inflation expectations and the linear solution are
  assumptions; rare events are hard to capture (SB PDF pp.47-48) [E150, E151, E153].
- Forward guidance puzzle: in the simple model, promises about the far future have implausibly strong effects today; no
  consensus fix (SB PDF p.48) [E115, E116].
- "Not the final word" (POP p.6) [E155]; the analysis can point to many responses, "one of which is laissez-faire" (SB
  PDF p.49) [E156].

## 6. Prize history (Nobel API, CC0; our count)

Label every number "our count from the Nobel Prize API (CC0)". Established by Sveriges Riksbank in 1968, first awarded in 1969
to Ragnar Frisch and Jan Tinbergen (ECO; API) [E015, E016]. 58 prizes from 1969 to 2026, 101 laureates, none twice,
none an organisation; 26 prizes to one laureate, 21 shared by two and 11 by three; three women: Elinor Ostrom (2009),
Esther Duflo (2019) and Claudia Goldin (2023) (API) [E017-E020]. The facts page saved before the announcement says 57
prizes and 99 laureates, which fits 57 + 1 and 99 + 2 [E021]. The API's 2022 award date is a data error and is never
printed [E022]. The API data are CC0 (TERMS) [E024].

## 7. Data used by the toys

- US national accounts from the U.S. Bureau of Economic Analysis (NIPA bulk files NipaDataQ.txt and
  SeriesRegister.txt), release of 30 September 2026, downloaded 2026-10-12, quarterly data to 2026Q2, pinned by sha256;
  BEA states its web information is in the public domain; credit "Source: U.S. Bureau of Economic Analysis"
  (BEA-FAQ; BEA-BULK; BEA-SCHED) [CLAIMS.md section 20].
- The set-the-rate toy uses no data: a textbook model with a calibration of the kind in Galí (2015), ch. 3, labelled
  "Textbook model, illustrative calibration" [E176].

## 8. Media and credits for the film "The lab with three equations"

- Music: Erik Satie, Gymnopédie No. 1, performed by Robin Alciatore for Musopen, public domain (CC-PDDC); Wikimedia
  Commons file page (SATIE).
- Voice: bm_george from Kokoro-82M, licence Apache-2.0 (KOKORO).
- Made with showtime, an open-source video studio (SHOWTIME). Footer: "Educational demo, not research".
- Likeness: none; the committee's illustrations by Johan Jarnestad and the Nobel laureate portraits and medal are not used.

## 9. Do-not-use list

E010-E014 (birthdays, other biography, ages, portraits and medal, committee illustrations); E051 (Hall "proved" it); E061
and E062 (80 per cent of households today; later estimates presented as Hall and Mishkin's); E075 (equation numbering);
E100 (the output gap "introduced" by Woodford); E118 (inverted forward-guidance sentence); E131 ("invented" or "did it
alone" or "worked together"); E143 (models "prevented" a crisis); E158 (inflation-shock start year); E165-E175
(firsts and rankings, forecasts, prediction lists, "Nobel" in titles, public-debate slogans, insinuating juxtapositions,
fiscal-versus-monetary claims, political black-swan example, unreliable references, stray notes).
