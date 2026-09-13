# Working in this prototype

Read `SPEC.md` and `DECISIONS.md` before modifying this directory.

- `SPEC.md` is canonical. Earlier images under `archive/` are superseded, not designs to copy.
- Keep every current mockup's text at one size, weight and color. A divider resize changes viewport height only.
- Keep `index.html` self-contained and dependency-free. Do not introduce real microphone access, credentials, telemetry or translation calls into this interaction demo.
- Preserve independent appending logs, their reading anchors, the 180-degree upper orientation, and an exit from every state.
- Arbitrate tap, hold, scroll and divider drag; interruptions must cancel recording safely.
- Regenerate separate mockups with `tools/render_mockups.py`; do not use a generative image model to redraw text.
- Run `tests/smoke.py`. Do not claim a phone, screen-reader or production-engine test that was not performed.
- Do not ship font files or fake checkerboard transparency. PNG exports need a verified alpha channel.
- Keep the binary-delivery status truthful until source PNGs have actually reached GitHub.
- Explain why a correction was necessary, not only which pixels or lines changed.
