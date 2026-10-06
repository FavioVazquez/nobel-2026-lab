// Headless-Chrome check of the "try it" page (educational demo, toy model).
// Opens index.html from file://, answers every step (step 1 by keyboard only), checks for console errors,
// network requests, sideways scrolling and the optional recruitment panel, and writes screenshots.
//
//   NODE_PATH=<dir containing playwright> node tests/test_page.cjs [--shots]     (from 2026/medicine/page/)
const { chromium } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");
const { execFileSync } = require("child_process");

const PAGE = path.resolve(__dirname, "..");
const SHOTS = process.argv.includes("--shots");
const REVIEW = process.argv.includes("--review") ? process.argv[process.argv.indexOf("--review") + 1] : null; // per-section crops
const PY = process.env.PYTHON || "python3"; // needs numpy (build_data.py) and Pillow (--shots)
const WIDTHS = [360, 768, 1440];
const THEMES = ["light", "dark"];
let failures = 0;
const check = (ok, msg) => { console.log(`${ok ? "ok  " : "FAIL"} ${msg}`); if (!ok) failures++; };

async function answerAll(page) {
  // Step 1 by keyboard: focus the first radio, arrow to red, Tab to the button, Enter.
  await page.focus('input[name="s1"]');
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("ArrowRight");
  await page.keyboard.press("Tab");
  await page.keyboard.press("Enter");
  await page.waitForSelector("#s1-out:not([hidden]) svg");
  // Step 2: 30 % duty (interpolated), 10 mW, guess 1.5 C.
  await page.fill("#s2-duty", "30");
  await page.dispatchEvent("#s2-duty", "input");
  await page.fill("#s2-guess", "1.5");
  await page.click("#s2-go");
  await page.waitForSelector("#s2-out:not([hidden]) svg");
  // Step 3: rates 80 / 100 / 20 Hz.
  for (const [i, r, g] of [[0, "80", "yes"], [1, "100", "yes"], [2, "20", "no"]]) {
    await page.selectOption(`#s3-rate${i}`, r);
    await page.check(`input[name="s3p${i}"][value="${g}"]`);
  }
  await page.click("#s3-go");
  await page.waitForSelector("#s3-out:not([hidden]) svg");
  // Bonus: blue vs amber only; red appears only as a labelled toy upper bound.
  await page.check('input[name="s4"][value="470"]');
  await page.click("#s4-go");
  await page.waitForSelector("#s4-out:not([hidden]) svg");
}

