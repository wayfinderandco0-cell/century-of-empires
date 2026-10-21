# V116 Hour 13 — provenance-guard checkpoint (2026-10-21)

Branch: `terrain-v116-hour13-provenance-hardening`.
Source commit: `04690fd7d22bf91d70b96e885e450a716a01a570`.
Test commit: `e088e9e98b3d1d43a6697bf3bcc887f4afafee7f`.

The candidate graph guard now pins the known V115 source Git blob and 1100x842 art dimensions, rejects incorrect source identity and falsely approved historical/playable/conquerable flags, and enforces the existing provisional bridge terminal [699,799]. It cannot authorize a continuation beyond the painted far bank.

Seven Node 22 tests passed locally (0 failed). Local Git blob hashes match the GitHub commits:
- guard: `c07aa4faa2a3b23640396d42869376e58f01f55d`
- tests: `33b5f4712cfee2e4d9d79909e117780b807116e6`

The tests use synthetic fixtures to isolate guard behavior; hosted CI and physical iPhone Safari tests have not run. GitHub issue #9 comment attempts are blocked by connector safety checks, so this branch checkpoint records the results.

The V115 road-to-art alignment and far-bank continuation are still unverified. No production road, conquest target or deep-zoom playable cell was added. Main, live game and saves remain unchanged.

Next: integrate the guard test into branch QA if allowed; collect independent painted-road and historical crossing evidence before enabling traversal.
