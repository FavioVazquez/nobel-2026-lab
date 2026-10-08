// Headless-Chromium check of the Literature "guess first, then see" page (educational demos made to show an
// open-source tool; not research). Opens index.html from file:// at 360, 768 and 1440 px in light and dark, makes every
// guess, reveals every answer, moves the papyrus slider, lights the translators' threads by hovering and tapping Greek
// words, switches the counts and the numbering, and checks: no console errors, no network requests, no sideways
// scrolling, the fonts load, every chart has a title and a description, the numbers come from data.js, and the
// preliminary box follows the inputs.
//
//   PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs [--shots] [--og] [--review DIR]
//   (from 2026/literature/page/; PLAYWRIGHT_CORE=/path/to/playwright-core/index.mjs overrides where playwright is found)
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
const D_OF = (page) => page.evaluate(() => window.NOBEL_LIT_DATA);
async function pickAndReveal(page, id, value) {
  check(await page.isDisabled(`#${id}-go`), `${id}: the reveal waits for a guess`);
  await page.click(`label[for="${await page.$eval(`input[name="${id}"][value="${value}"]`, (e) => e.id)}"]`);
  await page.click(`#${id}-go`);
  await page.waitForSelector(`#${id}-verdict`);
  return page.textContent(`#${id}-verdict`);
}
const fmt = (n) => n.toLocaleString("en-US");

