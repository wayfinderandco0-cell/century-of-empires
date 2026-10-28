# V261 — exact V260 source-pixel four-browser + strict V203 gate (2026-10-28)

**UNAPPROVED; production gate deliberately RED.** This is a new executable QA integration, not new terrain art or a playable build. V259's actual V249 renderer saved screenshots as `-RAW-UNAPPROVED.png`; the unchanged V203 auditor expects `-close.png` for all **12** WEST/MATREI/SOUTH × Chromium/WebKit × portrait/landscape captures. V261 copies screenshot bytes unchanged and invokes the existing V203 code and thresholds (**0.70** relative fine-luma and **0.70** relative fine-area). Missing screenshots fail closed.

## Exact local source inputs

WEST V258 lossless fictional art SHA256: `36a32828a74453ac105faf8af3729c46a42acd55d12d381d8a667d7022e1e1a7`. SOUTH V260 single-pass fictional art SHA256: `d63f5f056a682f976bafff95f04b2b71e0bb4077f34f18e9a95b32cd72fb5ccb`. Both require original 1536×1024 PNGs. Wrong/missing hash aborts before browser execution. The original PNGs remain local and are NOT committed.

With both exact original PNGs available in a checkout with Playwright Chromium/WebKit installed:

```bash
python scripts/v261_exact_art_four_browser_gate.py --root . \
  --west /private/west-v258-lossless.png \
  --south /private/south-v260-single-pass-UNAPPROVED.png \
  --out /private/v261-exact-art-report
```

The runner imports both images through the existing V259 offline real V249 game renderer, checks V123 army movement, captures actual RAW/PLAYABLE screenshots, then audits all 12 RAW screenshots with **unchanged V203**. Its `--screenshots` mode only re-audits existing captures and explicitly does not claim a browser ran.

## Verified this run

Read issue #9, V260 branch and Actions 40664780491; inspected actual V259 Chromium SOUTH gameplay screenshot and V260 native road-bend comparison. Local compilation and **6/6** V261 tests passed with local V259 screenshot subset: source-hash/dimension rejection, missing-image failure, byte-identical screenshot staging, and synthetic high-detail V203 numerical pass that still cannot set production approval. The local V259 archive contains only **4/12** actual RAW screenshots (Chromium portrait all three and landscape SOUTH); V261 correctly reports 8 missing and **V203 FAIL**, not a fabricated exact V260/WebKit pass. CI runs synthetic tests only; no original PNGs hosted.

## Still blocked

The last measured exact-art V259 SOUTH landscape V203 fine-luma/area was ~**0.638/0.637** against unchanged 0.70; V260 exact-art four-browser and V203 have not been completed. Source-to-game geographic V209 tiepoints, historic 1780 road evidence, WEST bridge banks, Matrei seams, physical iPhone and user visual approval remain unverified. Existing Matrei, V94 campaign/saves, sprites, core gameplay and immutable V121/V123 road/bridge graph untouched. **Three octagons unfinished.**
