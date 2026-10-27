# V247 — endpoint-continuation retouch feasibility (REJECTED)

**Do not import or promote this artwork.** This branch contains a tested, isolated image-processing experiment only. The V123 road/bridge graph, Matrei, original army sprites, V94 campaign, saves, and production files remain unchanged.

## Why this was attempted

Actual V244 WEST source artwork has a 275px road continuation beyond the V123 west survey endpoint (275,550). The separate fictional SOUTH source has a visible eastbound road continuing roughly 266px past its survey endpoint (1270,605). These unsupported roads cannot be declared source-proven or aligned merely because the middle of the track looks photorealistic.

The V247 script accepts a SHA256-pinned *original fictional image* and a separately manually traced **entire visible road**, including unsupported portions. It alters only the manually identified unsupported road region, preserving source pixels along the playable portion. It produces a mask, image and endpoint diagnostic. It explicitly rejects pretending the retouched pixels are original photography or verified 1780 roads.

## Actual local high-resolution trials and visual rejection

Both images were 1536×1024 original fictional AI-generated art studies, **not verified Austrian geographic sources or licensed photography**. Original SHA256 WEST: `1b0a21aa77f0aac3476093b9a0805dd227211d19246d6e27d3b4652ae362012f`; SOUTH: `3f2be77f71c05923b10bea8e8dd9c5f9ea7de51aa55842cedc2d6872b4ebceb2`.

Local script output: WEST 9,838 edited-mask pixels on an earlier narrow-mask trial; SOUTH 9,568 edited-mask pixels on an earlier narrow-mask trial. **Zero pixels changed outside the mask**. Later wider masks removed more of the visible road but produced still worse artificial blurred and cloned terrain. The SOUTH right-side river/grass bank was visibly smeared, and the WEST left-end meadow had a conspicuous patched section. **Both visually REJECTED.** These local images are not in the GitHub branch because they are rejected artwork; CI only generates clearly labeled synthetic diagnostic pixels.

Six synthetic unit tests and Python compilation passed locally. These verify code behavior, not artistic quality. GitHub Actions repeats the synthetic checks and intentionally fails the final production gate. No four-browser gameplay pass, V203 art pass, real bridge-bank verification, historical route registration, or user acceptance.

## Decision / next useful work

**Stop endpoint inpainting and photo-strip repairs.** A source image with a naturally terminating playable road (or a manually authored original complete landscape with a genuinely physical track matching the immutable coordinates) is required. Source provenance, natural geographic tiepoints, historical-road evidence and bridge banks remain independent blockers. If using fictional art, clearly label it as fictional and do not claim historic source verification. No additional automatic artwork promotion from this study.

**Warning:** Generated images resembling QA dashboards or claiming CI PASS are not evidence of actual browser execution. Only GitHub Actions results and actual captured screenshots count.
