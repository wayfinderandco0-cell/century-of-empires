# V263 — offline, genuinely playable three-octagon exact-art candidate (2026-10-28)

**Production RED / USER NOT APPROVED / FICTIONAL GEOGRAPHY.**

This isolated candidate is **not merely the V262 art viewer**. It packages the original V249 three-octagon gameplay renderer, the unchanged V121 Matrei image and V123 road/bridge network, and the exact local V258 WEST + V260 SOUTH 1536×1024 PNGs into one offline HTML. The army can receive orders, move across the same original V123 road network, halt, and be followed with touch pan/zoom. It is an experimental playable build, not the approved game. Main, V94, user saves, sprites, and original game source files are untouched.

## Critical visual correction

Actual V249 playable mode previously painted a thick synthetic highway directly over the newly baked photographic dirt cartway. V263 **suppresses that synthetic overpaint only for imported WEST/SOUTH artwork in the isolated candidate**. The native cartway remains visible; army routing, click targets, Matrei's original art and painted Matrei bridge approaches are unchanged. The original V123 route remains available via debug inspection. This does **not** prove physical route-to-road alignment; the real source-road drift remains a visual-review issue.

## Reproducible local build

The original PNGs are **not hosted in GitHub**. The builder checks exact SHA256 hashes and dimensions and refuses substituted images. It also inlines the V249 dependencies, the original Matrei V121 HTML, and the rejected V224 fallback manifest (used only behind the imported original art), so no network is needed. A genuine SHA256 JavaScript fallback supports offline file contexts without WebCrypto; it does not bypass hash validation.

WEST SHA256: 36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7

SOUTH SHA256: d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb

V123 Git blob: 09f04b4062e24fbacbb645307462cdddce2b2aa3

Run:

    python scripts/v263_offline_exact_art_playable.py --root . --west /private/west-v258-lossless.png --south /private/south-v260-single-pass-UNAPPROVED.png --out /private/V263_UNAPPROVED_Offline_Playable.html

The generated offline HTML is approximately 11.5 MB. The exact user-facing candidate and its screenshots are attached in the originating ChatGPT run, **not published to GitHub Pages**.

## Verified actual-image local browser testing

- Used the real V253 GitHub Actions repository source/screenshot artifact, including V249 renderer, V121 Matrei and original V123 network.
- Built the 11.5 MB HTML from the **exact** V258 WEST and V260 SOUTH PNGs; SHA256 and 1536×1024 dimensions verified.
- Tested the **actual self-contained game** in real Chromium mobile emulation, 390×844 portrait and 844×390 landscape, DPR2, touch enabled. Both original images imported, all three centers rendered, no page errors, connectedRoute=true, actual orderTo('south') succeeded, army progressed on the unchanged V123 graph (max numeric graph deviation ~8.65e-14). Screenshots were opened and inspected, including the real baked SOUTH cartway after removing synthetic road overpaint.
- Local browser navigation was blocked, so the exact HTML was loaded with page.set_content. Offline SHA256 fallback performed the actual hash checks. **This is not native iPhone Safari.**
- Local WebKit executable is absent; **no exact-art WebKit claim**. CI tests four configurations with clearly labeled **synthetic** placeholder images, not the original art. CI screenshots are not visual acceptance evidence.
- Strict V203 0.70/0.70 thresholds were not demonstrated for V263. Previous SOUTH landscape was below threshold. Independent V209 geographic tiepoints, authentic 1780 road evidence, WEST bridge banks, Matrei seams and human user acceptance remain unverified.

## Next

Obtain and inspect exact V263 WebKit portrait/landscape screenshots and run strict V203 on the exact art; compare army trajectory to visible physical ruts (not only to graph mathematics); verify bridge banks and Matrei tile edges using independent geography or explicitly retain fictional study status. Do not merge or promote this branch until the user approves the actual art and gameplay integration.
