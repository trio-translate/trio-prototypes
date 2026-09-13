# Two persistent reading cards — proposed portrait variant

A separate, clickable alternative to the original [portrait prototype](../README.md). The original `../index.html`, `../SPEC.md`, decisions, tests and mockups remain unchanged. The cards proposal is not a new canonical product decision.

## Try it

Open `index.html` directly in a browser. It is one self-contained file, with no build, account, API key, network service or microphone permission. Choose the languages before starting. **Speech, translation and recording are simulated.**

From the repository root, a static server also works:

```sh
python3 -m http.server 8000 --directory face2face/portrait/cards
```

Open `http://localhost:8000`. The following suffixes expose reproducible states:

| Suffix | State |
| --- | --- |
| `?demo=1` | Two cards, automatic sample conversation |
| `?layout=divider&demo=1` | Internal divider comparison with identical behavior |
| `?preview=live` | Frozen 50/50 sample; gestures still work |
| `?preview=resized` | 67/33 allocation; no text-size change |
| `?preview=controls` | Lower participant's controls |
| `?preview=top-controls` | Rotated, localized upper controls |
| `?preview=recording` | Transient recording simulation; Escape cancels |

## What the proposal changes

**Exactly two permanent cards, one per language — not a new card for each sentence.** Dark green and dark blue surfaces, rounded boundaries and a narrow gap replace the visible dividing line and resting handle. The upper reader remains rotated 180 degrees. The gap remains draggable: removing the drawn line does not remove the logical allocation boundary.

The numerical prototype choices here are a 12 px gap, 26 px card corners, 44 px transparent drag target, 20–80% allocation limits, 450 ms hold delay and 9 px movement tolerance. These are experimental values, not replacements for the original specification's prototype values. Real-device evaluation should select the final values.

The cards variant uses one typography token: **22 CSS px, weight 400, color `#f0f4f5`, line-height 1.45**. The same size, weight and color apply to every language, paragraph, control and transient recording message. Changing allocation changes visible lines, never text size. There is no cursor, faded history, special draft styling, waveform decoration, persistent recording button or live language-name label. The later uniform-text request supersedes the earlier grey-draft experiment.

## Append-only behavior

Each card owns an independent chronological, scrolling log. Settled utterances remain unchanged. New utterances append at the reader's chronological end. A streaming utterance has a stable ID and one pending paragraph that can be revised in place; each recognition partial must not become a duplicate log entry. Both language views refer to the same ordered utterance IDs, without assuming speaker alternation or identity.

Each card follows new text only while its reader is at the end. Scrolling back preserves that reader's place while the other card may continue following. A conditional “Jump to latest” action is available in the tapped panel; no extra resting button is added. Resizing preserves scroll position or live-follow state.

## Gestures and complete navigation

| Action | Result |
| --- | --- |
| Drag the gap | Reallocate viewport height without changing typography |
| Swipe a card | Scroll only that language's history |
| Tap a card | Show controls oriented and localized for that participant |
| Hold still for 450 ms | Simulate recording on that side; pause ambient sample playback |
| Release a hold | Deliver one simulated manual utterance; do not also open controls |
| Move before the hold triggers | Scroll rather than record or open controls |
| Cancel / lose pointer / lose focus / hide page / Escape | Cancel held recording without submitting a manual utterance |
| Stop session | Stop playback and return to setup; retain the previous log for review |
| Go back / Voltar | Dismiss the panel and return to the log; do not stop |
| Read previous log | Read the stopped log; its panel offers Back to setup |
| Equal space | Restore 50/50 allocation |
| Start another demo | Begin a fresh session after language/layout selection |

Keyboard equivalents: Tab to a reader and press Enter for controls, hold Space for recording, End for latest. The focused gap exposes separator values and accepts Arrow Up/Down, Home and End. Modal focus is trapped and returns to its reader. A transient keyboard focus outline is not a permanent divider.

The gap's resize discoverability is **unproven**. Instructions live before the session and the panel offers Equal space. The cards are intended to supply the visible boundary without a drawn line, not to make resizing an undocumented requirement.

## Why these corrections were needed

The persistent card boundaries make a drawn separator visually redundant. A shared executable source and computed-style checks prevent earlier image regressions that reintroduced controls, cursors or mixed typography. One pending paragraph prevents duplicate recognition hypotheses. Independent following makes historical reading possible. Pointer cancellation and movement arbitration separate tap, hold, swipe and resizing. Participant-oriented controls and explicit exits keep both readers able to leave every state.

## Verification and separate images

```sh
python3 -m pip install playwright
python3 -m playwright install chromium
python3 face2face/portrait/cards/tests/test_portrait.py
python3 face2face/portrait/cards/tests/render_mockups.py
```

An installed `chromium` is detected automatically; `CHROMIUM_EXECUTABLE` can override its path. Python and Playwright are only test/render dependencies, never runtime requirements.

The 26 browser tests cover fixed typography across languages, states, narrow screens and allocation limits; retained history; independent following; pending revision identity; native emulated touch and mouse scrolling; hold/cancel/drag arbitration; keyboard interaction; modal focus; and setup/live/stopped/review navigation. `tests/verification.txt` records the initial local run. These are prototype checks, not physical-iPhone or screen-reader results. The unchanged original prototype has its own separate harness.

Six SVG companions are included in `mockups/`. The actual HTML is the interaction/rendering source of truth; SVG font fallback can change metrics. The rendering script exports six separate browser PNGs, with true alpha outside the rounded device. Those PNGs are included in the downloadable package; this repository addition contains the SVGs and reproducible PNG renderer, not uploaded PNG binaries.

## Remaining route to product completion

This completes an interaction prototype, not production translation. No audio is captured or uploaded. The log lives only in page memory and does not persist across reloads; retained DOM entries are not a production virtualized unlimited log.

Compare this proposal against the original on physical iPhones with two people, including gap discovery, rotated scrolling, accidental tap/hold/drag, safe areas, large user-selected text, VoiceOver and every exit. Select the preferred layout and numerical thresholds. Then bind it to Trio's existing utterance/revision/session pipeline, implement durable long-session retention and virtualization, and verify real recognition/translation/playback, interruption, teardown and restart end to end. Do not introduce a parallel speech engine or substitute this exploration for Trio's shared product specification.
