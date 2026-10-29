# V267 original SOUTH source artwork — UNAPPROVED

This isolated candidate replaces the previous SOUTH terrain source with a newly generated, independent 1536×1024 fictional Alpine landscape. It is **not verified historic topography**. The artwork is committed as [south-valley-recomposed-unapproved.jpg](v267-original-source/south-valley-recomposed-unapproved.jpg), and embedded in the same existing [playable HTML](../v267-three-octagon-original-art-prototype.html) for offline-capable viewing.

Unlike the earlier terrain correction, this source keeps trees, rocks, streams and cartway pixels at native proportions. The old SOUTH road transplant was removed from the renderer. WEST art, original V121 Matrei bytes, immutable V123 road graph, V94 campaign, sprites and saves remain unchanged. The candidate is **not production approved**.

**Visual blocker:** the newly painted SOUTH cartway is closer to the V123 path near the northern entrance but still diverges toward the east; the Matrei-to-SOUTH photographic seam is also conspicuous. Do not treat pathfinding or browser success as artwork approval. Next art task is composing the road into the terrain at the exact V123 guide points without bending trees, and improving the Matrei/SOUTH seam. The central decorative diamond remains non-playable; no southwest full tile is fabricated.

**Independent local Chromium mobile run (2026-10-29):** the source-image candidate loaded the original Matrei, rendered at 390×844 CSS pixels, reported 100 V123 nodes, two exact seams, and successfully marched WEST→SOUTH over 53 route segments to world [2806,1629]. This test predates this exact integrated branch commit; GitHub Actions/browser review of the committed artifact is still required.
