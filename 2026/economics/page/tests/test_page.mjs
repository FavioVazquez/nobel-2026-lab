// Headless-Chromium check of the Economics page. Educational demos made to show an open-source tool. Not research.
// Opens index.html from file:// at 360, 768 and 1440 px in light and dark (and with reduced motion), makes both slider
// guesses and all three button guesses, and checks what a visitor would see. With --shots it refreshes screenshots/,
// with --og og.jpg.
//   PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs [--shots] [--og]
//   (from 2026/economics/page/; PLAYWRIGHT_CORE=/path/to/playwright-core/index.mjs overrides where playwright is found)
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const PW = process.env.PLAYWRIGHT_CORE || path.join(os.homedir(), ".showtime/node/node_modules/playwright-core/index.mjs");
const { chromium } = await import(pathToFileURL(PW).href);
const PAGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PY = process.env.PYTHON || "python3";
const SHOTS = process.argv.includes("--shots"), OGMODE = process.argv.includes("--og");
const WIDTHS = [360, 768, 1440], THEMES = ["light", "dark"];
let passed = 0; const failed = [];
function check(ok, what) { if (ok) passed++; else { failed.push(what); console.log("FAIL " + what); } }

const readData = (file) => { const s = fs.readFileSync(file, "utf8"); return JSON.parse(s.slice(s.indexOf("= ") + 2, s.trimEnd().lastIndexOf(";"))); };
const D = readData(path.join(PAGE, "data.js"));
const NB = "\u00a0", MINUS = "\u2212";
const p1 = (x) => (x < 0 ? MINUS : "") + Math.abs(Number(x)).toFixed(1);
const pct = (x) => p1(x) + NB + "%";
const rng = (c) => p1(c[0]) + " to " + p1(c[1]) + NB + "%";
const bench = (x) => (x == null ? "zero" : Number.isInteger(x) ? x + NB + "%" : pct(x));
const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");
// named central banks and advice words: never in the page's own text (a data credit in the footer may name its source)
const BANKS = /federal reserve|riksbank|european central bank|\bECB\b|bank of england|bank of japan|people's bank|bundesbank|banxico/i;
const ADVICE = /\bshould\b|\bought to\b|\bthe right move\b|\bno (other )?(viable )?alternative/i;
// part one is framed as the committee frames it: no verdict on Hall's hypothesis
const VERDICT = /\bwrong\b|\bfail(s|ed|ure)?\b|\bconfirm(s|ed)?\b|\brefut(e|es|ed)\b|\bdisprov(e|es|ed)\b|\bdebunk|\bproves?\b/i;

// every number a visitor can read must be a number of data.js (or an axis tick, or their own guess)
const allowed = new Set(["0", "40", "60", "30", "70"]);
(function walk(v) {
  if (typeof v === "number") { for (const s of [String(v), v.toFixed(1), v.toFixed(3), Math.abs(v).toFixed(1), Math.abs(v).toFixed(3), String(Math.abs(v))]) allowed.add(s); }
  else if (typeof v === "string") { for (const t of v.match(/\d+(?:\.\d+)?/g) || []) allowed.add(t); }
  else if (v && typeof v === "object") { for (const k in v) { walk(k); walk(v[k]); } }
})(D);

