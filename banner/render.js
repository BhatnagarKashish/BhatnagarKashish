// Renders banner/hero.html frame-by-frame for a seamless 6s loop.
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const N = 75, dir = path.join(__dirname, 'frames');
  fs.mkdirSync(dir, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 400 } });
  await p.goto('file://' + path.join(__dirname, 'hero.html'));
  await p.waitForFunction('window.ready');
  const el = await p.$('#c');
  for (let i = 0; i < N; i++) {
    await p.evaluate(t => draw(t), 6 * i / N);
    await el.screenshot({ path: path.join(dir, `f${String(i).padStart(3, '0')}.png`) });
  }
  await b.close();
})();
