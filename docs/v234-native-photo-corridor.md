# V234: source-native full-scene corridor experiment (PRODUCTION RED)

October 27, 2026. Isolated branch `terrain-v234-native-photo-corridor-search-20261027`, based on V233. Main V192, V94 saves/campaign, Matrei art, V121/V123 roads and bridge, army sprites, and mechanics are unchanged.

## Why this approach is different

V230/V231 painted a photo-derived road-ground strip onto unrelated scenery. V232 proved the unmodified sources contained trees and cliffs under the road. V233 tried to deform entire images to bring clear ground beneath the original route; both images required destructive displacement and were rejected.

V234 instead searches **every native 1536x1024 crop at 48px intervals** within two separately licensed, high-resolution Austrian photographs. For each crop it measures the **original untouched photograph pixels** directly under the exact V123 cartway, including a 25px-wide shoulder and the longest continuously obstructed segment. It ranks entire scenes without painting, terrain warping, upsampling, repeating pixels, changing the road, or inserting a fake bridge. Full-resolution original pixels are used for the final strict V232 ground check.

The sources remain Stijn te Strake's *Forested mountain valley (Unsplash)* (4288x2848) and Volker Schnäbele's *Turquoise mountain lake (Unsplash)* (6000x4000), both CC0 1.0, from Wikimedia Commons. Original SHA1 values are inherited and verified from V231; downloaded SHA256, authors, license, original dimensions, and source pages are recorded in the generated manifest. The sources are **NOT Matrei**, **NOT 1780 cartway evidence**, and **NOT geographically registered to V123**. No natural V209 tiepoints have been verified.

## Art gates

A crop may be emitted as an **unapproved ground preflight candidate** only when original-pixel V232 necessary clearance passes (open roadbed area and open route samples >= 0.72, longest blocked run <=70px). A passing numerical mask is **not** sufficient to prove real cartway geometry, bridge banks, scene realism, Matrei visual coherence, historical period correctness, or human approval. Every source/game registration and production approval flag stays FALSE.

GitHub Actions runs positive/negative synthetic tests, downloads the pinned original photographs, analyzes the full source area for BOTH cells, and uploads real source-pixel diagnostic JPGs and a JSON report. The last step deliberately fails production approval. If both images pass ground preflight, their unmodified native-crop WebP images are included in the artifact for further visual examination; otherwise they are rejected without pretending to be playable assets.

## Next

Inspect actual V234 CI review images and numeric report. If either source remains unsuitable, do **not** iterate on the same photo with cosmetic patches. Seek two genuinely compatible high-resolution landscape compositions, or explicitly document that historical geographic registration is blocked and proceed only with a clearly labeled fictional, isolated art alternative. A viable pair must then be integrated in a playable isolated branch, subjected to four iPhone Chromium/WebKit configurations, unchanged V203 0.70/0.70 thresholds, human screenshot inspection and user visual approval. No production merge until every gate is satisfied.
