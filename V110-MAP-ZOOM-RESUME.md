# Century of Empires V110 checkpoint (2026-10-20)
- V109 Alpine illustration and 39-point painted-road alignment are USER APPROVED on an actual iPhone. Preserve both.
- New V110 prototype: v110-zoom-continuity.html. Four continuous levels: Europe atlas (V94), Central Europe (V90), Brenner (V97), and approved V109 Matrei artwork. Pan, pinch, zoom, four scene presets, restrained labels, demo army march/halt/select, route debug optional.
- Geography in atlas/region/pass layers comes from their existing repository measured elevation assets. The oblique illustrated V109 artwork has only an approximate geographic anchor. It is NOT rigorously georeferenced.
- Full game V94, V100, V109 and campaign saves preserved. V110 is a standalone graphics/interaction proof, not integrated with the real military/economy simulation.
- Keep main game army commands in mind: halt/resume, redirect, entrench, force march, retreat, morale, strength, unit counts, splitting and merging.
- A formation with four detachable component units must be splittable into four REAL independently selectable and ordered formations. No new soldiers may be created by splitting. Merging remains possible.
- Verification: GitHub readback, Javascript compilation and expected 39 points succeeded. scripts/qa_v110_zoom.py and .github/workflows/qa-v110-zoom.yml added. No verified passing browser run or physical iPhone QA yet.
- Next: user iPhone test of all four layers and visual transitions; correct camera/registration errors without spoiling V109; then integrate with actual shared army engine, not simulated controls.
