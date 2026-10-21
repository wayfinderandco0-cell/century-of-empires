# Century of Empires — Two-piece geographically registered atlas test

This **engineering preview** demonstrates Octagon 001 and the new eastern Octagon 002 with their shared terrain, common coordinates and automatic square connector. It is *not* final polished artwork.

Open `v106-atlas-puzzle-proof.html`. By default the player sees just a continuous geographic terrain surface with mapped natural stream guides and an *illustrative* trail. Tap **Show hidden grid + dots** to reveal the two octagon boundaries, connector square, nodes and edges. The debug overlay is off during normal use and must never appear in the finished game.

### Ground rules
- Background is the **same geographically registered V102 material** for both pieces, not two arbitrarily aligned maps. The art can later be replaced piece by piece, but the coordinates and edge intersections are authoritative.
- Octagon 001 centred at (0,0)m and Octagon 002 centred at (+1000,0)m; common E/W vertical seam at x=+500m.
- Trail passes 001 southeast edge, traverses connector `BNR:S:0:-1`, and enters 002 southwest edge. This is a *candidate route based on an illustrative trail*, **not an authenticated period route**.
- In both octagons all node connections have `enabled_in_game=false`; the map demo is not troop gameplay.
- The 4 overview levels are camera tests. The V97 retained DEM and V102 raster can't create verified per-tree or per-rock close-up detail.
- Landscape and iPhone portrait QA are required; no existing saves or playable files touched.
