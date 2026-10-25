# V173 — residual contemporary roofs in geographic SOURCE L (2026-10-24)

**Scope:** A conservative correction to the V169 modern-feature exclusion study, NOT a historical road reconstruction or three playable GAME octagons. No changes to main, the V121 Matrei painting, the V123 road graph, game saves, or published previews.

## Actual image evidence
Opened the original [V169 real-source CI artifact 12577237697](https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/40138360256/artifacts/12577237697), including the full 1536×1024 source reference and muted study. Reviewed native-pixel coordinate-grid crops for West, Center and South. The image contains original geographically continuous photographic woodland/meadow, but also **visible contemporary roofs** not fully excluded. The retained pixels are *modern* geography, not evidence of a historical settlement or route.

- Center upper meadow, near **source pixel (1090,397)**: visible light roof/building on the field edge, outside the former developed rectangle. Added candidate exclusion **[1066,377,1138,424]**.
- West meadow, near **(268,484)**: small bright rectangular roof remained just below old exclusion **[247,438,287,474]**. Extended to **[247,438,291,496]**.
- West north, near **(407,64)**: small colored rooftop fragment remained just below old exclusion **[392,15,432,57]**. Extended to **[389,15,438,79]**.

All three regions are visually observed **exclusion candidates** from modern photography. They do not identify historical structures. Uncertain source pixels stay unknown/transparent; the code does not inpaint them or create roads, trees, buildings or bridge banks.

## Measured source-pixel impact
Using the actual original V169 artifact's alpha channel, independently applying the three conservative rectangles removes **5,881 additional opaque source pixels** without adding any: **2,625 West**, **3,256 Center**, **0 South**. Original vs revised retained counts: West **373,396 → 370,771**; Center **333,320 → 330,064**; South **268,387 → 268,387**. These are source-sector coverage figures, **not** game-art detail or historical confidence scores.

## Engineering checks
- The V169 exclusion generator is revised in-place **only on this isolated branch**, retaining original V168 18-JPEG SHA256 verification, no-copy rules, alpha-zero unknown quadrant and source provenance.
- V169 regression tests now explicitly reject residual visible roofs at the three observed source points while confirming adjacent genuine source pixels remain visible. Developed exclusion observation count changes **10 → 11**; two prior observations have bounded extensions.
- Dedicated V173 Actions workflow regenerates the real 18-tile mosaic, validates the output and publishes a review artifact; it preserves V121/V123 identity tests and the no-approval flags.

## Still RED / next
This improves the cleanliness of geographically sourced *reference materials*; it does **not** complete historical three-octagon game art. Other contemporary features may still be present; holes cannot be guessed or auto-filled. V171 strict West/South GAME-art visual parity remains **0/4**. No independently verified V121↔source landmarks, historically authenticated routes or far-bank continuation, nor physical iPhone art approval. Next: inspect the newly generated V173 image artifact, audit remaining modern features, and establish source-first terrain/landmark correspondence before creating period-interpreted GAME-frame art. Preserve all original route geometry and unchanged visual gates.

`productionApproved=false`; `v123RoadsGeoregistered=false`; `physicalIPhoneApproved=false`.
