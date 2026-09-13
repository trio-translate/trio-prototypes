# Conversation record and corrections

Source: the face-to-face portrait design conversation supplied with this task, 13 September 2026. This is a focused record of that conversation, not a duplicate global Trio product specification.

| Order | Direction from the user | Result / why the correction matters |
| --- | --- | --- |
| 1 | Symmetric portrait screen; first participant below, second above rotated 180°; a thin divider; streaming transcription and text. | The content must be readable from opposite ends of one phone. Early landscape/tablet renderings did not satisfy the requested portrait composition. |
| 2 | Drag the divider to distribute the screen between the languages. | Reallocate viewport height, not participant identity or language. Symmetry is the initial state, not a permanently locked split. |
| 3 | Select languages before the session; omit names after starting to maximize useful space. | Remove language labels/selectors from the live surfaces. Showing them again in later generated images was a regression. |
| 4 | Tap anywhere for a panel to stop and go back, instead of displaying many controls. | Keep live reading uncluttered but never trap the user. The prototype offers Continue and Stop and go back. The older ambiguous “Go back” label is not the final interaction contract. |
| 5 | Hold on one's own side to record; clickable prototypes are needed. | The whole surface is the gesture target. Permanent circular buttons and “Hold to record” labels in earlier images misrepresented the request. |
| 6 | “Text does not change size. Rather, it's an infinite scrolling appending log.” | Resize the viewport and preserve history. Do not enlarge the current sentence, shrink older entries, replace the whole screen or append every partial hypothesis as a separate entry. |
| 7 | Make only the most recent unsettled sentence grey. | This was an intermediate experiment. Older settled entries were not supposed to fade. Several generated pictures also incorrectly reordered or split sentences. |
| 8 | Remove both recording buttons; give all text equal size, weight and color; remove the cursor. | This supersedes the grey-draft experiment. Current images and the prototype use one text style for all conversation entries, including active partial text. |
| 9 | Subtly distinguish the sections with green/blue backgrounds. | Preserve the minimal uniform-text layout; change only the section backgrounds. The subsequent generated image brought back controls, cursors and mixed typography and is not canonical. |
| 10 | Remove selected areas. | The exact image-editor selection masks are not available as separate inputs. Do not invent their boundaries. The explicit requirements already establish that the permanent recording controls and cursors are absent. |
| 11 | “All text must be the same size. In all images. Regenerate.” | Apply one typography token across every current image and state, not merely within one screenshot. New vector mockups and PNG exports are generated deterministically instead of relying on a generative model to preserve text geometry. |
| 12 | Put this work in `flyrev/trio-prototypes`, at `face2face/portrait/`. | Package the design contract, executable interaction prototype, current separate mockups, tests and provenance in that location. This is not a request to change the production app. |

## Precedence

The latest explicit requirements in `SPEC.md` win over any contradicting mockup. Earlier images are historical evidence of exploration, not implementation guidance. Do not infer speaker alternation, speaker identity, speech-engine behavior, microphone permission handling or production readiness from scripted sample text.

## Status of the source images

The original source files are collected in the complete downloadable archive. `archive/manifest.json` records their identities, deduplicated filenames and SHA-256 hashes. The canonical repository mockups are the newly generated SVGs; they do not depend on old image-generator output or externally hosted images.
