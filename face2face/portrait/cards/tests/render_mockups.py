"""Capture actual prototype states. Each PNG is separate and has true outer alpha."""
import os
from pathlib import Path
import shutil
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
STATES = {
    'cards-live': '',
    'cards-resized': 'portraitPrototype.setSplit(.67)',
    'cards-controls': "portraitPrototype.openMenu('bottom')",
    'cards-top-controls': "portraitPrototype.openMenu('top')",
    'cards-recording': "portraitPrototype.recording('bottom')",
    'divider-live': "document.getElementById('layout').value='divider'; portraitPrototype.start({auto:false,count:3})",
}


def main():
    target = ROOT / 'mockups'
    target.mkdir(exist_ok=True)
    with sync_playwright() as pw:
        executable = os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        browser = pw.chromium.launch(**({'executable_path': executable} if executable else {}), args=['--no-sandbox'])
        context = browser.new_context(viewport={'width': 520, 'height': 884}, device_scale_factor=2)
        for name, action in STATES.items():
            page = context.new_page()
            page.set_content(HTML)
            page.evaluate('portraitPrototype.start({auto:false,count:3})')
            if action:
                page.evaluate(action)
            page.wait_for_timeout(100)
            page.locator('.device').screenshot(path=str(target / f'{name}.png'), omit_background=True)
            page.close()
        browser.close()


if __name__ == '__main__':
    main()
