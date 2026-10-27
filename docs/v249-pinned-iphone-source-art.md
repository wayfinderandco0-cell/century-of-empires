# V249 — SHA-pinned two-cell iPhone source review (ART RED)

**Purpose:** V248 required manually selecting WEST and SOUTH files on each iPhone. V249 adds an isolated URL-shareable, *exact-byte* pair review, allowing a newly created or properly licensed **1536×1024** artwork pair to be inspected in the actual three-cell game without changing code or using iOS file pickers. This is an artwork iteration tool, not finished art.

## Usage and source integrity

Open `v249-pinned-source-art-review.html` served over HTTPS with four URL parameters:
`westSrc`, `southSrc`, `westSha256`, `southSha256`. URLs may be same-origin or HTTPS `upload.wikimedia.org`; SHA-256 hashes are mandatory, lowercase hex, exact downloaded bytes. Sources must be PNG/JPEG/WebP, at most 20 MiB each, exactly 1536×1024. No resampling, canvas painting or route geometry adjustments occur in the loader. Missing URL/hash, bad digest, inaccessible/CORS-blocked host, wrong MIME/dimensions, or partial pair rejects the **entire pair**. This does not assert the source is historically authentic or licensed; source rights must be verified separately. URLs should not contain private tokens.

On successful loading the page **automatically enters V248 raw-source inspection mode**: synthetic cartway ink is hidden on WEST/SOUTH, red dashed immutable V123 centerline remains visible, and army orders are blocked. Exiting inspection restores exact original movement. Matrei, army sprites, V94 campaign/saves, core mechanics, V121/V123 topology and production remain untouched. All approval flags remain false. A link is not a verified historical source or a production build.

## Test and next step

Run `node scripts/test_v249_pinned_source_art_review.js` and `python scripts/qa_v249_pinned_source_art_review.py` in the checked-out branch after installing Playwright browsers. QA uses **previously rejected V224 SUHEJLO CC BY 4.0** WEST/SOUTH image fixtures, tests Chromium/WebKit at 390×844 and 844×390, captures actual source-pixel screenshots, checks original route after leaving review and rejects a mismatched SOUTH SHA atomically. The fixture pair is not roaded, source-registered, 1780-authentic or user-approved. V203 thresholds remain strict, and production intentionally RED.

**Unresolved art blocker:** No physically plausible, independently traced, period-safe high-resolution WEST/SOUTH pair with matching V123 cartways, valid bridge banks and natural geographic tiepoints. Do not promote a transport test or an AI-rendered dashboard as actual game art. Next substantive work is acquiring/authoring and inspecting a distinct pair that truly matches the immutable roads, not further painting procedural stripes.
