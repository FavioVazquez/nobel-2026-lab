// Headless-Chromium check of the Peace page. Educational demos made to show an open-source tool. Not research.
// Opens index.html from file:// at 360, 768 and 1440 px in light and dark (and with reduced motion), makes both
// guesses, flips both toggles and checks what a visitor would see. With --shots it refreshes screenshots/, with --og og.jpg.
//   PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs [--shots] [--og]
//   (from 2026/peace/page/; PLAYWRIGHT_CORE=/path/to/playwright-core/index.mjs overrides where playwright is found)
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
const NB = "\u00a0", pct = (x) => Number(x).toFixed(1) + NB + "%";
// the excluded place terms, in rot13 so that no file of the page spells them
const rot13 = (t) => t.replace(/[a-z]/gi, (c) => String.fromCharCode((c <= "Z" ? 65 : 97) + (c.toLowerCase().charCodeAt(0) - 84) % 26));
const EXCLUDED = new RegExp(rot13("tnmn|vfenry|cnyrfgva"), "i");
const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");

// every number a visitor can read must be a number of data.js (or an axis tick, or their own guess)
const allowed = new Set(["0", "5", "10", "15", "20", "25", "50", "75", "100", "40", "60"]);
(function walk(v) {
  if (typeof v === "number") { for (const s of [String(v), v.toFixed(1), v.toFixed(3), Math.abs(v).toFixed(1), Math.abs(v).toFixed(3), String(Math.abs(v))]) allowed.add(s); }
  else if (typeof v === "string") { for (const t of v.match(/\d+(?:\.\d+)?/g) || []) allowed.add(t); }
  else if (v && typeof v === "object") { for (const k in v) { walk(k); walk(v[k]); } }
})(D);
for (const d of (D.ends || {}).decades || []) allowed.add(d.decade.slice(2, 4));  // narrow screens label decades ’90s

