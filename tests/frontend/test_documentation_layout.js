'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const puppeteer = require('puppeteer');

const QUICK_START = path.resolve(__dirname, '..', '..', 'docs', 'quick-start.html');
const EXPECTED_SETUP_COMMANDS = [
  '.\\setup-towerscout.cmd -Engine docker -Gpu off',
  '.\\setup-towerscout.cmd -Engine docker -Gpu on',
  '.\\setup-towerscout.cmd -Engine podman -Gpu off',
  '.\\setup-towerscout.cmd -Engine podman -Gpu on'
];

function findBrowserExecutable() {
  const candidates = [
    process.env.TOWERSCOUT_EXECUTABLE_PATH,
    'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe',
    'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  ].filter(Boolean);
  return candidates.find((candidate) => fs.existsSync(candidate));
}

async function inspectViewport(page, width) {
  await page.setViewport({ width, height: 900, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(QUICK_START).href, { waitUntil: 'load' });

  return page.evaluate((expectedCommands) => {
    const grid = document.querySelector('[aria-label="Setup commands by configuration"]');
    if (!grid) {
      return { error: 'Setup command grid was not found.' };
    }

    const cards = [...grid.querySelectorAll('article')];
    const commandElements = cards.map((card) => card.querySelector('pre'));
    const commands = cards.map((card) => card.querySelector('code')?.textContent.trim());
    const rectangles = cards.map((card) => card.getBoundingClientRect());

    return {
      pageHasHorizontalOverflow:
        document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
      commands,
      expectedCommands,
      commandsNeedHorizontalScroll: commandElements.map(
        (element) => !element || element.scrollWidth > element.clientWidth + 1
      ),
      cardsOverlap: rectangles.some((rectangle, index) => {
        if (index === 0) return false;
        const previous = rectangles[index - 1];
        return rectangle.top < previous.bottom - 1;
      })
    };
  }, EXPECTED_SETUP_COMMANDS);
}

async function main() {
  const executablePath = findBrowserExecutable();
  const browser = await puppeteer.launch({
    headless: true,
    ...(executablePath ? { executablePath } : {})
  });
  try {
    const page = await browser.newPage();
    for (const width of [1440, 720]) {
      const result = await inspectViewport(page, width);
      if (result.error) throw new Error(`${width}px: ${result.error}`);
      if (result.pageHasHorizontalOverflow) {
        throw new Error(`${width}px: the document has horizontal overflow.`);
      }
      if (JSON.stringify(result.commands) !== JSON.stringify(EXPECTED_SETUP_COMMANDS)) {
        throw new Error(`${width}px: one or more setup commands are incomplete.`);
      }
      if (result.commandsNeedHorizontalScroll.some(Boolean)) {
        throw new Error(`${width}px: one or more setup commands require horizontal scrolling.`);
      }
      if (result.cardsOverlap) {
        throw new Error(`${width}px: setup command cards overlap.`);
      }
      console.log(`PASS documentation layout at ${width}px`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exitCode = 1;
});
