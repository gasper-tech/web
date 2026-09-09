// Step 1 of the preview build: run the real page in Chromium and capture the
// hydrated DOM, the runtime-injected stylesheet, and each state of the booking
// form. Writes .preview-cache/ for tools/make-preview.py to consume.
//
//   npm i -D playwright-core        (Chromium must already be on the machine)
//   node tools/snapshot-preview.js
const { chromium } = require('playwright-core');
const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const CACHE = path.join(ROOT, '.preview-cache');
const EXE = process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

(async () => {
  fs.mkdirSync(CACHE, { recursive: true });
  const b = await chromium.launch({ executablePath: EXE });
  const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  await p.goto('file://' + path.join(ROOT, 'casa-orquidea.html'), { waitUntil: 'load' });
  await p.waitForTimeout(2500);

  const card = () => p.evaluate(() => ({ form: document.querySelector('.pad-card').innerHTML }));
  const step1 = await card();
  const shell = await p.evaluate(() => ({
    styles: [...document.head.querySelectorAll('style')].map(s => s.textContent).join('\n'),
    html: document.querySelector('.pad-card').closest('div[style*="font-family"]').outerHTML,
  }));

  for (const n of ['purpose', 'propertyType', 'area', 'priority', 'budget', 'timeline'])
    await p.selectOption(`select[name="${n}"]`, { index: 1 });
  await p.locator('button:has-text("Continue")').click();
  await p.waitForTimeout(400);
  const step2 = await card();

  for (const [n, v] of [['firstName', 'A'], ['lastName', 'B'], ['phone', '1'],
                        ['email', 'a@b.co'], ['dealBreaker', 'x']])
    await p.fill(`[name="${n}"]`, v);
  for (const n of ['country', 'contactMethod'])
    await p.selectOption(`select[name="${n}"]`, { index: 1 });
  await p.locator('button:has-text("Request a viewing")').click();
  await p.waitForTimeout(600);
  const thanks = await card();

  // The hero photo lives in the bundle's image-slot state, as a data: URI.
  const bundle = fs.readFileSync(path.join(ROOT, 'casa-orquidea.html'), 'utf8')
    .replace(/\\u002F/g, '/').replace(/\\n/g, '\n').replace(/\\"/g, '"');
  const state = JSON.parse(/__IMAGE_SLOT_STATE = (\{.*?\});/s.exec(bundle)[1]);

  fs.writeFileSync(path.join(CACHE, 'snapshot.json'),
    JSON.stringify({ shell, step1, step2, thanks }, null, 1));
  fs.writeFileSync(path.join(CACHE, 'hero_uri.txt'), state['orq-hero'].u);
  console.log('snapshot written to .preview-cache/');
  await b.close();
})();
