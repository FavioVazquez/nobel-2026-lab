// Headless-Chromium check of the Physics "guess first, then see" page (educational demo, toy models; not research).
// Opens index.html from file://, makes every guess (step 1 by keyboard only), reveals every answer, moves every slider,
// and checks: no console errors, no network requests, no sideways scrolling, every chart has a title and description,
// the caveats sit next to the numbers, the numbers come from data.js, the preliminary banner follows the inputs.
//
//   PLAYWRIGHT_BROWSERS_PATH=~/.showtime/browsers node tests/test_page.mjs [--shots] [--og] [--review DIR]
//   (from 2026/physics/page/; PLAYWRIGHT_CORE=/path/to/playwright-core/index.mjs overrides where playwright is found)
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

async function open(browser, url, width, theme, height = 900) {
  const ctx = await browser.newContext({ viewport: { width, height }, colorScheme: theme, deviceScaleFactor: 1 });
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
  const D = await page.evaluate(() => window.NOBEL_PHYS_DATA);
  // Step 1 by keyboard: focus the first choice, arrow to "1 in 10,000", Tab to the button, Enter.
  check(await page.isDisabled("#s1-go"), `${tag}: step 1 reveal waits for a guess`);
  await page.focus('input[name="s1"]');
  for (let i = 0; i < 3; i++) await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Enter");
  await page.waitForSelector("#s1-out:not([hidden])");
  const t1 = await page.textContent("#s1-out");
  const n100 = Math.round(1 / D.km.p_interact_1km["100TeV"]);
  check(/You picked 1 in 10,000/.test(t1) && /our toy model, trend only/.test(t1) && /Caveat/.test(t1), `${tag}: step 1 answer, guess and caveat`);
  const n2 = Number(n100.toPrecision(2)).toLocaleString("en-US");
  check(t1.includes("1\u00a0in\u00a0" + n2), `${tag}: step 1 number (1 in ${n2}) comes from data.js`);
  if (D.km.curves.interaction) check(await page.isVisible("#s1-chart svg"), `${tag}: step 1 chart drawn`);

  check(await page.isDisabled("#s2-go"), `${tag}: step 2 reveal waits for a guess`);
  await page.check('input[name="s2"][value="10"]');
  await page.click("#s2-go");
  await page.waitForSelector("#s2-out:not([hidden]) svg");
  const r0 = await page.textContent("#s2-readout");
  await slide(page, "#s2-size", 0);
  const r1 = await page.textContent("#s2-readout");
  check(/10\u00a0m on each side/.test(r1) && r1 !== r0 && /trend only/.test(r1), `${tag}: step 2 size slider updates the readout (${r1.slice(0, 60)}...)`);
  await slide(page, "#s2-size", 1000);
  check(/2\u00a0km on each side/.test(await page.textContent("#s2-readout")), `${tag}: step 2 slider reaches 2 km`);
  await slide(page, "#s2-size", 869);
  const t2 = await page.textContent("#s2-out");
  check(/Caveat/.test(t2) && /trend only/.test(t2), `${tag}: step 2 caveat`);
  check(await page.$$eval("#s2-chart text", (ts) => ["10 m", "100 m", "1 km"].every((l) => ts.some((t) => t.textContent === l))), `${tag}: step 2 marks 10 m, 100 m and 1 km`);

  await page.check('input[name="s2b"][value="0.01"]');
  await page.click("#s2b-go");
  await page.waitForSelector("#s2b-out:not([hidden])");
  const t2b = await page.textContent("#s2b-out");
  check(/straight up at 1\u00a0PeV/.test(t2b) && /Caveat/.test(t2b) && /trend only/.test(t2b), `${tag}: Earth-shield answer and caveat`);
  if (D.km.curves.transmission_1PeV) {
    await slide(page, "#s2b-angle", 20);
    check(/20° below the horizon/.test(await page.textContent("#s2b-readout")), `${tag}: Earth angle slider updates the readout`);
    await slide(page, "#s2b-angle", 90);
  }

  check(await page.isDisabled("#s3-go"), `${tag}: step 3 reveal waits for a guess`);
  await page.check('input[name="s3"][value="5"]');
  await page.click("#s3-go");
  await page.waitForSelector("#s3-out:not([hidden]) svg");
  const t3 = await page.textContent("#s3-out");
  check(/tuned constants, trend only, not IceCube.s performance/.test(t3), `${tag}: step 3 caveat ("tuned constants, trend only, not IceCube's performance")`);
  check(await page.$$eval("#s3-chart text", (ts) => ts.some((t) => /IceCube 125 m/.test(t.textContent))), `${tag}: step 3 chart marks IceCube's 125 m`);
  await slide(page, "#s3-spacing", 230);
  const r3 = await page.textContent("#s3-readout");
  check(/230\u00a0m apart/.test(r3) && /interpolated/.test(r3), `${tag}: spacing slider updates and labels interpolation`);
  const i125 = D.tel.spacings_m.indexOf(125);
  await slide(page, "#s3-spacing", 125);
  if (i125 >= 0) {
    const v = D.tel.median_error_deg.pandel[i125];
    check((await page.textContent("#s3-readout")).includes(v.toFixed(v < 1 ? 2 : 1) + "°"), `${tag}: step 3 number at 125 m comes from data.js`);
  }
  if (D.tel.event) {
    check(await page.isVisible("#s3-event svg") && await page.isVisible("#s3-sky svg"), `${tag}: example event and sky zoom drawn`);
    const nTop = await page.$$eval("#s3-event circle", (c) => c.length);
    await page.click("#s3-side");
    check(await page.getAttribute("#s3-side", "aria-pressed") === "true" && await page.isVisible("#s3-event svg"), `${tag}: side view toggles`);
    await page.click("#s3-top");
    check(nTop >= D.tel.event.hits.length, `${tag}: every hit is drawn (${D.tel.event.hits.length})`);
  }
}

