# Century of Empires — V111 bridge junction checkpoint

2026-10-20/21. Standalone graphics-first proof, NOT production combat or saved gameplay.

## User review
V109 town art and north-to-center village marching alignments approved on physical iPhone.
V110 screenshot IMG_4845/IMG_4846 showed the army leaving the south road at the bottom, an apparent bridge dead-end, and a hard art boundary.
User confirmed intent: keep the main southbound road and give the bridge a real alternate branch with a visible far-bank trail.
Also keep four zoom levels, pinch/pan, clean labels, and future army splitting into four independent armies.

## V111 implementation
New v111-bridge-junction.html builds on V110 without changing V110/V109/V94/V100 or campaigns.
North/shared road points through [447,720] unchanged from V109.
South route last four vertices corrected toward x=366 at y=842; bridge route forks at [447,720], traverses visible bridge, continues across east bank to [855,742].
Both paths are navigable by the demo army and selectable with South road / Cross bridge.
A junction is one shared coordinate; new far-bank dirt trail rendering follows the same geometry as its passable branch.
Alternative branch can only be selected before reaching the fork; the demo does not teleport armies past a junction.
Crossing slows marching marker on the bridge. On-screen debug displays both routes and the junction.
Top location name is hidden in Town mode so the art's town label is not duplicated.
Town view camera slightly shifted to reduce empty backdrop visible in V110 screenshot; full georeferenced tile continuity still to be developed.

## Verification and limits
GitHub file readback, Javascript compilation, stubbed DOM runtime, switch-south/switch-bridge/march/halt checks passed.
Chromium/WebKit test: scripts/qa_v111_bridge.py and .github/workflows/qa-v111-bridge.yml published. Passing workflow results are NOT confirmed; physical iPhone screenshots pending.
The original map art is oblique illustration, not verified period GIS. Bridge existence and east bank continuation as actual 1780-1880 historical route are not yet proven; V111 branch is a gameplay/illustration proposal.
Far-bank road is rendered as a thin overlay on the original approved JPG; no repaint of original art.

## Important future gameplay
At every zoom: real army selection and orders; four component units -> four independent selectable armies with separate movement, morale, strength, state and orders, conservation of units, and merge mechanics; route graph controls rivers/bridges, no dead-end fake roads.

## Next
Ask user to inspect V111 in iPhone Safari. With debug ON verify southbound path and bridge trail. Select Cross bridge, March, visually confirm crossing and far bank. Inspect Town/Pass transition and bottom edge seam. Fix actual observed issues before game integration.
