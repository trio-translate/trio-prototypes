# Separate preview states

The SVG files are lightweight vector companions to the executable prototype. They all use exactly 22 px, weight 400 and the same text color. The HTML remains the interaction and layout source of truth; SVG font fallback can change glyph metrics.

- [Cards, balanced](cards-live.svg)
- [Cards, resized](cards-resized.svg)
- [Lower controls](cards-controls.svg)
- [Upper controls](cards-top-controls.svg)
- [Transient recording simulation](cards-recording.svg)
- [Divider comparison](divider-live.svg)

Run `python3 face2face/portrait/cards/tests/render_mockups.py` for exact browser PNG screenshots of these six states. The downloadable prototype package includes those PNGs. Outer backgrounds use true transparency, not a checkerboard.
