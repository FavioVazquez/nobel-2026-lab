// Headless-Chromium check of the Chemistry "guess first, then see" page (educational demo, toy models; not research).
// Opens index.html from file:// at 360, 768 and 1440 px in light and dark, makes every guess (step 1 by keyboard only),
// reveals every answer, moves every slider, runs the live race, and checks: no console errors, no network requests, no
// sideways scrolling, every chart has a title and description, caveats sit next to the numbers, the numbers come from
// data.js, Kagan's curve at 75:25 with K = 4, g = 0 reads 80%, the live race finishes and picks a hand, and the
// preliminary box follows the inputs.
//
//   PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs [--shots] [--og] [--review DIR]
//   (from 2026/chemistry/page/; PLAYWRIGHT_CORE=/path/to/playwright-core/index.mjs overrides where playwright is found)
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath, pathToFileURL } from "node:url";

const PW = process.env.PLAYWRIGHT_CORE || path.join(os.homedir(), ".showtime/node/node_modules/playwright-core/index.mjs");
const { chromium } = await import(pathToFileURL(PW).href);
const PAGE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const args = process.argv.slice(2);
const SHOTS = args.includes("--shots"), OG = args.includes("--og");
const REVIEW = args.includes("--review") ? args[args.indexOf("--review") + 1] : null;
const PY = process.env.PYTHON || "python3";
const WIDTHS = [360, 768, 1440], THEMES = ["light", "dark"];
let failures = 0;
const check = (ok, msg) => { console.log(`${ok ? "ok  " : "FAIL"} ${msg}`); if (!ok) failures++; };

async function open(browser, url, width, theme, height = 900, reduced = false) {
  const ctx = await browser.newContext({ viewport: { width, height }, colorScheme: theme, deviceScaleFactor: 1, reducedMotion: reduced ? "reduce" : "no-preference" });
  const page = await ctx.newPage();
  const errors = [], requests = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => { if (!r.url().startsWith("file://")) requests.push(r.url()); });
  await page.goto(url);
  return { ctx, page, errors, requests };
}
async function slide(page, sel, value) {
  await page.$eval(sel, (e, v) => { e.value = v; e.dispatchEvent(new Event("input", { bubbles: true })); }, String(value));
}

