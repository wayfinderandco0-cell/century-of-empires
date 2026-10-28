# V254 — distinct original physical-road landscapes (isolated; ART RED)

## Why this change is substantive
V253's actual WebKit three-cell screenshot (run 40621246002, artifact
12787641727) still showed WEST/SOUTH licensed Kosovo photographs with **no
physical cartway beneath V123**. V254 uses two **different original fictional
1536×1024 landscape studies** that already contain a visible earth cartway.
It relocates existing road and adjacent ground pixels together, rather than
painting a stripe over trees. The original images were generated for this
project with OpenAI image generation, not sourced from a third-party photograph.
This attribution is not proof of historical 1780 Austrian geography.

## Exact original inputs (not checked into GitHub)
- WEST: original project image `alpine_meadow_creek_and_rocky_trail.png`;
  SHA256 `7326e88c778ed4a0018c241156e701690e95deb1feeb8fa13a298c0f0c74505e`.
  The physical cartway runs from a rock-wall termination at x~275 to the
  east border. No new bridge is painted.
- SOUTH: original project image
  `a_highly_detailed_aerial_overhead_landscape_scene.png`;
  SHA256 `034246c5d9471cd6d87673daa48fb1a014dab38d414626677f6148ce8c7d08f3`.
  The road starts at the north edge and reaches a small **scenic, non-capturable**
  shepherd's hut near the V123 endpoint, with no obvious long eastward extension.
  This is not an added conquest node.

## Actual local 1536×1024 image experiment, visually inspected
Using `scripts/v254_native_roaded_pair.py` on both exact original PNGs:
- WEST: maximum centerline relocation **149.33px** (under the existing 155px
  cap), min sampled Jacobian **0.4459**, 0 sampled folds, observed coverage
  **0.997970**, arc stretch **0.78%**.
- SOUTH: maximum relocation **57.21px** (versus V252's 33.42px but without
  V252's long unsupported continuation), min sampled Jacobian **0.8267**,
  0 sampled folds, observed coverage **0.997202**, arc stretch **~1.4%**.
- Both pass **necessary geometry** only, not physical road alignment or
  production acceptance. Full-resolution raw art, warped art and overlays
  were opened and visually inspected locally.
- Critical visual failure: SOUTH's red V123 guide still rides **above the
  visible twin-rut cartway on part of the central bend**, despite passing
  mathematical geometry tests. WEST looks closer but has not been independently
  traced or accepted. The Matrei source tile remains visually richer/different;
  the edge transitions are not yet acceptable. **Both are rejected.**
- No new-art Chromium/WebKit four-configuration run, strict V203 approval,
  verified bridge banks, independent natural geographic tiepoints or physical
  iPhone approval has occurred. The V253 CI browser screenshots are of the
  previously rejected fixtures, NOT these originals.

## How to reproduce from exact original images
```sh
python scripts/v254_native_roaded_pair.py \
  --west alpine_meadow_creek_and_rocky_trail.png \
  --south a_highly_detailed_aerial_overhead_landscape_scene.png \
  --out qa/v254-native-pair
```
The CLI rejects wrong image SHA256 and changed immutable V123 atlas. CI
tests full native-size transforms with **synthetic pixels only**, and the
production approval job intentionally remains RED. These original PNGs and
their output WebP images are currently local project artifacts, not hosted
as a publicly accessible iPhone gameplay build.

## Protected systems and next work
No changes to Matrei, V121/V123 graph, V94 campaign/saves, army sprite
options, game mechanics, or production. Next must correct SOUTH's *visible*
mid-bend road contact without inventing geographic tiepoints, independently
review both source road traces and borders, then run the **actual images**
through V253 four-browser game renderer and strict V203 before asking for
user visual approval. If this cannot be done convincingly, keep RED and
reject the candidates. **Three octagons unfinished.**
