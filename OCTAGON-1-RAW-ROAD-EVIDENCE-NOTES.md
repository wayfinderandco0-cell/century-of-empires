# Octagon 1 raw-source road QA checkpoint — 2026-10-22

Branch: octagon-1-hour8-raw-road-evidence-20261022
Code commit: 97a5b4527110a9f1914cfa3fd8ac80d7c3b31269
CI: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/39814631290

Added an independent sampler for the original 1100x842 JPEG, measuring candidate east-bank and south-branch route center pixels against perpendicular offsets every approximately 16 pixels. Produces CSV, JSON, and a contact sheet of unpainted source-image crops. Synthetic tests exercise pixel contrast, arc sampling and bounds. Results are review diagnostics only: no image color pattern proves a road.

Outstanding: road paint remains unverified; old embedded labels, far-bank continuation, source terrain crossings and adjacent octagon remain unresolved. Do not certify movement, deep zoom or conquest from these samples. Next inspect actual JPEG evidence, then author terrain and road together and test in Chromium and WebKit.

Attempt to post progress to issue #9 was rejected by GitHub connector safety checks. Main, V94 atlas, game mechanics and saves remain unchanged.
