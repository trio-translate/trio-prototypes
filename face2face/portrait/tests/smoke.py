#!/usr/bin/env python3
"""Run: python -m pip install playwright && python -m playwright install chromium
Then: python face2face/portrait/tests/smoke.py
The prototype itself has no dependencies. Tests do not use the microphone.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, shutil
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
results=[]
def check(name, condition):
    assert condition, name
    results.append(name)

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True, executable_path=shutil.which("chromium") or None)
    page=browser.new_page(viewport={"width":480,"height":850})
    errors=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.set_content((ROOT/'index.html').read_text(), wait_until='domcontentloaded')
    check('Setup precedes session', page.locator('#setup').is_visible() and not page.locator('#session').is_visible())
    page.click('#start')
    check('Language selectors hidden during session',not page.locator('#setup').is_visible())
    page.wait_for_timeout(6000)
    check('Words stream into an existing utterance',page.locator('#bottom .entries p').count()>=2)
    styles=page.locator('.entries p').evaluate_all('(els)=>els.map(e=>{let s=getComputedStyle(e);return [s.fontSize,s.fontWeight,s.color]})')
    check('All text shares one size, weight and color',len(set(map(tuple,styles)))==1 and styles[0][0]=='22px')
    check('Top reader rotated 180 degrees',page.locator('#top .reader').evaluate('(e)=>getComputedStyle(e).transform')=='matrix(-1, 0, 0, -1, 0, 0)')
    check('Section backgrounds are different',page.locator('#top').evaluate('(e)=>getComputedStyle(e).backgroundColor')!=page.locator('#bottom').evaluate('(e)=>getComputedStyle(e).backgroundColor'))
    check('No cursor pseudo-content',page.locator('.entries p').evaluate_all('(els)=>els.every(e=>getComputedStyle(e,"::after").content==="none")'))
    for _ in range(40): page.evaluate('portraitDemo.append()')
    page.wait_for_timeout(100)
    before=page.locator('#bottom .entries p').count()
    page.locator('#top-log').evaluate('(e)=>e.scrollTop=0')
    page.wait_for_timeout(100)
    page.evaluate('portraitDemo.append()')
    page.wait_for_timeout(100)
    check('Scrolling history does not pull other side away from live',page.evaluate('portraitDemo.state().following.top===false && portraitDemo.state().following.bottom===true'))
    check('New messages do not steal history position',page.locator('#top-log').evaluate('(e)=>e.scrollTop')==0)
    b=page.locator('#divider').bounding_box()
    page.mouse.move(b['x']+b['width']/2,b['y']+22)
    page.mouse.down();page.mouse.move(240,270,steps=10);page.mouse.up()
    page.wait_for_timeout(100)
    check('Divider changes viewport sizes',page.evaluate('portraitDemo.state().split')<40)
    check('Drag does not open controls',not page.locator('#controls').is_visible())
    check('Resize does not scale typography',page.locator('#bottom .entries p').first.evaluate('(e)=>getComputedStyle(e).fontSize')=='22px')
    check('Log retained across resize',page.locator('#bottom .entries p').count()>=before)
    page.mouse.click(240,650)
    check('Tap opens controls',page.locator('#controls').is_visible())
    styles=page.locator('#controls button,#controls h2').evaluate_all('(es)=>es.map(e=>getComputedStyle(e).fontSize)')
    check('Panel text also uses 22px',set(styles)=={'22px'})
    page.click('#continue')
    check('Continue returns to running session',not page.locator('#controls').is_visible() and page.evaluate('portraitDemo.state().active'))
    page.mouse.move(240,650);page.mouse.down();page.wait_for_timeout(550)
    check('Hold starts simulated recording',page.evaluate('portraitDemo.state().recording')=='bottom')
    page.mouse.up()
    check('Release ends recording without opening menu',page.evaluate('portraitDemo.state().recording') is None and not page.locator('#controls').is_visible())
    page.mouse.move(240,650);page.mouse.down();page.wait_for_timeout(550)
    count=page.evaluate('portraitDemo.state().utterances')
    page.evaluate('window.dispatchEvent(new Event("blur"))');page.mouse.up()
    check('Interrupted hold cancels without appending a recording',page.evaluate('portraitDemo.state().recording') is None and page.evaluate('portraitDemo.state().utterances')==count)
    page.mouse.click(240,120)
    check('Top participant receives rotated panel',page.locator('#controls').get_attribute('data-side')=='top')
    check('History controls expose return to live',page.locator('#jump').is_visible())
    page.click('#jump')
    check('Jump restores independent live follow',page.evaluate('portraitDemo.state().following.top'))
    page.locator('#divider').focus();page.keyboard.press('End')
    check('Keyboard divider cannot collapse either participant',page.evaluate('portraitDemo.state().split')==75)
    page.keyboard.press('Enter')
    check('Keyboard reset restores symmetric split',page.evaluate('portraitDemo.state().split')==50)
    page.evaluate('portraitDemo.openControls("bottom")');page.click('#stop')
    check('Stop ends session and returns to setup',not page.evaluate('portraitDemo.state().active') and page.locator('#setup').is_visible())
    check('No JavaScript errors',not errors)
    browser.close()
for asset in sorted((ROOT/'mockups').glob('*.svg')):
    nodes=ET.parse(asset).getroot().findall('.//{http://www.w3.org/2000/svg}text')
    styles={(n.get('font-size'),n.get('font-weight'),n.get('fill')) for n in nodes}
    check('Uniform SVG typography: '+asset.stem,styles=={('22','400','#edf3f5')})
print(json.dumps({'passed':len(results),'checks':results},indent=2))