const browser = await chromium.launch();
const size = ["index.html", "data.js"].reduce((a, f) => a + fs.statSync(path.join(PAGE, f)).size, 0);
check(size < 1.5e6, `index.html + data.js = ${(size / 1024).toFixed(1)} KB (< 1.5 MB)`);
const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");
check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html), "no external scripts, styles or images");
check(!/rel=["']?canonical/i.test(html), "no canonical link");
check(html.includes('property="og:url" content="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/page/"') &&
  html.includes('property="og:image" content="https://faviovazquez.github.io/nobel-2026-lab/2026/physics/page/og.jpg"'), "share tags (og:url, og:image)");
check(html.includes("Educational demo, toy models. Not research."), "toy-model banner present");
check(/href="\.\.\/glashow\/"/.test(html) && fs.existsSync(path.join(PAGE, "../glashow/index.html")), "link card to ../glashow/ resolves");
check(html.includes("https://github.com/FavioVazquez/showtime"), "Made with showtime link");

const url = pathToFileURL(path.join(PAGE, "index.html")).href;
for (const theme of THEMES) for (const width of WIDTHS) {
  const tag = `${width}px ${theme}`;
  const { ctx, page, errors, requests } = await open(browser, url, width, theme);
  const D = await page.evaluate(() => window.NOBEL_PHYS_DATA);
  check(await page.isVisible("#prelim") === D.preliminary, `${tag}: preliminary banner ${D.preliminary ? "shown" : "hidden"} (inputs: ${JSON.stringify(D.inputs)})`);
  if (!D.km || !D.tel) { check(false, `${tag}: data.js lacks an input (${JSON.stringify(D.inputs)})`); await ctx.close(); continue; }
  await answerAll(page, tag);
  const svgOk = await page.$$eval("svg[role=img]", (s) => s.length > 0 && s.every((e) => e.querySelector("title") && e.querySelector("desc")));
  check(svgOk, `${tag}: every chart has a title and description`);
  const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
  check(over <= 0, `${tag}: no sideways scrolling (overflow ${over}px)`);
  const wide = await page.$$eval("main *", (els) => els.filter((e) => !e.closest("svg") && e.getBoundingClientRect().right > window.innerWidth + 0.5).map((e) => e.tagName + "#" + e.id).slice(0, 5));
  check(wide.length === 0, `${tag}: nothing pokes past the right edge ${wide.join(" ")}`);
  check(errors.length === 0, `${tag}: no console errors ${errors.join(" | ")}`);
  check(requests.length === 0, `${tag}: no network requests ${requests.join(" ")}`);
  if (SHOTS) {
    const out = path.join(PAGE, "screenshots", `page_${width}_${theme}.png`);
    fs.mkdirSync(path.dirname(out), { recursive: true });
    await page.screenshot({ path: out, fullPage: true });
    try { // 256-colour palette keeps each full-page PNG small without visible loss on flat UI colours
      execFileSync(PY, ["-c", "import sys; from PIL import Image; p=sys.argv[1]; Image.open(p).convert('RGB').quantize(256, method=0, dither=0).save(p, optimize=True)", out]);
    } catch (e) { console.log("note: Pillow not found, screenshot left uncompressed"); }
    console.log(`     wrote ${path.relative(PAGE, out)} (${(fs.statSync(out).size / 1024).toFixed(0)} KB)`);
  }
  if (REVIEW) {
    fs.mkdirSync(REVIEW, { recursive: true });
    for (const sel of ["header", "#step1", "#step2", "#step3", "#step4", "#summary", "footer"])
      await page.locator(sel).screenshot({ path: path.join(REVIEW, `${width}_${theme}_${sel.replace("#", "")}.png`) });
    await page.click("#s3-side");
    await page.locator("#s3-out .pics").screenshot({ path: path.join(REVIEW, `${width}_${theme}_side.png`) });
    await page.click("#s3-top");
  }
  await ctx.close();
}

// A copy built with every input "final" hides the banner; one with an input missing says so and has no errors.
for (const [label, mutate, expectBanner] of [["all final", (d) => { d.inputs = { kilometre: "final", telescope: "final" }; d.preliminary = false; d.placeholder = false; }, false],
                                              ["kilometre missing", (d) => { d.inputs.kilometre = "missing"; d.km = null; d.preliminary = true; }, true]]) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "phys-page-")), tmp = path.join(root, "page");
  fs.mkdirSync(tmp); fs.mkdirSync(path.join(root, "glashow"));
  fs.copyFileSync(path.join(PAGE, "../glashow/og.jpg"), path.join(root, "glashow/og.jpg"));
  fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
  const js = fs.readFileSync(path.join(PAGE, "data.js"), "utf8");
  const d = JSON.parse(js.slice(js.indexOf("=") + 1, js.lastIndexOf(";")));
  mutate(d);
  fs.writeFileSync(path.join(tmp, "data.js"), "window.NOBEL_PHYS_DATA = " + JSON.stringify(d) + ";\n");
  const { ctx, page, errors } = await open(browser, pathToFileURL(path.join(tmp, "index.html")).href, 768, "light");
  check(await page.isVisible("#prelim") === expectBanner, `${label}: preliminary banner ${expectBanner ? "shown" : "hidden"}`);
  if (label === "kilometre missing") check(await page.isDisabled("#s1-go") && /not in this copy/.test(await page.textContent("#s1-hint")), `${label}: step 1 says the results are not in yet`);
  check(errors.length === 0, `${label}: no console errors ${errors.join(" | ")}`);
  await ctx.close();
}

if (OG) {
  const { ctx, page, errors } = await open(browser, url + "#og", 1200, "dark", 630);
  const out = path.join(PAGE, "og.jpg");
  await page.screenshot({ path: out, type: "jpeg", quality: 85, clip: { x: 0, y: 0, width: 1200, height: 630 } });
  check(errors.length === 0, `og.jpg rendered (${(fs.statSync(out).size / 1024).toFixed(0)} KB), no console errors ${errors.join(" | ")}`);
  await ctx.close();
}
await browser.close();
console.log(failures ? `${failures} check(s) failed` : "all checks passed");
process.exit(failures ? 1 : 0);
