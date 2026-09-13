"""Browser checks for both prototype variants. No live microphone/network is used."""
import os
from pathlib import Path
import shutil
import unittest
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')


class PortraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        executable = os.environ.get('CHROMIUM_EXECUTABLE') or shutil.which('chromium')
        cls.browser = cls.pw.chromium.launch(**({'executable_path': executable} if executable else {}), args=['--no-sandbox'])

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 432, 'height': 844}, has_touch=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.set_content(HTML)
        self.page.evaluate('portraitPrototype.start({auto:false,count:3})')
        self.page.wait_for_timeout(60)

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def state(self):
        return self.page.evaluate('portraitPrototype.snapshot()')

    def api(self, expression):
        result = self.page.evaluate(expression)
        self.page.wait_for_timeout(60)
        return result

    def typography(self):
        return self.page.locator('.log p').evaluate_all("els => els.map(e => {const s=getComputedStyle(e);return [s.fontSize,s.fontWeight,s.color]})")

    def test_exactly_two_cards(self):
        self.assertEqual(self.page.locator('.card').count(), 2)
        self.assertEqual(self.state()['layout'], 'cards')

    def test_no_line_or_handle_in_cards(self):
        self.assertEqual(self.page.locator('#split').evaluate("e=>getComputedStyle(e,'::before').content"), 'none')
        self.assertEqual(self.page.locator('#split').evaluate("e=>getComputedStyle(e,'::after').content"), 'none')
        self.assertEqual(self.page.locator('#split').evaluate("e=>getComputedStyle(e).backgroundColor"), 'rgba(0, 0, 0, 0)')

    def test_equal_typography_both_languages(self):
        self.assertEqual(len(set(map(tuple, self.typography()))), 1)
        self.assertEqual(self.typography()[0][0:2], ['22px','400'])

    def test_resize_never_changes_type(self):
        before = self.typography()
        for split in [.2,.33,.5,.67,.8]:
            self.api(f'portraitPrototype.setSplit({split})')
            self.assertEqual(self.typography(), before)

    def test_top_rotated(self):
        self.assertEqual(self.page.locator('#reader-top').evaluate('e=>getComputedStyle(e).transform'), 'matrix(-1, 0, 0, -1, 0, 0)')
        self.assertEqual(self.page.locator('#reader-bottom').evaluate('e=>getComputedStyle(e).transform'), 'none')

    def test_distinct_backgrounds(self):
        colors = self.page.locator('.card').evaluate_all('els=>els.map(e=>getComputedStyle(e).backgroundColor)')
        self.assertNotEqual(*colors)

    def test_no_persistent_controls_language_names_cursors(self):
        self.assertEqual(self.page.locator('#stack button:visible, #stack select:visible').count(), 0)
        text = self.page.locator('#stack').inner_text()
        for forbidden in ['English', 'Português', 'Hold to record', 'Recording demo', '|']:
            self.assertNotIn(forbidden, text)

    def test_separate_scroll_positions_and_follow(self):
        self.api('portraitPrototype.append(70)')
        top = self.page.locator('#reader-top').evaluate('e=>e.scrollTop')
        self.page.locator('#reader-bottom').evaluate('e=>e.scrollTop = 130')
        self.page.wait_for_timeout(80)
        self.assertFalse(self.state()['follow']['bottom'])
        self.assertEqual(top, self.page.locator('#reader-top').evaluate('e=>e.scrollTop'))
        self.api('portraitPrototype.append(1)')
        self.assertEqual(130, self.page.locator('#reader-bottom').evaluate('e=>e.scrollTop'))
        self.assertGreater(self.page.locator('#reader-top').evaluate('e=>e.scrollTop'), top)

    def test_long_log_retained(self):
        self.api('portraitPrototype.append(500)')
        self.assertEqual(self.state()['count'], 503)
        for side in ['top','bottom']:
            self.assertEqual(self.page.locator(f'#log-{side} p').count(), 503)
        self.assertEqual(self.state()['entries'][0]['en'], 'That sounds like a great idea.')

    def test_pending_revision_in_place_and_uniform(self):
        self.api('portraitPrototype.stream()')
        id_before = self.state()['entries'][-1]['id']
        count = self.state()['count']
        self.api("portraitPrototype.revise({en:'Shall we meet at two?',pt:'Vamos nos encontrar às duas?'})")
        self.api("portraitPrototype.revise({en:'Shall we meet at three?',pt:'Vamos nos encontrar às três?'})")
        self.assertEqual(self.state()['count'], count)
        self.assertEqual(self.state()['entries'][-1]['id'], id_before)
        self.assertEqual(len(set(map(tuple,self.typography()))), 1)
        self.assertFalse(self.state()['entries'][-1]['settled'])
        self.api('portraitPrototype.settle()')
        self.assertTrue(self.state()['entries'][-1]['settled'])

    def test_completed_entries_unchanged(self):
        old = self.state()['entries']
        self.api('portraitPrototype.stream()')
        self.api("portraitPrototype.revise({en:'A different draft',pt:'Outro rascunho'})")
        self.assertEqual(self.state()['entries'][:len(old)], old)

    def test_tap_opens_menu_and_back_dismisses(self):
        self.page.locator('#reader-bottom').click(position={'x': 30,'y': 80})
        self.assertTrue(self.state()['menu'])
        self.page.locator('#back').click()
        self.assertFalse(self.state()['menu'])
        self.assertTrue(self.state()['running'])

    def test_top_controls_rotated_and_localized(self):
        self.page.locator('#reader-top').click(position={'x': 30,'y': 80})
        self.assertEqual(self.page.locator('#sheet').get_attribute('data-side'), 'top')
        self.assertEqual(self.page.locator('#stop-label').inner_text(), 'Parar sessão')
        self.assertEqual(self.page.locator('#sheet').evaluate('e=>getComputedStyle(e).transform'), 'matrix(-1, 0, 0, -1, 0, 0)')

    def test_all_menu_text_matches_log_size(self):
        self.api("portraitPrototype.openMenu('bottom')")
        sizes = self.page.locator('#sheet button').evaluate_all('els=>els.filter(e=>!e.hidden).map(e=>getComputedStyle(e).fontSize)')
        self.assertEqual(set(sizes), {'22px'})

    def test_hold_release_does_not_open_menu(self):
        rect = self.page.locator('#reader-bottom').bounding_box()
        self.page.mouse.move(rect['x']+35, rect['y']+80)
        self.page.mouse.down()
        self.page.wait_for_timeout(490)
        self.assertEqual(self.state()['recording'], 'bottom')
        self.page.mouse.up()
        self.assertIsNone(self.state()['recording'])
        self.assertFalse(self.state()['menu'])
        self.page.wait_for_timeout(2500)
        self.assertEqual(self.state()['count'], 4)
        self.assertEqual(self.state()['entries'][-1]['en'], 'Let’s take the quiet path along the river.')

    def test_escape_cancels_recording_without_appending(self):
        before = self.state()['count']
        self.page.locator('#reader-bottom').focus()
        self.page.keyboard.down('Space')
        self.assertEqual(self.state()['recording'], 'bottom')
        self.page.keyboard.press('Escape')
        self.page.keyboard.up('Space')
        self.assertIsNone(self.state()['recording'])
        self.assertEqual(self.state()['count'], before)

    def test_mouse_scroll_does_not_open_menu_or_record(self):
        self.api('portraitPrototype.append(30)')
        rect = self.page.locator('#reader-bottom').bounding_box()
        self.page.mouse.move(rect['x']+40,rect['y']+80)
        self.page.mouse.down()
        self.page.mouse.move(rect['x']+40,rect['y']+210, steps=5)
        self.page.wait_for_timeout(480)
        self.page.mouse.up()
        self.assertFalse(self.state()['menu'])
        self.assertIsNone(self.state()['recording'])
        self.assertFalse(self.state()['follow']['bottom'])

    def test_gap_drag_changes_split_only(self):
        rect = self.page.locator('#split').bounding_box()
        before = self.typography()
        self.page.mouse.move(rect['x']+rect['width']/2,rect['y']+22)
        self.page.mouse.down()
        self.page.mouse.move(rect['x']+rect['width']/2,rect['y']+155,steps=8)
        self.page.mouse.up()
        self.assertGreater(self.state()['split'], .6)
        self.assertEqual(self.typography(), before)
        self.assertFalse(self.state()['menu'])
        self.assertIsNone(self.state()['recording'])

    def test_accessible_resize_clamps(self):
        self.page.locator('#split').focus()
        self.page.keyboard.press('End')
        self.assertEqual(self.state()['split'], .8)
        self.page.keyboard.press('ArrowDown')
        self.assertEqual(self.state()['split'], .8)
        self.page.keyboard.press('Home')
        self.assertEqual(self.state()['split'], .2)

    def test_jump_to_latest_and_equal_space(self):
        self.api('portraitPrototype.append(30)')
        self.page.locator('#reader-bottom').evaluate('e=>e.scrollTop=0')
        self.page.wait_for_timeout(80)
        self.api("portraitPrototype.openMenu('bottom')")
        self.assertTrue(self.page.locator('#latest').is_visible())
        self.page.locator('#latest').click()
        self.assertTrue(self.state()['follow']['bottom'])
        self.api('portraitPrototype.setSplit(.8)')
        self.api("portraitPrototype.openMenu('bottom')")
        self.page.locator('#balance').click()
        self.assertEqual(self.state()['split'], .5)

    def test_stop_review_and_start_have_exits(self):
        count = self.state()['count']
        self.api("portraitPrototype.openMenu('bottom')")
        self.page.locator('#stop').click()
        self.assertTrue(self.page.locator('#setup').is_visible())
        self.assertFalse(self.state()['running'])
        self.page.locator('#review').click()
        self.assertEqual(self.state()['count'], count)
        self.assertTrue(self.page.locator('#stack').is_visible())
        self.api("portraitPrototype.openMenu('bottom')")
        self.assertEqual(self.page.locator('#stop-label').inner_text(), 'Back to setup')
        self.page.locator('#stop').click()
        self.page.locator('#start').click()
        self.assertTrue(self.state()['running'])
        self.assertEqual(self.state()['count'], 2)

    def test_language_selection_only_before_start(self):
        self.api('portraitPrototype.stop()')
        self.page.locator('#lower-language').select_option('pt')
        self.assertEqual(self.page.locator('#upper-language').input_value(), 'en')
        self.page.locator('#start').click()
        self.assertEqual(self.state()['languages'], {'top':'en','bottom':'pt'})
        self.assertTrue(self.page.locator('#log-bottom').inner_text().startswith('Parece uma ótima ideia.'))

    def test_legacy_variant_preserved_same_typography(self):
        self.page.evaluate("document.getElementById('layout').value='divider'; portraitPrototype.start({auto:false,count:3})")
        self.assertEqual(self.state()['layout'],'divider')
        self.assertEqual(self.page.locator('#split').evaluate("e=>getComputedStyle(e,'::before').height"), '1px')
        self.assertEqual(len(set(map(tuple,self.typography()))), 1)

    def test_native_touch_scrolls_both_orientations_without_actions(self):
        self.api('portraitPrototype.append(40)')
        session = self.context.new_cdp_session(self.page)
        for side in ['bottom', 'top']:
            reader = self.page.locator('#reader-' + side)
            rect = reader.bounding_box()
            x = rect['x'] + 100
            y = rect['y'] + (100 if side == 'bottom' else rect['height'] - 100)
            delta = 140 if side == 'bottom' else -140
            before = reader.evaluate('e=>e.scrollTop')
            session.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': x, 'y': y}]})
            for i in range(1, 9):
                session.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': x, 'y': y + delta * i / 8}]})
                self.page.wait_for_timeout(20)
            session.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
            self.page.wait_for_timeout(450)
            self.assertLess(reader.evaluate('e=>e.scrollTop'), before)
            self.assertFalse(self.state()['menu'])
            self.assertIsNone(self.state()['recording'])

    def test_narrow_phone_no_type_scaling_or_horizontal_overflow(self):
        before = self.typography()[0]
        for width,height in [(320,568),(375,667),(390,844)]:
            self.page.set_viewport_size({'width':width,'height':height})
            self.page.wait_for_timeout(60)
            self.assertEqual(self.typography()[0],before)
            self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            self.assertTrue(self.page.locator('#reader-bottom').evaluate('e=>e.scrollWidth<=e.clientWidth'))

    def test_modal_focus_trapped_and_escape_restores(self):
        self.page.locator('#reader-bottom').focus()
        self.page.keyboard.press('Enter')
        self.page.keyboard.press('Shift+Tab')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'balance')
        self.page.keyboard.press('Tab')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'stop')
        self.page.keyboard.press('Escape')
        self.assertEqual(self.page.evaluate('document.activeElement.id'), 'reader-bottom')


if __name__ == '__main__':
    unittest.main(verbosity=2)