async function answerAll(page, tag) {
  const D = await page.evaluate(() => window.NOBEL_CHEM_DATA);
  // Step 0: the stack button slides the mirror molecule onto ours and says why they do not match.
  check(await page.isVisible("#mol"), `${tag}: molecule viewer drawn`);
  await page.click("#s0-stack");
  await page.waitForSelector("#s0-out:not([hidden])", { timeout: 8000 });
  const t0 = await page.textContent("#s0-out");
  check(/point the wrong way/.test(t0) && /No turn fixes it/.test(t0), `${tag}: stacking shows they do not match`);
  const mis = await page.evaluate(() => /miss by ([\d.]+)/.exec(document.querySelector("#s0-out").textContent)[1]);
  check(Number(mis) > 0.5, `${tag}: the mismatched arms miss by more than 0.5 Å (${mis} Å)`);

  // Step 1 by keyboard: focus the first choice, arrow to 80%, Tab to the button, Enter.
  check(await page.isDisabled("#s1-go"), `${tag}: step 1 reveal waits for a guess`);
  await page.focus('input[name="s1"]');
  for (let i = 0; i < 2; i++) await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Enter");
  await page.waitForSelector("#s1-out:not([hidden]) svg");
  const t1 = await page.textContent("#s1-out");
  check(/You picked 80%/.test(t1) && /That's it/.test(t1), `${tag}: step 1 guess by keyboard and verdict`);
  check(t1.includes(D.kagan.pie.ee_prod_pct + "%") && /90 parts one hand to 10/.test(t1), `${tag}: step 1 answer 80% (90:10) from data.js`);
  check(/the textbook ML2 model; real systems vary/.test(t1), `${tag}: step 1 caveat`);
  check(await page.$$eval("#s1-pies svg", (s) => s.length) === 3 && /56%/.test(t1) && /38%/.test(t1) && /6%/.test(t1), `${tag}: our own three-pie drawing (75:25 -> 56/38/6 -> 90:10)`);
  check(await page.evaluate(() => KG.source) === "kagan.js", `${tag}: the curve uses kagan.js`);
  await slide(page, "#s1-p", 75); await slide(page, "#s1-k", Math.log10(4)); await slide(page, "#s1-g", 0);
  const r1 = await page.textContent("#s1-readout");
  check(/product excess\s+80%/.test(r1) && /K = 4/.test(await page.textContent("#s1-kv")), `${tag}: Kagan curve at 75:25, K = 4, g = 0 reads 80%`);
  await slide(page, "#s1-g", 1);
  check(/product excess\s+50%/.test(await page.textContent("#s1-readout")) && /straight line/.test(await page.textContent("#s1-readout")), `${tag}: g = 1 gives the straight line (50%)`);
  await slide(page, "#s1-g", 2);
  check(/sag below/.test(await page.textContent("#s1-readout")), `${tag}: g > 1 gives a sag`);
  await slide(page, "#s1-k", 3); await slide(page, "#s1-g", 0);
  { const t = await page.textContent("#s1-readout");
    check(/product excess\s+(9\d|9\d\.\d\d|more than 99\.9)%/.test(t) && !/product excess\s+100%/.test(t), `${tag}: large K with idle mixed pairs approaches 100% (never rounded up to it)`); }
  await slide(page, "#s1-k", Math.log10(4)); await slide(page, "#s1-g", 0);

  // Step 2
  check(await page.isDisabled("#s2-go"), `${tag}: step 2 reveal waits for a guess`);
  await page.check('input[name="s2"][value="50"]');
  await page.click("#s2-go");
  await page.waitForSelector("#s2-out:not([hidden]) svg");
  const t2 = await page.textContent("#s2-out");
  check(/0\.00005%/.test(t2) && /57%/.test(t2) && /99%/.test(t2) && />99\.5%/.test(t2) && /real measurement/.test(t2), `${tag}: step 2 shows Soai's real 2003 series`);
  check(!/99\.99/.test(t2), `${tag}: no "99.99%" anywhere in step 2`);
  check(/prepared on purpose/.test(t2), `${tag}: the head start was prepared, not chance`);
  check(/one published toy model of several; the real mechanism is still debated/.test(t2), `${tag}: step 2 caveat`);
  if (D.amp) check(/our toy model, trend only/.test(t2) && await page.$$eval("#s2-stairs rect", (r) => r.length) >= 8, `${tag}: toy rounds next to the real ones`);
  check(await page.isVisible("#s2-log svg"), `${tag}: log-scale inset drawn`);

  // Step 3
  check(await page.isDisabled("#s3-go"), `${tag}: step 3 reveal waits for a guess`);
  await page.check('input[name="s3"][value="random"]');
  await page.click("#s3-go");
  await page.waitForSelector("#race-result[data-winner]", { timeout: 20000 });
  const w1 = await page.getAttribute("#race-result", "data-winner");
  check(["one", "mirror"].includes(w1) || w1 === "tie", `${tag}: live race finishes and picks a hand (${w1})`);
  const S = await page.evaluate(() => { const s = window.__race(); return { x: s.x, y: s.y, free: s.free.length, N: s.N, done: s.done }; });
  check(S.done && S.free === 0 && Math.min(S.x, S.y) === 0, `${tag}: with antagonism the race ends with one hand only (${S.x} vs ${S.y})`);
  await page.click("#race-anta");
  await page.waitForSelector("#race-result[data-winner]", { timeout: 20000 });
  const S2 = await page.evaluate(() => { const s = window.__race(); return { x: s.x, y: s.y, anta: s.anta, done: s.done, N: s.N }; });
  check(!S2.anta && S2.done && S2.x + S2.y === S2.N, `${tag}: antagonism off: every molecule ends handed, a mix (${S2.x} vs ${S2.y})`);
  await page.click("#race-anta");
  await page.waitForSelector("#race-result[data-winner]", { timeout: 20000 });
  const t3 = await page.textContent("#s3-out");
  check(/toy network, not the Soai mechanism, and not the origin of life/.test(t3) && /is not an answer to the origin of biological homochirality/.test(t3), `${tag}: step 3 caveat`);
  check(/37 real runs/.test(t3) && /one hand 19 : mirror hand 18/.test(t3) && /15 to 91%/.test(t3) && /one hand 27 : mirror hand 27/.test(t3), `${tag}: is-the-coin-fair panel (19/18, 15-91%, 27/27)`);
  if (D.mirror && D.mirror.hist) {
    await page.waitForTimeout(150);
    for (const b of ["#h-copy", "#h-early", "#h-build", "#h-anta"]) { if (!(await page.isDisabled(b))) { await page.click(b); await page.waitForTimeout(80); } }
    await page.waitForTimeout(1100);
    check(await page.$$eval("#s3-hist rect", (r) => r.length) > 2, `${tag}: histogram drawn`);
  }
}

const browser = await chromium.launch();
const size = ["index.html", "data.js"].reduce((a, f) => a + fs.statSync(path.join(PAGE, f)).size, 0);
check(size < 1.5e6, `index.html + data.js = ${(size / 1024).toFixed(1)} KB (< 1.5 MB)`);
const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");
check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html) && !/@import|url\(["']?https?:/i.test(html), "no external scripts, styles, fonts or images");
check(!/rel=["']?canonical/i.test(html), "no canonical link");
check(html.includes('property="og:url" content="https://faviovazquez.github.io/nobel-2026-lab/2026/chemistry/page/"') &&
  html.includes('property="og:image" content="https://faviovazquez.github.io/nobel-2026-lab/2026/chemistry/page/og.jpg"'), "share tags (og:url, og:image)");
check(html.includes("Educational demo, toy models. Not research."), "toy-model banner present");
check(html.includes("https://github.com/FavioVazquez/showtime"), "Made with showtime link");
check(!/99\.99/.test(html), 'no "99.99%" in the page');

const url = pathToFileURL(path.join(PAGE, "index.html")).href;
for (const theme of THEMES) for (const width of WIDTHS) {
  const tag = `${width}px ${theme}`;
  const { ctx, page, errors, requests } = await open(browser, url, width, theme);
  const D = await page.evaluate(() => window.NOBEL_CHEM_DATA);
  check(await page.isVisible("#prelim") === D.preliminary, `${tag}: preliminary box ${D.preliminary ? "shown" : "hidden"} (inputs: ${JSON.stringify(D.inputs)})`);
  if (!D.mirror || !D.kagan || !D.amp) { check(false, `${tag}: data.js lacks an input (${JSON.stringify(D.inputs)})`); await ctx.close(); continue; }
  await answerAll(page, tag);
  const svgOk = await page.$$eval("svg[role=img]", (s) => s.length > 0 && s.every((e) => e.querySelector("title") && e.querySelector("desc")));
  check(svgOk, `${tag}: every chart has a title and description`);
  check(await page.$$eval("canvas[role=img]", (c) => c.every((e) => e.getAttribute("aria-label"))), `${tag}: every canvas has a label`);
  const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check(over <= 0, `${tag}: no sideways scrolling (overflow ${over}px)`);
  const wide = await page.$$eval("main *, header *, footer *", (els) => els.filter((e) => !e.closest("svg") && e.getBoundingClientRect().right > window.innerWidth + 0.5).map((e) => e.tagName + "#" + e.id + "." + e.className).slice(0, 5));
  check(wide.length === 0, `${tag}: nothing pokes past the right edge ${wide.join(" ")}`);
  check(errors.length === 0, `${tag}: no console errors ${errors.join(" | ")}`);
  check(requests.length === 0, `${tag}: no network requests ${requests.join(" ")}`);
  if (SHOTS) {
    const out = path.join(PAGE, "screenshots", `page_${width}_${theme}.png`);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out, fullPage: true });
    try { // 256-colour palette keeps each full-page PNG small
      execFileSync(PY, ["-c", "import sys; from PIL import Image; p=sys.argv[1]; Image.open(p).convert('RGB').quantize(256, method=0, dither=0).save(p, optimize=True)", out]);
    } catch (e) { console.log("note: Pillow not found, screenshot left uncompressed"); }
    console.log(`     wrote ${path.relative(PAGE, out)} (${(fs.statSync(out).size / 1024).toFixed(0)} KB)`);
  }
  if (REVIEW) {
    fs.mkdirSync(REVIEW, { recursive: true });
    for (const sel of ["header", "#step0", "#step1", "#step2", "#step3", "#step4", "footer"])
      await page.locator(sel).screenshot({ path: path.join(REVIEW, `${width}_${theme}_${sel.replace("#", "")}.png`) });
  }
  await ctx.close();
}

// Reduced motion: every animation jumps to its end, and nothing breaks.
{
  const { ctx, page, errors } = await open(browser, url, 360, "light", 900, true);
  await answerAll(page, "360px reduced motion");
  check(errors.length === 0, `reduced motion: no console errors ${errors.join(" | ")}`);
  await ctx.close();
}

// A copy built with every input "final" hides the box; one with the mirror race missing says so and has no errors.
for (const [label, mutate, expectBox] of [["all final", (d) => { d.inputs = { mirror_race: "final", kagan_curve: "final", soai_amplifier: "final" }; d.preliminary = false; d.placeholder = false; }, false],
                                          ["mirror race missing", (d) => { d.inputs.mirror_race = "missing"; d.mirror = null; d.preliminary = true; }, true],
                                          ["kagan missing", (d) => { d.inputs.kagan_curve = "missing"; d.kagan = null; d.preliminary = true; }, true]]) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "chem-page-"));
  fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
  const js = fs.readFileSync(path.join(PAGE, "data.js"), "utf8");
  const start = js.indexOf("window.NOBEL_CHEM_DATA = ") + "window.NOBEL_CHEM_DATA = ".length, end = js.indexOf(";\nwindow.NOBEL_CHEM_KAGAN");
  const d = JSON.parse(js.slice(start, end));
  mutate(d);
  fs.writeFileSync(path.join(tmp, "data.js"), js.slice(0, start) + JSON.stringify(d) + js.slice(end));
  const { ctx, page, errors } = await open(browser, pathToFileURL(path.join(tmp, "index.html")).href, 768, "light");
  check(await page.isVisible("#prelim") === expectBox, `${label}: preliminary box ${expectBox ? "shown" : "hidden"}`);
  if (label === "kagan missing") check(await page.isDisabled("#s1-go") && /not in this copy/.test(await page.textContent("#s1-hint")), `${label}: step 1 says the results are not in yet`);
  if (label === "mirror race missing") {
    await page.check('input[name="s3"][value="random"]'); await page.click("#s3-go");
    await page.waitForSelector("#race-result[data-winner]", { timeout: 20000 });
    check(/not in this copy/.test(await page.textContent("#s3-hist")), `${label}: the live race still runs; the histogram says it is not in yet`);
  }
  check(errors.length === 0, `${label}: no console errors ${errors.join(" | ")}`);
  await ctx.close();
}

if (OG) {
  const { ctx, page, errors } = await open(browser, url + "#og", 1200, "light", 630);
  const out = path.join(PAGE, "og.jpg");
  await page.waitForTimeout(200);
  await page.screenshot({ path: out, type: "jpeg", quality: 86, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  check(errors.length === 0, `og.jpg rendered (${(fs.statSync(out).size / 1024).toFixed(0)} KB), no console errors ${errors.join(" | ")}`);
  await ctx.close();
}
await browser.close();
console.log(failures ? `${failures} check(s) failed` : "all checks passed");
process.exit(failures ? 1 : 0);
