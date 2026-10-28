# V266 — Matrei native-photo edge reveal (2026-10-28)

**Isolated experimental playable artifact. PRODUCTION RED; NOT user-approved.**

## Actual image improvement

V265's Matrei source was excessively faded into procedural green terrain. V266 reveals more of the **already-existing protected V121 source photograph** by changing the Matrei alpha feather 280→145 and scenic focus .59→.33. Original V121, WEST and SOUTH image bytes are unchanged. No tree copying, mirrored terrain, synthetic roads, route moves or historical claims. The gold frame remains masked. The original source is fictional artwork, not historical topography.

Rebuild locally using the exact V265 offline HTML SHA256 1d267eb96ba5b1e60f3dcb0b83fa898afc41c580d3c141fcf18f8ecdcf9dfe9a:

    python scripts/v266_native_matrei_edge_reveal.py V265_UNAPPROVED_Offline_Playable.html V266_UNAPPROVED_Offline_Playable.html

No source imagery is committed to GitHub. The fail-closed builder only changes two alpha expressions and the UNAPPROVED title, and rejects an unexpected V265 HTML, missing production guard or V264 mirrored seam.

## Actual-art Chromium testing (not user approval)

In the 390×844 DPR1 Matrei screenshot, x30–360, upper transition y210–350: Gaussian fine-luma increased **17.32→24.20**, area above threshold 12 **.481→.624**; lower transition y490–660: **13.03→15.52**, area **.373→.446**. The original photographic rocks/forest remain visible farther toward the perimeter; this is not seam registration.

Strict V203 zoom-6 scores from actual Chromium screenshots (minimum 0.70 for both ratios): portrait WEST **0.7831/0.8544 PASS**, SOUTH **0.7842/0.8781 PASS**; landscape WEST **0.7492/0.8731 PASS**, SOUTH **0.7561/0.8827 PASS**. The portrait Matrei baseline itself becomes sharper, reducing WEST/SOUTH relative ratios from V265. These were checked, not assumed. No JS page errors.

## Unresolved / do not promote

Large procedural gaps and abrupt source boundaries remain. No independent V209 geographic tiepoints, 1780 road proof, verified bridge banks, nonduplicated physical landscape continuity, exact original-art WebKit, native iPhone Safari or user visual approval. CI four-browser testing uses **synthetic imagery only**. No main, sprites, saves, V94, V121/V123 road graph or original V249 renderer changes. **Three octagons unfinished; production gate deliberately RED.**
