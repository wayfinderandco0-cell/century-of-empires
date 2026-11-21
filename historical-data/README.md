# Local historical world atlas source

The file `world_1783_simplified.geojson` is a modified, reduced-resolution copy of the historical boundary dataset:
- Source: https://github.com/aourednik/historical-basemaps
- Original file: `geojson/world_1783.geojson`
- Original project credit: A. Ourednik et al., *historical-basemaps*
- Source license: GPL-3.0 (see the source repository's LICENSE)
- Modifications made 2026-11-17: Retained NAME and SUBJECTO properties only; simplified rings by 0.01 geographic degrees with Douglas-Peucker; coordinates rounded to four decimals; all 641 historical features retained.

**Important limitations:** The boundaries are an approximate 1783 reconstruction, not a verified 1780 military map. The local copy supports an in-game *reference atlas* of the world and a stable offline European background, not 641 or 1,100 new playable provinces, accurate period cartways, historical cadastral borders, or implemented non-European warfare. The original game's province IDs, army movement, economy, and saves are unchanged.

Do not relabel this data as a finished 1780–1880 global campaign.