check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html) && !/@import|url\(["']?https?:/i.test(html), "no external scripts, styles, fonts or images");
check(html.includes('href="https://github.com/FavioVazquez/showtime"'), "Made with showtime link");
check(/<meta property="og:image" content="[^"]+og\.jpg"/.test(html), "og:image");

const browser = await chromium.launch();
async function open(url, { width = 1440, height = 900, theme = "dark", reduced = false } = {}) {
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
const E = D.ends, H = D.hold;

for (const width of WIDTHS) for (const theme of THEMES) {
  const tag = `${width}px ${theme}`, reduced = width === 360 && theme === "dark";
  const { ctx, page, errors, requests } = await open(URL0, { width, theme, reduced });
  const first = await page.evaluate(() => document.body.innerText.trim().split("\n")[0]);
  check(first === D.tag, `${tag}: the label is the first thing on the page`);
  check(await page.evaluate(() => document.documentElement.getAttribute("data-theme")) === theme, `${tag}: theme follows the system`);
  check(await page.isHidden("#prelim"), `${tag}: no preliminary box when every input is final`);
  check(await page.isDisabled("#ends-go") && await page.isDisabled("#hold-go"), `${tag}: Reveal waits for a guess`);
  check(await page.isHidden("#ends-reveal") && await page.isHidden("#hold-reveal"), `${tag}: the answers are hidden before the guess`);
  // first room
  await page.fill("#ends-guess-input", "40");
  check(await page.isEnabled("#ends-go"), `${tag}: Reveal enabled after a guess`);
  check((await page.textContent("#ends-guess-input-out")).startsWith("40"), `${tag}: the guess is shown`);
  await page.click("#ends-go");
  check((await page.textContent("#ends-big")) === pct(E.pct), `${tag}: first answer ${pct(E.pct)}`);
  check((await page.textContent("#ends-verdict")).includes("You guessed 40"), `${tag}: verdict repeats the guess`);
  check(await page.locator("#ends-chart svg title").first().textContent() !== "" && await page.locator("#ends-chart svg > desc").count() === 1, `${tag}: bars have a title and desc`);
  check(await page.locator("#ends-chart rect.bar").count() === E.decades.length, `${tag}: one bar per decade`);
  check(await page.locator("#ends-chart polyline.low").count() === 1, `${tag}: low-activity line in the all-endings view`);
  const note = await page.textContent("#ends-note");
  check(note.includes(E.insights[2].text) && note.includes(String(E.second.low_activity_2010s_pct.toFixed(1))), `${tag}: the fade-out twist`);
  const hAll = await page.locator("#ends-chart rect.bar").first().getAttribute("height");
  await page.click("#view-clear");
  check(await page.getAttribute("#view-clear", "aria-pressed") === "true" && await page.getAttribute("#view-all", "aria-pressed") === "false", `${tag}: clear-outcome toggle pressed`);
  check(await page.locator("#ends-chart polyline.low").count() === 0 && hAll !== await page.locator("#ends-chart rect.bar").first().getAttribute("height"), `${tag}: clear-outcome bars redrawn`);
  const cn = await page.textContent("#ends-note");
  check(cn.includes(E.second.complete_decades_since_1990_min_pct.toFixed(1)) && cn.includes(E.second.before_1990_max_pct.toFixed(1)), `${tag}: clear-outcome minimum and maximum`);
  // second room
  await page.fill("#hold-guess-input", "60");
  await page.click("#hold-go");
  check((await page.textContent("#hold-big")) === pct(H.main.pct), `${tag}: second answer ${pct(H.main.pct)}`);
  const ci = await page.textContent("#hold-ci");
  check(ci.includes(H.main.ci[0].toFixed(1) + " to " + H.main.ci[1].toFixed(1)) && ci.includes("linked conflicts"), `${tag}: cluster interval, linked conflicts allowed for`);
  check(await page.locator("#hold-chart path.km").count() === 2 && await page.locator("#hold-chart svg > title").count() === 1, `${tag}: two Kaplan-Meier curves with a title`);
  const d1 = await page.getAttribute("#hold-chart path.km.sel", "d");
  check(d1.split("V").length - 1 === H.main.curve.length, `${tag}: the main curve has one step per JSON point`);
  await page.click("#clock-strict");
  check((await page.textContent("#hold-big")) === pct(H.strict.pct), `${tag}: strict clock ${pct(H.strict.pct)}`);
  check((await page.textContent("#hold-note")).includes("never stopped"), `${tag}: why the strict clock differs`);
  check(d1 !== await page.getAttribute("#hold-chart path.km.sel", "d"), `${tag}: the curve switches`);
  check((await page.textContent("#hold-types")).includes("cannot rank"), `${tag}: types not ranked`);
  // the page as a whole
  const text = await page.evaluate(() => document.body.innerText);
  const strays = (text.match(/\d+(?:\.\d+)?/g) || []).filter((t) => !allowed.has(t));
  check(strays.length === 0, `${tag}: every number shown is in data.js` + (strays.length ? " (not: " + [...new Set(strays)].join(", ") + ")" : ""));
  check(!EXCLUDED.test(text), `${tag}: no excluded places`);
  for (const c of [E.credit.citation, H.credit.pa.citation, H.credit.pa.codebook_citation, "CC BY 4.0"]) check(text.includes(c), `${tag}: credit ${c.slice(0, 30)}`);
  check(await page.locator(`a[href="${D.prize.url}"]`).count() >= 1, `${tag}: press release link`);
  check(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), `${tag}: no sideways scrolling`);
  check(await page.evaluate(() => ["Peace Page Sans", "Peace Page Serif"].every((f) => document.fonts.check("16px \"" + f + "\""))) &&
        await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").length >= 3), `${tag}: bundled fonts load`);
  check(requests.length === 0, `${tag}: no network requests` + (requests.length ? " " + requests.join(" ") : ""));
  check(errors.length === 0, `${tag}: no console errors` + (errors.length ? " " + errors.join(" | ") : ""));
  if (reduced) check(await page.evaluate(() => getComputedStyle(document.querySelector("#ends-chart rect.bar")).transitionDuration === "0s"), `${tag}: reduced motion stops the transitions`);
  if (width === 1440) {
    const bg0 = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
    await page.click("#theme");
    check(await page.evaluate(() => document.documentElement.getAttribute("data-theme")) !== theme && bg0 !== await page.evaluate(() => getComputedStyle(document.body).backgroundColor), `${tag}: theme switch`);
    await page.click("#theme");
  }
  if (SHOTS) {
    await page.click("#view-all"); await page.click("#clock-main");
    fs.mkdirSync(path.join(PAGE, "screenshots"), { recursive: true });
    await page.screenshot({ path: path.join(PAGE, "screenshots", `page_${width}_${theme}.png`), fullPage: true });
  }
  await ctx.close();
}

// other inputs: placeholder numbers, and a toy missing
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "peace-page-"));
fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
fs.symlinkSync(path.join(PAGE, "fonts"), path.join(tmp, "fonts"));
for (const [name, args] of [["fixtures", ["--fixtures"]], ["no hold", ["--from", path.join(PAGE, "tests/fixtures/how-conflicts-end/results"), path.join(tmp, "nowhere")]]]) {
  execFileSync(PY, [path.join(PAGE, "build_data.py"), ...args, "--out", path.join(tmp, "data.js")], { stdio: "ignore" });
  const { ctx, page, errors } = await open(pathToFileURL(path.join(tmp, "index.html")).href, { width: 768 });
  check(await page.isVisible("#prelim"), `${name}: preliminary box shown`);
  if (name === "fixtures") check((await page.textContent("#prelim")).startsWith("Placeholder"), "fixtures: says placeholder");
  else {
    check((await page.textContent("#hold")).includes("not in this copy") && await page.isHidden("#hold-guess"), "no hold: second room says the data are missing");
    await page.fill("#ends-guess-input", "30"); await page.click("#ends-go");
    check(await page.isVisible("#ends-chart svg"), "no hold: first room still works");
  }
  check(errors.length === 0, `${name}: no console errors ` + errors.join(" | "));
  await ctx.close();
}
fs.rmSync(tmp, { recursive: true, force: true });

if (OGMODE) {
  const { ctx, page } = await open(URL0 + "#og", { width: 1200, height: 630, theme: "dark" });
  await page.screenshot({ path: path.join(PAGE, "og.jpg"), type: "jpeg", quality: 86 });
  await ctx.close();
}
await browser.close();
console.log(`${passed} checks passed, ${failed.length} failed` + (SHOTS ? "; screenshots/ refreshed" : "") + (OGMODE ? "; og.jpg refreshed" : ""));
process.exit(failed.length ? 1 : 0);
