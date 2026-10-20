# V104 inspection and decision — October 20, 2026

## Result
**Do not promote V104 to main.** The source is preserved on the isolated `terrain-v104-forest-mesh` branch as an experiment.

- QA workflow `39510532975`: completed successfully for Chromium and WebKit. Both engines passed all test assertions, including no JavaScript errors, terrain geometry, controls, source isolation, forest meshes, and phone-sized screenshots.
- Review the actual visual screenshots in `terrain-v104/chromium-forest-detail.png` and `terrain-v104/webkit-forest-detail.png`. These do **not** pass artistic quality review.
- 3D canopy meshes still appear as sparse repeated dark triangular/conical marks on fairly flat terrain at the close zoom. This is not sufficiently realistic, and not a meaningful enough improvement for the historical-strategy visual target.
- QA observed approximately 9,000–9,600 tree meshes in later frames, approximately 208,000–212,000 canopy triangles, and max recorded frame times around 146–182ms in browser automation, which does not establish acceptable iPhone performance.
- Atlas/region relief and V97-derived landforms are a useful preserved foundation. Leave V103 published as the last public preview.

## Next graphics direction, V105
Stop iterating tiny tree symbols. First build *cohesive canopy coverage* baked as high-quality organic forest texture / foliage clusters from the existing geographically referenced woodland proxy. Forest mass should read as continuous at Region/Local and gradually transition to distinctly rendered canopy only when close enough. Test a zoom/camera view closer to the actual ground; avoid flat overhead triangle icons. Forest shadows, patch variation, tree heights and valley clearings must be visually convincing and deterministic. Preserve the V97 geography, real stream network guides, historical illustrative status and all earlier versions and campaign saves. Do not deploy without visual screenshot comparison in WebKit and actual iPhone.

## Other UI
Close detail map header should shrink; V104 does this, which can be reused independently if helpful. Native pinch still needs physical iPhone verification.

No changes to the production campaign or save key were made in this V104 experiment.
