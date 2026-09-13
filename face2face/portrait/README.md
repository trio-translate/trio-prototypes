# Face-to-face portrait: two persistent reading cards

A clickable, dependency-free prototype for the simplified **in-session** face-to-face portrait experience. The **cards** variant explores removing the visible dividing line. The **divider** variant retains the earlier layout for comparison. These are alternatives in one implementation, not two diverging copies of the interaction logic.

## Open

Open `index.html` in a browser. Select the two languages and the layout before starting the demo. No build, account, API key, microphone permission or network service is required. This is an **interaction simulation**, not a translator or audio recorder.

A static file server also works:

```sh
python3 -m http.server 8000 --directory face2face/portrait
```

Then open `http://localhost:8000`. Query parameters support direct comparison:

| URL suffix | State |
| --- | --- |
| `?demo=1` | Cards with automatically appended sample speech |
| `?layout=divider&demo=1` | Same behavior with the original line/handle |
| `?preview=live` | Cards, frozen sample log, 50/50 allocation |
| `?preview=resized` | Cards, 67/33 allocation, identical typography |
| `?preview=controls` | Lower participant's controls |
| `?preview=top-controls` | Upper participant's rotated/localized controls |
| `?preview=recording` | Transient recording-demo feedback |

“Frozen” previews pause scripted conversation playback; gestures remain interactive. A preview's recording state can be cancelled with Escape. The ordinary demo starts at the pre-session setup, not at a bypassed language picker.

## Current visual contract

- Exactly **two permanent cards**, one per language. Not one chat bubble/card per sentence.
- Upper reader rotated 180 degrees; lower reader upright. Initial space allocation is equal.
- Subtly different dark green and dark blue backgrounds, a narrow 12 px gap, no visible dividing line or permanent drag handle in the cards variant.
- One typography token: **22 CSS px, weight 400, color `#f0f4f5`**. It applies to both logs, pending text, settled text, controls, setup and transient recording feedback. Resizing changes the viewport, **never** the text size. No fit-to-box or transform-based scaling.
- No live language-name labels, recording buttons, waveform decoration, cursor, or per-sentence typographic hierarchy.
- Every generated state uses the same rendering source and type token. Separate images, not grids. PNG screenshots have true alpha outside the rounded device, not a checkerboard.

The later uniform-size/weight/color request supersedes the earlier exploration where unsettled text was grey. The discarded images that reintroduced buttons, cursors or mixed text sizes are not implementation references.

## Append-only meaning

The **completed conversation** is append-only for the current session. Each log is independently scrollable and retains earlier paragraphs. The reader's viewport stays fixed; the page does not grow and text is not shrunk to fit.

A streaming utterance has a stable ID and **one pending paragraph**. Its partial text can be revised in place until settled. Appending every recognizer partial would instead create duplicate sentences. Settlement does not create a second paragraph. Completed paragraphs are not restyled or rewritten by subsequent utterances. Pending and settled paragraphs look identical in this variant.

Both language views refer to the same ordered utterance IDs. Reversing the upper view changes reading orientation, not chronology. There is no assumed speaker identity or required alternation in the UI model.

Automatic following is per card: when a reader is at the latest text, new text remains visible. After a reader scrolls back, additions do not pull that reader away from history. The other card can continue following. “Jump to latest” appears in the tapped card's controls only when needed. The control-free resting state stays uncluttered.

## Interaction and navigation

| Gesture/state | Result |
| --- | --- |
| Drag the narrow gap | Change allocation, clamped to 20–80%; no text resizing |
| Swipe a card | Scroll that language's history independently |
| Short tap on a card | Open controls oriented and localized for that participant |
| Hold still on a card for 450 ms | Simulate manual recording on that side; suspend ambient sample playback |
| Release after holding | Append one simulated manual utterance; do not also open controls |
| Move more than 9 px before the hold triggers | Scroll, not record or open controls |
| Cancel, lose the pointer, hide the page or press Escape | Cancel held recording without committing a manual utterance |
| Stop session | Stop playback and return to setup; previous log remains reviewable |
| Go back / Voltar in the controls | Dismiss controls and return to the log; does not stop the session |
| Read previous log | Open the stopped log; tap for “Back to setup” to exit |
| Equal space | Restore 50/50 without needing a precise drag |
| Start another demo | Begin a new session log after selecting languages/layout |

The 12 px visible gap has a **44 px transparent hit region** for dragging. A keyboard focus outline is transient; it is not a permanent dividing line. The gap is focusable and exposes a separator value: Arrow Up/Down adjusts space, Home/End selects the clamp endpoints. Card Enter opens controls; holding Space simulates recording; End jumps to the latest text. Modal focus is trapped and returns to its originating reader.

The two cards supply a visible boundary, but **resizing still has a logical boundary**. Removing its drawn line should not remove allocation behavior. Instructions live before the session, with “Equal space” available in the transient panel. Discoverability of the draggable gap remains a real-phone design question, not a proven usability result.

## Why these corrections were needed

1. Persistent reading cards make a drawn separator redundant while preserving independent scrolling surfaces.
2. Earlier image generations repeatedly changed text size, color and weight, or brought removed controls back. A single executable source plus computed-style tests prevents those contradictions.
3. Rendering each partial as another sentence would contradict an append-only conversation log by duplicating recognizer hypotheses. The pending paragraph keeps a stable ID.
4. Auto-follow must not make reading history impossible. Each reader has its own follow state.
5. Tap, long press, scrolling and allocation drag compete for the same screen. Movement thresholds, pointer cancellation and separate gap handling prevent one gesture from accidentally triggering another.
6. Controls must be readable from the side that opened them, and every state needs an exit. Rotation/localization, focus restoration, stop/review/setup navigation are included.

## Verification

Install the browser-test dependency and run the checks:

```sh
python3 -m pip install playwright
python3 -m playwright install chromium
python3 face2face/portrait/tests/test_portrait.py
python3 face2face/portrait/tests/render_mockups.py
```

An installed `chromium` executable is detected automatically; `CHROMIUM_EXECUTABLE` can override its path. Runtime `index.html` has **no dependency** on Playwright or Python.

The checks cover uniform typography across languages, sizes and layouts; absent resting controls/line; orientation; revision IDs; retained history; independent follow; mouse and emulated native touch scrolling; hold cancellation; dragging; keyboard equivalents; modal focus; and complete setup/live/stopped/review navigation. `tests/verification.txt` records the local run. Screenshots are produced from the actual HTML, rather than generative interpretations of it.

## Boundaries and completion

This completes a **browser interaction prototype**, not a production implementation. Sample speech, translations and recording are simulated. No audio is captured; no data is uploaded; the session log exists only in page memory and is not saved across reloads. The demo does not prune old entries, but it is not a production virtualized or durable unlimited log. The append test helper caps a single bulk test call at 5,000 items, not the session length.

Before adopting this in Trio: compare both layouts on an actual iPhone with two people; test whether each person discovers scrolling/resizing and can tap/hold without accidental actions; test VoiceOver and large user-selected text with real iOS gesture behavior; then bind the selected layout to Trio's real utterance/revision/session pipeline, add long-session retention/virtualization, and rerun navigation and interruption tests on device. Browser automation is evidence for the prototype, not a substitute for those device checks.

This exploration does not replace Trio's product specification or promote the cards variant to a final product decision without evaluation.
