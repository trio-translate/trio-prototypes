#!/usr/bin/env python3
"""Export separate PNGs and portable SVGs from the self-contained prototype.
Requires Playwright + Chromium. No font files or network assets are packaged.
PNG exports use real alpha outside the device; SVGs have no canvas background.
"""
from pathlib import Path
import html
import shutil
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
STATES = ('live','resized','controls','controls-top','recording')

def svg_from_snapshot(data):
    width, height, pad = 432, 768, 16
    h = height * data['split'] / 100
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="464" height="800" viewBox="0 0 464 800" role="img" aria-label="Face-to-face portrait: {data["mode"]}">',
      '<title>Face-to-face portrait — uniform 22px text</title>',
      '<defs><clipPath id="screen"><rect x="16" y="16" width="432" height="768" rx="34"/></clipPath>',
      f'<clipPath id="top"><rect width="432" height="{h:g}"/></clipPath>',
      f'<clipPath id="bottom"><rect width="432" height="{height-h:g}"/></clipPath></defs>',
      '<rect x="9" y="9" width="446" height="782" rx="41" fill="#11181c"/>',
      '<g clip-path="url(#screen)">',
      f'<rect x="16" y="16" width="432" height="{h:g}" fill="#102923"/>',
      f'<rect x="16" y="{16+h:g}" width="432" height="{height-h:g}" fill="#102332"/>']
    # A single typography definition covers every text node in every state.
    def text(x,y,value):
        return f'<text x="{x:g}" y="{y:g}" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="400" fill="#edf3f5">{html.escape(value)}</text>'
    for name in ('top','bottom'):
        dh = h if name=='top' else height-h
        transform = f'translate(16 16) translate(432 {h:g}) rotate(180)' if name=='top' else f'translate(16 {16+h:g})'
        parts.append(f'<g transform="{transform}" clip-path="url(#{name})">')
        y = 28 + 22 - data[name]['scrollTop']
        for lines in data[name]['lines']:
            for line in lines:
                parts.append(text(28,y,line)); y += 33
            y += 16
        if data['mode']=='recording' and name=='bottom':
            parts.append(f'<rect x="1.5" y="1.5" width="429" height="{dh-3:g}" fill="none" stroke="#8be0d0" stroke-width="3"/>')
            parts.append(f'<rect x="24" y="{dh-78:g}" width="384" height="48" rx="10" fill="#10232b"/>')
            parts.append(text(155,dh-47,'Recording…'))
        parts.append('</g>')
    parts.append(f'<path d="M16 {16+h:g}H448" stroke="#98aeb4" stroke-width="1"/>')
    parts.append(f'<rect x="213" y="{14+h:g}" width="38" height="4" rx="2" fill="#98aeb4"/>')
    if data['mode'].startswith('controls'):
        parts.append('<rect x="16" y="16" width="432" height="768" fill="#000" opacity=".48"/>')
        rotation='rotate(180 232 400)' if data['mode']=='controls-top' else ''
        parts.append(f'<g transform="{rotation}"><rect x="57" y="267" width="350" height="266" rx="20" fill="#172c37" stroke="#758b97"/>')
        t = ['Sessão','Continuar','Parar e voltar'] if data['mode']=='controls-top' else ['Session','Continue','Stop and go back']
        parts.append(text(80,312,t[0]))
        for y,label in [(342,t[1]),(426,t[2])]:
            parts.append(f'<rect x="80" y="{y}" width="304" height="58" rx="12" fill="#1b303c" stroke="#748591"/>')
            parts.append(f'<text x="232" y="{y+37}" text-anchor="middle" font-family="Arial,Helvetica,sans-serif" font-size="22" font-weight="400" fill="#edf3f5">{label}</text>')
        parts.append('</g>')
    parts += ['</g>','<rect x="16" y="16" width="432" height="768" rx="34" fill="none" stroke="#50616b"/>','</svg>']
    return '\n'.join(parts)+'\n'

with sync_playwright() as p:
    browser=p.chromium.launch(headless=True,executable_path=shutil.which('chromium') or None)
    for mode in STATES:
        page=browser.new_page(viewport={'width':480,'height':816},device_scale_factor=2)
        source=(ROOT/'index.html').read_text().replace('new URLSearchParams(location.search)',f'new URLSearchParams("?snapshot={mode}")')
        # Screenshot layout is the same fixed 432 x 768 layout as the SVG, not a phone-width resize.
        page.set_content(source.replace('@media(min-width:540px)','@media(min-width:0px)'))
        page.wait_for_timeout(120)
        page.screenshot(path=str(ROOT/'mockups'/f'{mode}.png'),omit_background=True,clip={'x':8,'y':8,'width':464,'height':800})
        image=Image.open(ROOT/'mockups'/f'{mode}.png')
        # A native dialog backdrop covers the browser canvas too; trim only the outside of the device.
        image=image.convert('RGBA')
        mask=Image.new('L',(image.width*4,image.height*4),0)
        ImageDraw.Draw(mask).rounded_rectangle((9*8,9*8,455*8,791*8),radius=41*8,fill=255)
        mask=mask.resize(image.size,Image.Resampling.LANCZOS)
        image.putalpha(ImageChops.multiply(image.getchannel('A'),mask))
        image.save(ROOT/'mockups'/f'{mode}.png')
        assert image.mode=='RGBA' and image.getextrema()[3][0]==0
        data=page.evaluate('''() => {
          const canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font='400 22px Arial';
          const result={split:portraitDemo.state().split};
          for(const name of ['top','bottom']) {
            const log=document.getElementById(name+'-log');
            result[name]={scrollTop:log.scrollTop,lines:[...log.querySelectorAll('p')].map(p=>{
              const lines=[];let line='';
              for(const word of p.textContent.split(' ')) {const trial=line?line+' '+word:word;
                if(ctx.measureText(trial).width>376&&line){lines.push(line);line=word;}else line=trial;}
              if(line) lines.push(line);return lines;
            })};
          }return result;
        }''')
        data['mode']=mode
        (ROOT/'mockups'/f'{mode}.svg').write_text(svg_from_snapshot(data))
        page.close()
    browser.close()
print('Rendered 5 separate SVGs and 5 RGBA PNGs; every text style is 22px / 400 / #edf3f5.')
