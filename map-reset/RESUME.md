# Latest status — November 10, 2026

**Four-section iPhone preview now published** without merging draft PR #26 or changing the live game's homepage, mechanics, saves, or the three approved source photographs.

- Public review URL: https://wayfinderandco0-cell.github.io/century-of-empires/four-section-iphone-review.html
- Source file copied byte-for-byte from this draft branch's `map-reset/approved-four-playable-review.html` into *main* as a **separate standalone file** `four-section-iphone-review.html`. The gameplay `index.html` is unchanged.
- Publishing commit on main: `72e72b93cab9eb5d18de1cf80de065622eeeb737`.
- GitHub Pages deployment: https://github.com/wayfinderandco0-cell/century-of-empires/actions/runs/42886595996 — **completed successfully**.
- Original/extension road-graph CI passed on latest PR head `94db3f5c5f9257d5f4f950153f6f7fa2ec843ba9`.
- This confirms hosted **publication**, not real iPhone Safari usability. **NEXT: have user open live preview on iPhone, see all four artworks, drag/pinch, tap "March to eastern valley", and inspect the road seams.** Repair defects on isolated review prototype only; do not merge without explicit visual approval.
- Prior historical note below says "no hosted four-section page"; that note refers to the November 7 checkpoint and is **superseded** by this November 10 deployment. Do not restart that work.

---

# Resume the Alpine map review

Continue Century of Empires from draft PR #26 on branch `map-restart-approved-three-road-first-20261105` in `wayfinderandco0-cell/century-of-empires`. Read this file at the branch tip after any interruption. Do not start another map experiment.

## Checkpoint — November 7, 2026

The review target is Western Pass → Matrei → Southern Valley → Eastern Valley, using the original three V267/V121 source images and one adjoining eastern section. The eastern image in the saved `century-of-empires-four-section-preview(1).html` is the newer of two candidates. Its JPEG SHA-256 starts with `9dbd6414d285`. The Matrei WebP in the repository is authoritative.

The original three-section reference and road engine are under `map-reset/`. At source commit `69974221dcfd479a72029cc7f9f2a24ce255af81` the four-section manifest has a null eastern image, and there is no hosted four-section page in this branch. Check for later commits before repeating any of these steps.

1. Restore the fourth artwork and playable page on this draft branch. Trace the visible cartways, especially switchbacks and the new eastern approach. Use one road graph for touch selection, route drawing and army travel. Preserve campaign rules and original source images.
2. Run the original and four-section road tests. Verify the actual page at iPhone size, including the bridge, all three joins, pan, focal-point pinch zoom and a march to a point inside a road segment. Capture screenshots.
3. Publish only the isolated four-section review. A dedicated review Site has been registered with ID `appgprj_6aef53ae2b888191bc5dbaa90d5c29ff`. Look it up before another deploy. Record the verified playable URL and test results here.
4. Keep PR #26 draft until Stanley reviews the fourth section on his iPhone. The wider European map and campaign integration follow approval of the artwork and roads.

Restart prompt: “Resume Century of Empires from draft PR #26. Read map-reset/RESUME.md at the latest branch commit and continue from the first unfinished step.”
