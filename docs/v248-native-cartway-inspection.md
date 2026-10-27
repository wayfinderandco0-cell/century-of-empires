# V248 — Native-cartway pixels versus synthetic route ink (UNAPPROVED)

**Problem actually addressed:** V242 made imported original images visible above the
rejected V236 fallback, but then V194's opaque 22px synthetic cartway was drawn
over every WEST/SOUTH source. It hid the physical road pixels an artist needs to
inspect, allowing the painted route to look aligned when the source itself has no
road or a displaced road. This is an isolated *rendering/inspection* correction,
not a new terrain source or a production art approval.

## Isolated playable-preview behavior

`v248-native-cartway-inspection.html` preserves the V242 gameplay preview and
all unchanged V121/V123/V94 graph, sprite, Matrei, save and movement code.

- Default **playable route mode** keeps the original V194 cartway ink on exact
  V123 geometry and allows existing army commands.
- After **both** native 1536x1024 WEST and SOUTH images are imported locally,
  **Inspect native cartways (no gameplay)** hides synthetic road ink ONLY on
  imported WEST/SOUTH cells. A thin dashed red V123 centerline shows the
  immutable path, exposing any mismatch between real image pixels and gameplay.
- While native inspection is active, army movement is paused without changing
  route progress, road taps and new army orders are refused. Exiting resumes
  the original playable route mode; no source pixels or original game files
  are modified. Matrei's original art and bridge-exit strokes stay unchanged.
- A missing image fails closed. No import, screenshot, red line, V203 score or
  visual inspection can set an approval flag to true.

## Evidence and limitations

Run `node scripts/test_v248_native_cartway_review.js` and
`python scripts/qa_v248_native_cartway_review.py` after installing free
Playwright browsers. The browser QA imports **REJECTED** V224 CC BY 4.0
SUHEJLO fixtures solely to verify actual pixels in four Chromium/WebKit
portrait/landscape configurations; captures both painted and native modes,
checks Matrei pixel parity and original V123 army routing after exit.

**This does not supply new landscape artwork.** The original SOUTH and WEST
source suitability, natural V209 tiepoints, historic 1780 cartways, bank/bridge
alignment, strict V203 human realism and physical iPhone/user approval remain
unverified or rejected. No source pixels are promoted. Production stays RED.

**Next substantive step:** replace rejected sources with distinct,
license-attributed, photo-grade WEST/SOUTH landscapes whose native cartways
are independently traced and physically plausible at the immutable V123
positions; inspect raw pixels with this preview, then run V240/V246 source
registration and four-browser V203 visual tests. Never alter the V121/V123
graph to make an image fit.
