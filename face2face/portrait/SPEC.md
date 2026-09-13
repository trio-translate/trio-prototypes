# Design contract: face-to-face portrait

## Agreed requirements

### Screen and orientation

The active session has two equally important reading surfaces and starts at a symmetric 50:50 split. The first participant reads the lower section normally. The other participant reads the upper section rotated exactly 180 degrees. Text and controls presented to that participant share the rotation.

A thin horizontal divider separates the sections. Dragging it up or down reallocates viewport height. **It never changes font size, weight or color.** Less space means fewer visible log lines, not smaller text. The green upper background and blue lower background differ subtly; they do not imply that one participant owns the app or has more authority.

### Typography — applies to every current mockup

All displayed text has the same size, regular weight and color. Prototype tokens are 22 CSS pixels, weight 400, color `#edf3f5`, line-height 1.5. These tokens also cover controls and temporary recording feedback. The numerical size is a prototype choice; the uniformity and absence of automatic fitting are requirements.

There is no large “current sentence,” small “previous sentence,” bold translation, faded history or differently colored draft. The earlier “only unsettled text is grey” experiment was superseded by the later equal-size/weight/color instruction. There is no trailing cursor or blinking insertion bar.

Platform accessibility text preferences must not be disabled in the real app. A deliberate user/system text-size change should apply consistently to both sections. Moving the divider must never trigger such a change. Preserve legible text and scrollability at large accessibility sizes rather than shrinking content to fit.

### The conversation log

Each section is an independently scrolling, chronological, appending log in that participant's selected language. Older entries remain available as the session grows. The newest material appears at the reading-direction end: near the lower physical edge for the lower participant and the upper physical edge for the rotated participant once scrolling is needed.

Transcription and translation appear progressively. Interim revisions update the same utterance in place; they are not appended as duplicate completed sentences. Once settled, an utterance is retained as history and subsequent utterances append after it. The prototype demonstrates progressive words and the draft-to-settled model; it does not implement real recognition or translation revision semantics.

Scrolling one side does not scroll the other. New text follows live only when that participant is already following the end. Scrolling back suspends follow on that side, not on the other. Resizing preserves each side's reading position or live-follow state. Returning to the end restores follow. The prototype additionally exposes “Jump to live” in the tapped panel while reading history, not as a permanent screen control.

“Infinite” describes the user-visible log, not permission to grow RAM indefinitely. Production needs a persistent transcript model and a virtualized/windowed renderer. Loading older entries must not discard data or change the reader's anchor. The prototype deliberately keeps its demo entries in the DOM and in memory; it does not claim production-scale persistence.

### Before versus during a session

Languages are selected before starting. During the live session there are no visible language names, language selectors, persistent record buttons, “Hold to record” hints, giant waveforms, or permanent navigation controls. The content uses the available reading surfaces.

Language names and interaction instructions may appear on setup, outside the running session. The sample language choices in the prototype are presentation fixtures and do not redefine Trio's engine capabilities or cloud/offline policy.

### Tap, hold, scroll and resize

A short tap anywhere in a participant's reading surface opens a temporary panel oriented for that participant. The panel provides a clear way to return to the conversation and a clear way to **stop the session and go back** to setup. Stopping and navigation are one unambiguous action in this prototype; it must not leave capture running behind the setup screen.

Holding anywhere on one's own surface enters manual recording for that side. Release finishes recording and returns to the ambient session. No dedicated visible recording button is required. Recording feedback exists only during the hold. Cancelled gestures, pointer cancellation, application focus loss and interruptions must not leave recording stuck on or submit an unintended utterance.

Gesture arbitration is mandatory: vertical scrolling must not open the panel; divider dragging must not start recording; releasing a completed long press must not be interpreted as a tap; content auto-scrolling must not masquerade as finger movement. A second touch must not silently switch recording ownership.

## Prototype choices, not yet product mandates

The current demo uses a 450 ms hold threshold, a 10 CSS-pixel movement tolerance, a 44-pixel invisible divider hit target, and a divider range of 25–75%. The thin visible line is not its entire hit target. These values prevent accidental collapse and make testing deterministic; physical-device testing should determine the final values.

The divider can be moved with arrow keys, adjusted more quickly with Shift, sent to its limits with Home/End, and reset to the center with Enter or a double-click. Each log exposes keyboard session controls and Space-to-hold recording. Native dialog focus handling supplies modal keyboard behavior. These are accessibility affordances, not extra always-visible controls.

## State and navigation map

| State | Entry | Valid exits |
| --- | --- | --- |
| Setup | Initial load or explicit stop | Start session |
| Live | Start succeeds, or manual hold ends | Open controls, record, scroll or resize |
| Reading history | Scroll away from the end on one side | Scroll to end, or tap → Jump to live; Stop remains reachable |
| Controls open | Short tap / accessible action | Continue / dismiss; Jump to live when applicable; Stop and go back |
| Manual recording | Hold on a participant's surface | Release to finish; interruption/cancel to discard |
| Stopped | Stop and go back | Setup is shown; a fresh start is possible |

Every state must have a reachable exit. A screenshot that omits navigation is not permission to strand the user. Missing exits must be challenged during review with concrete acceptable resolutions and acceptance evidence.

## Acceptance and production completion

The included Chromium harness checks uniform typography; rotation; backgrounds; streaming; lack of cursors; independent scrolling and live follow; resize without scaling or history loss; tap panels; oriented upper controls; hold/release; interrupted holds; keyboard divider boundaries; and stop-to-setup.

Before shipping, additionally verify on physical target iPhones: touch scrolling in the rotated view, small-screen and safe-area layouts, large accessibility text, VoiceOver and Switch Control, interrupted and multi-touch gestures, all menu exits, app backgrounding, and sessions long enough to require history virtualization. Connect the app's existing global session and per-utterance states rather than introduce a parallel speech engine. Validate draft revision/finalization, cancellation, teardown and restart against real recognition, translation and playback. Prove that an EN ↔ PT-BR pair can start once, put the phone down, speak naturally and understand each other without repeated handling.

No production changes or physical-device results are implied by this prototype package.