async function run(browser, url, width, theme, label) {
  const ctx = await browser.newContext({ viewport: { width, height: 900 }, colorScheme: theme, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = [], requests = [];
  page.on("console", (m) => { if (m.type() === "error") errors.push(m.text()); });
  page.on("pageerror", (e) => errors.push(String(e)));
  page.on("request", (r) => { if (!r.url().startsWith("file://")) requests.push(r.url()); });
  await page.goto(url);
  return { ctx, page, errors, requests };
}

(async () => {
  const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
  const size = fs.statSync(path.join(PAGE, "index.html")).size + fs.statSync(path.join(PAGE, "data.js")).size;
  check(size < 1.5e6, `index.html + data.js = ${(size / 1024).toFixed(1)} KB (< 1.5 MB)`);
  const html = fs.readFileSync(path.join(PAGE, "index.html"), "utf8");
  check(!/<(script|link|img)[^>]+(src|href)="https?:/i.test(html), "no external scripts, styles or images");
  check(html.includes("Educational demo, toy model. Not research, not for lab or clinical use."), "toy-model banner present");

  const url = "file://" + path.join(PAGE, "index.html");
  for (const theme of THEMES) for (const width of WIDTHS) {
    const tag = `${width}px ${theme}`;
    const { ctx, page, errors, requests } = await run(browser, url, width, theme);
    const hasRecruit = await page.evaluate(() => !!window.NOBEL_MED_DATA.recruitment);
    check(hasRecruit && await page.isVisible("#step4"), `${tag}: bonus panel shown (data.js built with --recruitment)`);
    check(await page.isDisabled("#s1-go"), `${tag}: reveal is disabled before a prediction`);
    await answerAll(page);
    const t1 = await page.textContent("#s1-out");
    check(/Red light reaches deepest/.test(t1) && /absorbed by blood/.test(t1), `${tag}: step 1 answer and caveat`);
    const t2 = await page.textContent("#s2-out");
    check(/interpolated/.test(t2) && /Estimate\./.test(t2), `${tag}: step 2 labels the interpolation`);
    const t3 = await page.textContent("#s3-out");
    check(/of 3 guesses match/.test(t3) && /simplified/.test(t3), `${tag}: step 3 results`);
    check(/resonance of this toy cell, not of the light switch/.test(t3) && /at least 20 Hz/.test(t3) && /read the order, not the numbers/.test(t3),
      `${tag}: step 3 carries the resonance note and the ChrimsonR statement`);
    const t4 = await page.textContent("#s4-out");
    check(/toy upper bound/.test(t4) && (await page.$$('input[name="s4"][value="635"]')).length === 0,
      `${tag}: bonus panel compares blue and amber; red only as a labelled toy upper bound`);
    const num = await page.evaluate(() => { const D = window.NOBEL_MED_DATA; return [D.light.reach_mm["470"]["3"], D.speed.switches["ChR2 (Williams 2013)"].max_following_rate_Hz]; });
    check(t1.includes(num[0].toFixed(2)) && t3.includes(`ChR2 ${num[1]}`), `${tag}: stated numbers come from data.js`);
    const svgOk = await page.$$eval("svg[role=img]", (s) => s.every((e) => e.querySelector("title") && e.querySelector("desc")));
    check(svgOk, `${tag}: every chart has a title and description`);
    const over = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth);
    check(over <= 0, `${tag}: no sideways scrolling (overflow ${over}px)`);
    check(errors.length === 0, `${tag}: no console errors ${errors.join(" | ")}`);
    check(requests.length === 0, `${tag}: no network requests ${requests.join(" ")}`);
    if (SHOTS) {
      const out = path.join(PAGE, "screenshots", `page_${width}_${theme}.png`);
      await page.screenshot({ path: out, fullPage: true });
      // 256-colour palette keeps each full-page PNG (bonus panel open) under 600 KB without visible loss on flat UI colours
      execFileSync(PY, ["-c", "import sys; from PIL import Image; p=sys.argv[1]; Image.open(p).convert('RGB').quantize(256, method=0, dither=0).save(p, optimize=True)", out]);
      const kb = fs.statSync(out).size / 1024;
      check(kb < 600, `wrote ${path.relative(PAGE, out)} (${kb.toFixed(0)} KB, < 600 KB)`);
    }
    if (REVIEW) for (const sel of ["header", "#step1", "#step2", "#step3", "#step4", "#summary", "footer"]) {
      await page.locator(sel).screenshot({ path: path.join(REVIEW, `${width}_${theme}_${sel.replace("#", "")}.png`) });
    }
    await ctx.close();
  }

  // Extrapolation label below 10 % duty.
  {
    const { ctx, page } = await run(browser, url, 768, "light");
    await page.fill("#s2-duty", "5");
    await page.dispatchEvent("#s2-duty", "input");
    await page.fill("#s2-guess", "0.2");
    await page.click("#s2-go");
    check(/Extrapolation\./.test(await page.textContent("#s2-out")), "step 2 says when it extrapolates (5 % duty)");
    await ctx.close();
  }

  // Bonus panel: a page copy built WITHOUT recruitment data must hide it (the shipped data.js includes it).
  {
    const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "page-norecruit-"));
    fs.copyFileSync(path.join(PAGE, "index.html"), path.join(tmp, "index.html"));
    execFileSync(PY, [path.join(PAGE, "build_data.py"), "--out", path.join(tmp, "data.js")]);
    const { ctx, page, errors } = await run(browser, "file://" + path.join(tmp, "index.html"), 768, "light");
    check(await page.isHidden("#step4"), "bonus panel hidden without recruitment data");
    check(errors.length === 0, `no-recruitment copy: no console errors ${errors.join(" | ")}`);
    await ctx.close();
  }

  await browser.close();
  console.log(failures ? `${failures} check(s) failed` : "all checks passed");
  process.exit(failures ? 1 : 0);
})();
