// Renderon rritje-academy.html në PDF (A4) + PNG për kontroll vizual.
// Përdorimi: NODE_PATH=$(npm root -g) node render.js [--png]
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 794, height: 1123 }, deviceScaleFactor: 1.4 });
  await page.goto('file://' + path.join(__dirname, 'rritje-academy.html'), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  // kontroll: asnjë element nuk del jashtë faqes së vet
  const overflow = await page.evaluate(() => [...document.querySelectorAll('.page')].map((p, i) => {
    const pr = p.getBoundingClientRect();
    const foot = p.querySelector('.pf');
    const limit = foot ? foot.getBoundingClientRect().top : pr.bottom;
    let max = 0;
    p.querySelectorAll('*').forEach(e => { if (e.closest('.pf') || e.closest('.cover')) return; const r = e.getBoundingClientRect(); if (r.height) max = Math.max(max, r.bottom); });
    return { page: i + 1, spare: Math.round(limit - max) };
  }));
  console.log(overflow.map(o => `${o.page}:${o.spare}`).join('  '));
  await page.pdf({ path: path.join(__dirname, 'Rritje-Academy-Plani-Strategjik.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  if (process.argv.includes('--png')) {
    const pages = await page.$$('.page');
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: process.env.PNG_DIR + `/p${String(i + 1).padStart(2, '0')}.png` });
  }
  await browser.close();
})();
