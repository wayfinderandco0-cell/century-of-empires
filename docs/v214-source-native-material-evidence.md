# V214 — original photographic material bank; NOT playable geographic terrain

Date: 2026-10-26. New isolated branch `terrain-v214-source-native-material-bank-20261026` from V213. Read issue #9 through V213, verified V213 CI 40315416021 (original route/bridge/camera and modern-source mobile capture green; strict V203 photographic game-art gate RED 4/4), inspected the real V213 WebKit portrait three-cell screenshot contact and the original V205/V207 modern source contacts. No production, main, V94 campaigns/saves, V121 original Matrei photo or V123 roads/army graph touched.

## Engineering change

The current V205 forest reference is approximately 3.578 km from the independently documented modern Matrei anchor. Its native 512×512 panels do not register to V123's 1536×1024 octagons. They may be used as *photographic material research*, never pasted into the game as if they describe the same place.

- `scripts/v214_source_native_material_bank.py` uses only original native 256px JPEG tiles, independently verified and assembled by V204/V205. It checks V206's pinned source SHA and V207's conservative modern-feature masks. It selects **one 128×128 unresized, unaltered RGB crop per modern source panel**, requiring a 12px fully retained buffer. A luminance gradient ranks the eligible crops but **is not a visual-quality pass**, nor a claim that all modern features were detected.
- The first real CI artifact exposed a **visible '2023' imprint inside the highest-ranked WEST crop** even though the old V207 mask had considered that region retained. The actual native source contact was opened and inspected. V214 now adds an explicit reviewed west-source quarantine rectangle x=340–413, y=26–91, with a regression check at (370,60); this is not an assertion that every modern artifact is excluded. The material samples must be regenerated and re-inspected after this fix.\n- It exports three original-pixel PNG candidates, exact native pixel rectangles, modern EPSG:3857 footprints, hashes, a contact sheet, license attribution and immutable NOT APPROVED metadata. No invented tree, inpainting, sharpening, texture noise, historical reconstruction, map warp, or unverified traversability.
- `scripts/test_v214_source_native_material_bank.py` rejects masked regions, malformed masks, synthetic source substitutions, altered source pixels, changed contact evidence and false approval metadata.
- `.github/workflows/qa-v214-native-material-bank.yml` runs inherited V204–V209 and V213 geographic invariants, the new native source QA, the unchanged original four-browser route/bridge/army/camera checks and **unchanged strict V203 photographic-art test**. The art test must remain RED while West/South are still synthetic.

## What this does NOT solve

The candidate crops are small modern **material samples**, not high-resolution final octagon paintings and not period-safe geography. Even a perfectly passing material audit cannot establish forest extent in 1780, source-to-game landmarks, bridge-bank geometry, natural cell seams, West/South road destinations, all four V100 zoom tiers, or user physical-iPhone approval.

Real V209 independently reviewed source/game tiepoints remain **empty** and registration is BLOCKED. Do not insert the crops into playable terrain until source alignment and semantic placement can be defended. Original Matrei photo and road/army controls remain immutable.

`sourceRegisteredToV123=false; historicalRoadsVerified=false; bridgeBanksVerified=false; gameArtApproved=false; physicalIPhoneApproved=false; productionApproved=false`.

CI results must be checked on the branch after the workflow runs; this document does not preclaim success.