check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html) && !/@import|url\(["']?https?:/i.test(html), "no external scripts, styles, fonts or images");
check(html.includes('href="https://github.com/FavioVazquez/showtime"'), "Made with showtime link");
check(/<meta property="og:image" content="[^"]+og\.jpg"/.test(html), "og:image");
check(!/nobel/i.test((html.match(/<title>(.*?)<\/title>/) || [])[1] || "x") && !/nobel/i.test((html.match(/og:title" content="([^"]*)"/) || [])[1] || "x"), "the title does not say Nobel");

const browser = await chromium.launch();
async function open(url, { width = 1440, height = 900, theme = "light", reduced = false } = {}) {
  const ctx = await browser.newContext({ viewport: { width, height }, colorScheme: theme, deviceScaleFactor: 1, reducedMotion: reduced ? "reduce" : "no-preference", hasTouch: width < 500 });
  const page = await ctx.newPage();
  const errors = [], requests = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("requestfailed", (r) => errors.push("request failed: " + r.url()));
  page.on("request", (r) => { if (!r.url().startsWith("file://") && !r.url().startsWith("data:")) requests.push(r.url()); });
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  return { ctx, page, errors, requests };
}
const URL0 = pathToFileURL(path.join(PAGE, "index.html")).href;
const S = D.spend, R = D.rate, CL = D.curve_label;
const panels = async (page, id) => page.locator(`#${id} svg`).count();

for (const width of WIDTHS) for (const theme of THEMES) {
  const tag = `${width}px ${theme}`, reduced = width === 360 && theme === "dark";
  const { ctx, page, errors, requests } = await open(URL0, { width, theme, reduced });
  const first = await page.evaluate(() => document.body.innerText.trim().split("\n")[0]);
  check(first === D.tag, `${tag}: the label is the first thing on the page`);
  check(await page.evaluate(() => document.documentElement.getAttribute("data-theme")) === theme, `${tag}: theme follows the system`);
  check(await page.isHidden("#prelim") === !D.preliminary, `${tag}: preliminary box only when an input is not final`);
  check(await page.isHidden("#synth") === !S.synthetic, `${tag}: simulated box only when the spending toy is synthetic`);
  check(await page.isDisabled("#a-go") && await page.isDisabled("#b-go"), `${tag}: Reveal waits for a guess`);
  check(await page.isHidden("#a-reveal") && await page.isHidden("#b-reveal") && await page.isHidden("#xa-reveal") && await page.isHidden("#xb-reveal") && await page.isHidden("#xc-reveal"),
    `${tag}: the answers are hidden before the guess`);
  // part one, question a
  await page.fill("#a-guess-input", "40");
  check(await page.isEnabled("#a-go") && (await page.textContent("#a-guess-input-out")).startsWith("40"), `${tag}: Reveal enabled, guess shown`);
  await page.click("#a-go");
  check((await page.textContent("#a-big")) === pct(S.a.answer), `${tag}: spending answer ${pct(S.a.answer)}`);
  check((await page.textContent("#a-verdict")).includes("You guessed 40"), `${tag}: verdict repeats the guess`);
  const order = await page.evaluate(() => [...document.querySelectorAll("#a-reveal > *")].map((e) => e.id || e.className));
  check(order[0] === "a-bridge" && order[1] === "big" && (await page.textContent("#a-bridge")).includes("spend as they earn") && (await page.textContent("#a-bridge")).includes("next question"),
    `${tag}: part one leads with the bridge (households who spend as they earn, the next question), then the number`);
  check(!(await page.textContent("#a-reveal")).match(/Hall's benchmark: /) && await page.isHidden("#a-ci"), `${tag}: no "benchmark: 0" line next to the number (it is under More)`);
  const aci = await page.textContent("#a-ci");
  check((S.a.ci ? aci.includes(rng(S.a.ci)) : true) && aci.includes("Hall's benchmark, where every household looks ahead: " + bench(S.a.benchmark)), `${tag}: interval (if the toy gives one) and Hall's benchmark, under More`);
  check(await page.locator("#a-chart svg > title").count() === 1 && await page.locator("#a-chart svg > desc").count() === 1, `${tag}: spending chart has a title and desc`);
  check(await page.locator("#a-details #a-more li").count() === S.a.more.length && await page.isHidden("#a-more"), `${tag}: secondary numbers folded under More`);
  check((await page.textContent("#a-note")) === (S.roles.a || []).map((i) => i.text).join(" "), `${tag}: the toy's own sentences (INSIGHTS.md), under More`);
  // part one, question b
  await page.fill("#b-guess-input", "60");
  await page.click("#b-go");
  const benchTxt = await page.textContent("#b-bench"), bextra = await page.textContent("#b-extra");
  const quotes = await page.locator("#b-bench q").allTextContents();
  check(await page.locator("#b-bench li").count() === 2 && quotes.every((q) => q.split(/\s+/).length < 15), `${tag}: two benchmark lines, quotes under 15 words`);
  check(!S.b.cm.short || (benchTxt.includes(S.b.cm.short) && S.b.cm.quote.includes(S.b.cm.short) && benchTxt.includes("of income")), `${tag}: Campbell-Mankiw "${S.b.cm.short}" of income`);
  check(!S.b.hm.pct || (benchTxt.includes("about " + S.b.hm.pct + NB + "% of food spending") && benchTxt.includes("committee") && benchTxt.includes(S.b.hm.years.join("-"))), `${tag}: the committee's Hall-Mishkin line, credited, with its sample years`);
  check((!S.b.cm.quote || bextra.includes(S.b.cm.quote)) && (!S.b.hm.quote || bextra.includes(S.b.hm.quote)) && await page.isHidden("#b-extra"), `${tag}: the full quotes under More`);
  const ours = await page.textContent("#b-ours");
  check(!S.b.ours.ci || (ours.includes(rng(S.b.ours.ci)) && ours.includes("range")), `${tag}: our estimate as a range`);
  check(!S.b.ours.weak || (/weak instruments/i.test(ours) && bextra.includes(String(S.b.ours.F))), `${tag}: weak-instrument warning (F under More)`);
  check(!(S.b.ours.ar || []).length || (!ours.includes(rng(S.b.ours.ar[0])) && bextra.includes(rng(S.b.ours.ar[0]))), `${tag}: the Anderson-Rubin set under More`);
  check(!S.control || ((await page.textContent("#b-details #b-control")).includes("Simulated control") && (await page.textContent("#b-control")).includes(pct(S.control.coverage_pct))), `${tag}: simulated control line, under More`);
  check(await page.locator("#b-chart svg > title").count() === 1, `${tag}: range chart has a title`);
  // part two
  await page.click('#xa .choices button[data-v="' + (R.a.correct === "raise" ? "lower" : "raise") + '"]');
  check((await page.textContent("#xa-verdict")).includes("differently"), `${tag}: a wrong pick is told so`);
  await page.click('#xa .choices button[data-v="' + R.a.correct + '"]');
  check((await page.textContent("#xa-verdict")).includes("the model's answer"), `${tag}: the right pick is told so`);
  check((await page.textContent("#xa-say")).includes(String(Math.abs(R.a.rate_impact))), `${tag}: cost-push: the rate on impact`);
  check(await panels(page, "xa-chart") === R.vars.length && await page.locator("#xa-chart polyline").count() === R.vars.length * (R.a.strong ? 2 : 1), `${tag}: cost-push: three panels, two rules each`);
  const pts = (await page.getAttribute("#xa-chart polyline.sel", "points")).trim().split(" ").length;
  check(pts === R.a.base.paths[R.vars[0].key].length, `${tag}: the curve has one point per JSON value`);
  await page.click('#xb .choices button[data-v="' + R.b.correct + '"]');
  check(await page.locator("#xb-details #xb-eig svg circle").count() === R.b.active.moduli.length + R.b.passive.moduli.length && await page.isHidden("#xb-eig"), `${tag}: Taylor principle: every eigenvalue drawn, under More`);
  check(await panels(page, "xb-chart") === R.vars.length && (await page.textContent("#xb-cap")).includes("none is drawn"), `${tag}: Taylor principle: one path drawn, the many not`);
  await page.click('#xc .choices button[data-v="' + R.c.correct + '"]');
  check(await panels(page, "xc-chart") === R.vars.length && await page.locator("#xc-chart line.mark").count() === R.vars.length, `${tag}: forward guidance: three panels with the promised quarter`);
  const pz = (await page.textContent("#xc-puzzle")).trim(), xcx = await page.textContent("#xc-extra");
  check(await page.isVisible("#xc-puzzle") && pz.split(/[.;:]\s/).length === 1 && pz.endsWith(".") && (await page.textContent("#xc-puzzle-src")).includes(R.c.puzzle.published_version.replace(/\),.*$/, ")")),
    `${tag}: forward-guidance puzzle box: one sentence and the citation`);
  check(xcx.includes(((R.roles.puzzle || [])[0] || {}).text || R.c.puzzle.text) && xcx.includes("not a measurement") && xcx.includes(R.c.puzzle.published_version) && await page.isHidden("#xc-extra"), `${tag}: the puzzle's numbers under More`);
  // the ten-second rule: what a reveal shows before "More on this answer" is short; More starts closed
  const words = await page.evaluate(() => Object.fromEntries(["a", "b", "xa", "xb", "xc"].map((k) => {
    const c = document.querySelector("#" + k + "-reveal").cloneNode(true);
    c.querySelectorAll("details, svg, [hidden]").forEach((e) => e.remove());
    return [k, c.textContent.trim().split(/\s+/).length];
  })));
  const LIMIT = { a: 58, b: 90, xa: 45, xb: 50, xc: 80 };
  check(Object.keys(LIMIT).every((k) => words[k] <= LIMIT[k]), `${tag}: each reveal is short before More (${JSON.stringify(words)})`);
  check(await page.evaluate(() => [...document.querySelectorAll(".reveal details")].every((d) => !d.open)) && await page.locator(".reveal details").count() === 5, `${tag}: every reveal has a closed "More on this answer"`);
  for (const id of ["xa-chart", "xb-chart", "xc-chart"]) {
    const titles = await page.locator(`#${id} svg > title`).allTextContents();
    const inside = await page.locator(`#${id} svg text.cl`).allTextContents();
    check(titles.length === R.vars.length && titles.every((t) => t.includes(CL)) && inside.every((t) => t === CL) && inside.length === R.vars.length, `${tag}: ${id}: every curve labelled "${CL}"`);
  }
  // the page as a whole
  const text = await page.evaluate(() => document.body.innerText);
  const strays = (text.match(/\d+(?:\.\d+)?/g) || []).filter((t) => !allowed.has(t));
  check(strays.length === 0, `${tag}: every number shown is in data.js` + (strays.length ? " (not: " + [...new Set(strays)].join(", ") + ")" : ""));
  const own = await page.evaluate(() => document.querySelector("header").textContent + document.querySelector("main").textContent);
  const fullText = await page.evaluate(() => document.body.textContent);
  // the prize's official name is the one place a bank's name may appear (once); the rule is about current policy
  check(fullText.split(D.prize.name).length === 2 && (await page.textContent("#credits")).includes(D.prize.name), `${tag}: the prize's official name, once, in the credits`);
  const own2 = own.split(D.prize.name).join("");
  check(!BANKS.test(own2), `${tag}: no named central bank` + ((own2.match(BANKS) || [])[0] ? " (" + own2.match(BANKS)[0] + ")" : ""));
  check(!ADVICE.test(text), `${tag}: no advice words` + ((text.match(ADVICE) || [])[0] ? " (" + text.match(ADVICE)[0] + ")" : ""));
  check(!VERDICT.test(own2), `${tag}: no verdict words` + ((own2.match(VERDICT) || [])[0] ? " (" + own2.match(VERDICT)[0] + ")" : ""));
  check(!/nobel/i.test(await page.title()), `${tag}: no Nobel in the title`);
  const cred = await page.textContent("#credits");
  for (const l of (S.credit.licence || [])) check(cred.includes(l.text), `${tag}: licence line ${l.text.slice(0, 30)}`);
  if (S.credit.source && !S.synthetic) check(cred.includes(S.credit.source), `${tag}: data source credited`);
  check(R.calibration.source ? cred.includes(R.calibration.source) : true, `${tag}: calibration source credited`);
  check(await page.locator(`a[href="${D.prize.url}"]`).count() >= 1, `${tag}: press release link`);
  check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${tag}: no sideways scrolling`);
  check(await page.evaluate(() => ["Econ Page Sans", "Econ Page Serif", "Econ Page Mono"].every((f) => document.fonts.check("16px \"" + f + "\""))) &&
        await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").length >= 4), `${tag}: bundled fonts load`);
  check(requests.length === 0, `${tag}: no network requests` + (requests.length ? " " + requests.join(" ") : ""));
  check(errors.length === 0, `${tag}: no console errors` + (errors.length ? " " + errors.join(" | ") : ""));
  if (reduced) check(await page.evaluate(() => getComputedStyle(document.querySelector("#a-reveal")).transitionDuration === "0s"), `${tag}: reduced motion stops the transitions`);
  if (width === 1440) {
    const bg0 = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await page.click("#theme");
    check(await page.evaluate(() => document.documentElement.getAttribute("data-theme")) !== theme && bg0 !== await page.evaluate(() => getComputedStyle(document.body).backgroundColor), `${tag}: theme switch`);
    await page.click("#theme");
  }
  if (SHOTS) {
    fs.mkdirSync(path.join(PAGE, "screenshots"), { recursive: true });
    await page.screenshot({ path: path.join(PAGE, "screenshots", `page_${width}_${theme}.png`), fullPage: true });
  }
  await ctx.close();
}

// other inputs: placeholder numbers, the rate toy missing, and a synthetic-only spending toy
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "econ-page-"));
fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
fs.symlinkSync(path.join(PAGE, "fonts"), path.join(tmp, "fonts"));
const FIX = path.join(PAGE, "tests/fixtures");
const synth = path.join(tmp, "synthetic/can-you-predict-spending/results");
fs.mkdirSync(synth, { recursive: true });
const sj = JSON.parse(fs.readFileSync(path.join(FIX, "can-you-predict-spending/results/spending.json"), "utf8"));
delete sj.data; sj.synthetic = true;
fs.writeFileSync(path.join(synth, "spending.json"), JSON.stringify(sj));
const cases = [["fixtures", ["--fixtures"]],
  ["no rate", ["--from", path.join(FIX, "can-you-predict-spending/results"), path.join(tmp, "nowhere")]],
  ["synthetic", ["--from", synth, path.join(FIX, "set-the-rate/results")]]];
for (const [name, args] of cases) {
  execFileSync(PY, [path.join(PAGE, "build_data.py"), ...args, "--out", path.join(tmp, "data.js")], { stdio: "ignore" });
  const { ctx, page, errors } = await open(pathToFileURL(path.join(tmp, "index.html")).href, { width: 768 });
  check(await page.isVisible("#prelim"), `${name}: preliminary box shown`);
  if (name === "fixtures") check((await page.textContent("#prelim")).startsWith("Placeholder"), "fixtures: says placeholder");
  else if (name === "no rate") {
    check((await page.textContent("#rate")).includes("not in this copy") && await page.isHidden("#xa"), "no rate: part two says the data are missing");
    await page.fill("#a-guess-input", "30"); await page.click("#a-go");
    check(await page.isVisible("#a-chart svg"), "no rate: part one still works");
  } else {
    check(await page.isVisible("#synth") && (await page.textContent("#synth")).includes("simulated"), "synthetic: says the numbers are simulated");
    await page.fill("#a-guess-input", "30"); await page.click("#a-go");
    check(await page.isVisible("#a-sim") && (await page.textContent("#a-what")).includes("simulated"), "synthetic: the answer is labelled simulated");
    await page.fill("#b-guess-input", "30"); await page.click("#b-go");
    check(await page.isVisible("#b-sim") && (await page.textContent("#b-ours")).startsWith("Simulated"), "synthetic: the range is labelled simulated");
    check((await page.textContent("#credits")).includes("no data"), "synthetic: credits say no data");
  }
  check(errors.length === 0, `${name}: no console errors ` + errors.join(" | "));
  await ctx.close();
}
fs.rmSync(tmp, { recursive: true, force: true });

if (OGMODE) {
  const { ctx, page } = await open(URL0 + "#og", { width: 1200, height: 630, theme: "light" });
  await page.screenshot({ path: path.join(PAGE, "og.jpg"), type: "jpeg", quality: 86 });
  await ctx.close();
}
await browser.close();
console.log(`${passed} checks passed, ${failed.length} failed` + (SHOTS ? "; screenshots/ refreshed" : "") + (OGMODE ? "; og.jpg refreshed" : ""));
process.exit(failed.length ? 1 : 0);