async function answerAll(page, tag) {
  const D = await D_OF(page);
  // fonts: every face the page declares loads from file:// (no CDN)
  const faces = await page.evaluate(async () => { await document.fonts.ready; return [...document.fonts].map((f) => [f.family, f.style, f.weight, f.status]); });
  const used = faces.filter((f) => f[3] === "loaded").map((f) => f[0]);
  check(["Lit Page Body", "Lit Page Greek", "Lit Page Hand"].every((f) => used.includes(f)), `${tag}: self-hosted fonts loaded (${[...new Set(used)].join(", ")})`);
  check(/for her bold and inventive oeuvre/.test(await page.textContent("#citation")) && /Swedish Academy/.test(await page.textContent("#citation-by")), `${tag}: the citation, quoted and attributed`);

  // I. survival ledger
  if (D.ledger) {
    const soph = D.ledger.rows.find((r) => r.id === "sophocles");
    const v1 = await pickAndReveal(page, "s1", soph.survive.lo);
    check(/That's it/.test(v1) && v1.includes(`${soph.survive.lo}`), `${tag}: I. guess and verdict (${soph.survive.lo} plays)`);
    const n = await page.$$eval("#shelves .shelf", (s) => s.length), nsvg = await page.$$eval("#shelves .shelf svg", (s) => s.length);
    const textRows = await page.$$eval('#shelves .shelf[data-kind="text"]', (s) => s.length);
    check(n === D.ledger.rows.length && nsvg === n - textRows, `${tag}: I. one row per author (${n}), ${nsvg} drawn`);
    const before = await page.$eval("#shelves", (e) => e.textContent);
    await page.click("#mode-modern");
    const after = await page.$eval("#shelves", (e) => e.textContent);
    check(await page.getAttribute("#mode-modern", "aria-pressed") === "true" && (before !== after || D.ledger.rows.every((r) => JSON.stringify(r.ancient) === JSON.stringify(r.modern))), `${tag}: I. the ancient / modern switch redraws the shelves`);
    await page.click("#mode-ancient");
    check(await page.isVisible("#sappho-grid") && /100 by 100 grid/.test(await page.getAttribute("#sappho-grid", "aria-label")), `${tag}: I. Sappho's 100 x 100 grid, labelled`);
    check(/Estimate\./.test(await page.textContent("#r1")), `${tag}: I. the grid says it is an estimate`);
  }
  // II. fragments
  if (D.fragments && D.fragments.lengths) {
    const med = D.fragments.lengths.median, ans = med < 10 ? "few" : med <= 30 ? "some" : "many";
    const v2 = await pickAndReveal(page, "s2", ans);
    check(/That's it/.test(v2) && v2.includes(`${fmt(D.fragments.lengths.n)} fragments`), `${tag}: II. guess and verdict (median ${med} words of ${D.fragments.lengths.n})`);
    if (D.fragments.papyrus) {
      const op = () => page.$$eval("#papyrus .rest .t", (s) => s.map((e) => getComputedStyle(e).opacity));
      await page.$eval("#pap-slider", (e) => { e.value = 0; e.dispatchEvent(new Event("input", { bubbles: true })); });
      const o0 = await op();
      await page.$eval("#pap-slider", (e) => { e.value = 100; e.dispatchEvent(new Event("input", { bubbles: true })); });
      const o1 = await op();
      check(o0.length > 0 && o0.every((x) => x === "0") && o1.every((x) => x === "1"), `${tag}: II. papyrus slider hides (0) and shows (1) the ${o0.length} restorations`);
      check(/letters restored by the editors/.test(await page.textContent("#pap-stats")), `${tag}: II. papyrus letter counts`);
      await page.$eval("#pap-slider", (e) => { e.value = 0; e.dispatchEvent(new Event("input", { bubbles: true })); });
    }
    if (D.fragments.quote) check(await page.$$eval("#quote .qline", (q) => q.length) === D.fragments.quote.lines.length && /the quotation ends here/.test(await page.textContent("#quote")), `${tag}: II. the stopped quotation and its mark`);
    await page.click("#hist .bar >> nth=0");
    const bl = await page.textContent("#binlist");
    check(/fr\. \d+ Wharton/.test(bl), `${tag}: II. a histogram bar lists its fragments`);
    await page.click("#num-v");
    const bl2 = await page.textContent("#binlist");
    check(/Voigt/.test(bl2) && bl2 !== bl, `${tag}: II. the Wharton / Voigt switch renumbers`);
    await page.click("#num-w");
    check(await page.$$eval("#hist svg[role=img] title", (t) => t.length) === 1, `${tag}: II. histogram titled`);
  }
  // III. translators
  if (D.translators && D.translators.versions.length) {
    const T = D.translators;
    const k = T.versions.filter((v) => v.links["greek:1:1"] && v.links["greek:1:2"]).length;
    const want = k === T.versions.length ? "all" : k === 0 ? "none" : "some";
    const v3 = await pickAndReveal(page, "s3", want);
    check(/That's it/.test(v3) && v3.includes(`${k} of ${T.versions.length}`), `${tag}: III. guess and verdict (${k} of ${T.versions.length} keep "seems to me")`);
    await page.waitForFunction(() => window.__threads && window.__threads.selected() != null);
    const linked = await page.$$eval(".gw:not(.nolink)", (b) => b.map((x) => x.dataset.id));
    const target = linked[Math.min(3, linked.length - 1)];
    await page.hover(`.gw[data-id="${target}"]`);
    await page.waitForTimeout(80);
    const sel = await page.evaluate(() => window.__threads.selected());
    const lit = await page.evaluate(() => window.__threads.lit());
    const st = await page.evaluate(() => window.__threads.stanza());
    const expectLit = T.versions.reduce((a, v) => a + v.lines.filter((l) => l.stanza === st).flatMap((l) => l.segs).filter((s) => s.g && s.g.some((x) => x[0] === target)).length, 0);
    check(sel === target && lit.length === expectLit && expectLit > 0, `${tag}: III. hovering a Greek word lights its ${expectLit} counterparts`);
    check(await page.evaluate(() => window.__threads.paths()) > 0, `${tag}: III. threads drawn`);
    await page.click(`.gw[data-id="${linked[0]}"]`);
    check(await page.evaluate(() => window.__threads.selected()) === linked[0] && await page.getAttribute(`.gw[data-id="${linked[0]}"]`, "aria-pressed") === "true", `${tag}: III. tapping a Greek word selects it`);
    check(/LSJ/.test(await page.textContent("#gloss-line")), `${tag}: III. the selected word's gloss (LSJ)`);
    await page.click("#stanza-2");
    await page.waitForTimeout(120);
    check(await page.evaluate(() => window.__threads.stanza()) === 2 && await page.evaluate(() => window.__threads.paths()) > 0, `${tag}: III. stanza 2 shows its own threads`);
    await page.click("#stanza-1");
    await page.click("#show-add");
    check(await page.$eval("#threads", (e) => e.classList.contains("show-add")), `${tag}: III. the additions switch`);
    check(/our rough count/.test(await page.textContent("#r3")), `${tag}: III. counts labelled "our rough count"`);
    if (T.glukupikron) check(/compound adjective from Sappho/.test(await page.textContent("#glu")) && /does not name the word/.test(await page.textContent("#glu")), `${tag}: III. the bitter-sweet box with the Committee's sentence`);
  }
  // IV. forms, Float, prize
  if (D.forms) {
    check(await page.$$eval("#formshelf .spine", (s) => s.length) === D.forms.works.length, `${tag}: IV. one spine per book (${D.forms.works.length})`);
    await page.click(".chips-legend button >> nth=0");
    await page.waitForTimeout(50);
    const hits = await page.$$eval("#formshelf .spine.hit", (s) => s.length);
    check(hits === D.forms.forms[0].n && hits > 0, `${tag}: IV. a form filter lights its ${hits} books`);
    await page.click(".chips-legend button >> nth=0");
    const v4 = await pickAndReveal(page, "s4", "bb");
    check(/That's it/.test(v4) && (await page.textContent("#orderings")).replace(/,/g, "") === D.forms.float.orderings && D.forms.float.orderings === "1124000727777607680000", `${tag}: IV. Float: 22! = 1,124,000,727,777,607,680,000`);
    const o1 = await page.textContent("#order"); await page.click("#shuffle"); const o2 = await page.textContent("#order");
    check(o1 !== o2, `${tag}: IV. the chapbooks shuffle`);
  }
  if (D.prize) {
    const v5 = await pickAndReveal(page, "s5", D.prize.women);
    check(/That's it/.test(v5) && v5.includes(`${D.prize.women} of ${D.prize.total}`) && /\d+(st|nd|rd|th)\b/.test(v5), `${tag}: IV. prize: ${D.prize.women} women of ${D.prize.total}`);
    check(await page.$$eval("#prizeshelf .spine", (s) => s.length) === D.prize.total && await page.$$eval("#prizeshelf .spine.woman", (s) => s.length) === D.prize.women, `${tag}: IV. one spine per laureate, women inked`);
  }
}

const browser = await chromium.launch();
const served = ["index.html", "data.js", ...fs.readdirSync(path.join(PAGE, "fonts")).filter((f) => f.endsWith(".woff2")).map((f) => "fonts/" + f)];
const size = served.reduce((a, f) => a + fs.statSync(path.join(PAGE, f)).size, 0);
check(size < 1.5e6, `index.html + data.js + fonts = ${(size / 1024).toFixed(1)} KB (< 1.5 MB)`);
const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");
check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html) && !/@import|url\(["']?https?:/i.test(html), "no external scripts, styles, fonts or images");
check(!/rel=["']?canonical/i.test(html), "no canonical link");
check(html.includes('property="og:url" content="https://faviovazquez.github.io/nobel-2026-lab/2026/literature/page/"') &&
  html.includes('property="og:image" content="https://faviovazquez.github.io/nobel-2026-lab/2026/literature/page/og.jpg"'), "share tags (og:url, og:image)");
check(fs.readFileSync(path.join(PAGE, "data.js"), "utf8").includes("Educational demos made to show an open-source tool. Not research."), "label present");
check(html.includes("https://github.com/FavioVazquez/showtime"), "Made with showtime link");
check(html.includes('href="../video/exports/nobel-2026-literature.mp4"') && fs.existsSync(path.join(PAGE, "..", "video", "exports", "nobel-2026-literature.mp4")), "link to the video file, which exists");
check(fs.existsSync(path.join(PAGE, "..", "video", "README.md")) && html.includes("video/\">claims, captions and credits"), "link to the video folder");
check((html.match(/hold in equipoise/g) || []).length <= 1, "the Committee-quoted line at most once");
// The laureate's words appear only as short quotations from ../quotes.json (verified wording, attributed, capped).
const QJ = JSON.parse(fs.readFileSync(path.join(PAGE, "..", "quotes.json"), "utf8")).quotes;
const words = (t) => (t.match(/[\p{L}\p{N}’'-]+/gu) || []).length;
async function checkQuotes(page, tag) {
  const D = await D_OF(page);
  const shown = await page.$$eval("figure.carson-quote", (fs_) => fs_.map((f) => [f.getAttribute("data-quote"), f.querySelector("blockquote").textContent, f.querySelector("figcaption").textContent]));
  check(shown.length === (D.quotes || []).length, `${tag}: every verified quotation is shown once (${shown.length} of ${(D.quotes || []).length})`);
  for (const [id, text, cap] of shown) {
    const q = QJ.find((x) => x.id === id);
    const bare = text.replace(/^“|”$/g, "");
    check(!!q && q.text === bare, `${tag}: quotation ${id} is in quotes.json word for word`);
    check(!!q && cap.startsWith(`Anne Carson, ${q.work} (${q.year})`), `${tag}: quotation ${id} attributed (${cap.split(" · ")[0]})`);
    check(words(bare) <= D.quote_cap, `${tag}: quotation ${id} has ${words(bare)} words (cap ${D.quote_cap})`);
  }
  const html_ = await page.content();
  for (const q of QJ) check((html_.split(q.text).length - 1) <= 1, `${tag}: quotation ${q.id} appears at most once`);
}

const url = pathToFileURL(path.join(PAGE, "index.html")).href;
for (const theme of THEMES) for (const width of WIDTHS) {
  const tag = `${width}px ${theme}`;
  const { ctx, page, errors, requests } = await open(browser, url, width, theme);
  const D = await D_OF(page);
  check(await page.isVisible("#prelim") === D.preliminary, `${tag}: preliminary box ${D.preliminary ? "shown" : "hidden"} (${JSON.stringify(D.inputs)})`);
  await answerAll(page, tag);
  await page.evaluate(() => { window.__inkAll(); const c = document.querySelector("#sappho-grid"); if (c && c.__finish) c.__finish(); });
  await checkQuotes(page, tag);
  const svgOk = await page.$$eval("svg[role=img]", (s) => s.length > 0 && s.every((e) => e.querySelector("title") && e.querySelector("desc")));
  check(svgOk, `${tag}: every chart has a title and a description`);
  check(await page.$$eval("canvas[role=img]", (c) => c.every((e) => e.getAttribute("aria-label"))), `${tag}: every canvas has a label`);
  const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check(over <= 0, `${tag}: no sideways scrolling (overflow ${over}px)`);
  const wide = await page.$$eval("main *, header *, footer *", (els) => els.filter((e) => !e.closest("svg") && !e.closest(".chaps") && e.getClientRects().length && e.getBoundingClientRect().right > window.innerWidth + 0.5).map((e) => e.tagName + "#" + e.id + "." + e.className).slice(0, 5));
  check(wide.length === 0, `${tag}: nothing pokes past the right edge ${wide.join(" ")}`);
  check(errors.length === 0, `${tag}: no console errors ${errors.join(" | ")}`);
  check(requests.length === 0, `${tag}: no network requests ${requests.join(" ")}`);
  if (SHOTS) {
    await page.waitForTimeout(1300);
    const out = path.join(PAGE, "screenshots", `page_${width}_${theme}.png`);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out, fullPage: true });
    try { // a 256-colour palette keeps each full-page PNG near 1 MB (the paper grain defeats JPEG)
      execFileSync(PY, ["-c", "import sys; from PIL import Image; p=sys.argv[1]; Image.open(p).convert('RGB').quantize(256, method=0, dither=0).save(p, optimize=True)", out]);
    } catch (e) { console.log("note: Pillow not found, screenshot left uncompressed"); }
    console.log(`     wrote ${path.relative(PAGE, out)} (${(fs.statSync(out).size / 1024).toFixed(0)} KB)`);
  }
  if (REVIEW) {
    fs.mkdirSync(REVIEW, { recursive: true });
    await page.waitForTimeout(1300);
    for (const sel of ["header", "#s0", "#s1", "#s2", "#s3", "#s4", "footer"])
      await page.locator(sel).screenshot({ path: path.join(REVIEW, `${width}_${theme}_${sel.replace("#", "")}.png`) });
  }
  await ctx.close();
}

// Reduced motion: everything is drawn at once, and nothing breaks.
{
  const { ctx, page, errors } = await open(browser, url, 360, "light", 900, true);
  await answerAll(page, "360px reduced motion");
  const undrawn = await page.$$eval("svg.ink", (s) => s.filter((e) => !e.closest(".drawn")).map((e) => (e.closest("[id]") || {}).id));
  check(undrawn.length === 0, `reduced motion: every ink figure is drawn at once ${undrawn.join(" ")}`);
  check(errors.length === 0, `reduced motion: no console errors ${errors.join(" | ")}`);
  await ctx.close();
}
// The lamp switch flips the theme by hand.
{
  const { ctx, page, errors } = await open(browser, url, 768, "light");
  const bg0 = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  await page.click("#lamp");
  const bg1 = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  check(bg0 !== bg1 && await page.getAttribute("html", "data-theme") === "dark", `lamp switch: ${bg0} -> ${bg1}`);
  check(errors.length === 0, `lamp switch: no console errors ${errors.join(" | ")}`);
  await ctx.close();
}

// A copy built with every input "final" hides the box; copies without one input say so and still have no errors.
const js = fs.readFileSync(path.join(PAGE, "data.js"), "utf8");
const start = js.indexOf("window.NOBEL_LIT_DATA = ") + "window.NOBEL_LIT_DATA = ".length, end = js.lastIndexOf(";");
const base = JSON.parse(js.slice(start, end));
const variants = [
  ["all final", (d) => { for (const k in d.inputs) d.inputs[k] = "final"; d.preliminary = false; d.placeholder = false; }, false],
  ["ledger missing", (d) => { d.inputs["ledger.json"] = "missing"; d.ledger = null; d.preliminary = true; }, true],
  ["fragments missing", (d) => { d.inputs["fragments.json"] = "missing"; d.fragments = null; d.preliminary = true; }, true],
  ["translators missing", (d) => { d.inputs["versions.json"] = "missing"; d.inputs["alignment.json"] = "missing"; d.translators = null; d.preliminary = true; }, true],
  ["forms missing", (d) => { d.inputs["forms.json"] = "missing"; d.inputs["prize_history.json"] = "missing"; d.forms = null; d.prize = null; d.preliminary = true; }, true],
];
for (const [label, mutate, expectBox] of variants) {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "lit-page-"));
  fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
  fs.cpSync(path.join(PAGE, "fonts"), path.join(tmp, "fonts"), { recursive: true });
  const d = JSON.parse(JSON.stringify(base)); mutate(d);
  fs.writeFileSync(path.join(tmp, "data.js"), js.slice(0, start) + JSON.stringify(d) + js.slice(end));
  const { ctx, page, errors } = await open(browser, pathToFileURL(path.join(tmp, "index.html")).href, 768, "light");
  check(await page.isVisible("#prelim") === expectBox, `${label}: preliminary box ${expectBox ? "shown" : "hidden"}`);
  if (label !== "all final") check(/not in this copy/.test(await page.textContent("main")), `${label}: the page says which part is not in yet`);
  else await answerAll(page, "all final");
  check(errors.length === 0, `${label}: no console errors ${errors.join(" | ")}`);
  await ctx.close();
  fs.rmSync(tmp, { recursive: true, force: true });
}

if (OG) {
  const { ctx, page, errors } = await open(browser, url + "#og", 1200, "light", 630);
  const out = path.join(PAGE, "og.jpg");
  await page.waitForTimeout(300);
  await page.screenshot({ path: out, type: "jpeg", quality: 88, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  check(errors.length === 0, `og.jpg rendered (${(fs.statSync(out).size / 1024).toFixed(0)} KB), no console errors ${errors.join(" | ")}`);
  await ctx.close();
}
await browser.close();
console.log(failures ? `${failures} check(s) failed` : "all checks passed");
process.exit(failures ? 1 : 0);
