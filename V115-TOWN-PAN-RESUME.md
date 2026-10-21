# Century of Empires — V115 Town Pan & Controls checkpoint

October 20–21, 2026. Original game remains unchanged. Last physical iPhone screenshot IMG_4863.jpeg shows V114 filling the screen but the army appears off-path; three rows of map controls obscure the bottom, and town view effectively cannot pan far enough to expose the stone bridge.

## What was built in V115
New standalone v115-town-pan-controls.html built from V114. V109 embedded visual artwork preserved, V94/V100/V109–V114, gameplay and saved campaigns left untouched.
- Town preset span reduced from ~90% of entire art height to ~54%, so a phone sees the town at closer magnification with meaningful free vertical panning within the art.
- Camera remains clamped to actual visible artwork bounds so users cannot expose an empty band.
- Bottom toolbar now just Orders, Army, Bridge, Map; Orders and Map expand independently and hide by default. Only a 43px row should cover map at rest.
- Army button centers camera on formation and follows it during march; manual touch-drag switches follow OFF; tapping Army switches it ON.
- Bridge button moves the camera to the real rendered stone bridge area in one tap and disables army-follow.
- Four Europe/Region/Pass/Town presets remain under Map. Route choices, March/Halt, Reset, Show route remain under Orders.
- Existing bridge path stops on the visible far bank. No fake bridge-road extension drawn. Actual geographic continuation remains unfinished.

## Validation
- GitHub V115 source readback with approved embedded JPEG and JavaScript syntax passed.
- Simulated DOM test passed initial compact UI, Town span ~0.186 atlas units vs ~0.344 full art height, 300px map drag y camera displacement ~0.065 units, within-image clamp, bridge focus, drawer transitions, march/halt, follow-on-march, follow-off-on-touch, follow-resume via Army.
- Real Chromium/WebKit iPhone-size browser test and workflow published at scripts/qa_v115_pan.py and .github/workflows/qa-v115-pan.yml. Passing workflow evidence not yet read; physical iPhone screenshot still needed.
- Important: V115 fixes the reported map panning and control coverage structurally but DOES NOT verify or fix any remaining graphic road/path mismatch. Do not call the entire route correct.

## Path integrity and next step
The approved V109-looking imagery is an oblique 1100x842 illustration. Road centerlines after the village and the bridge approach have been guessed in V110-V114, causing repeated drift. DO NOT keep inventing revised endpoints. Need a single visual/geographic road graph aligned pixel-for-pixel to the actual painted track, ideally author art and path together. The 1800s cart-road continuation beyond the stone bridge remains unverified and should not be faked.
Ask user to open V115 on iPhone, tap Bridge, check bridge pan (and drag). To diagnose drifting segments ask for one clear screenshot with Orders > Show route while Town map centered on roadway, not a shot with debug off.
Keep future full gameplay: any army comprising 4 detachable units must split into 4 real independently selectable armies, each with distinct ID/orders/position/morale/supplies, and able to merge; halt, entrench, redirect, retreat, force march, terrain combat preserved across all 4 zoom levels. V115 is an isolated visual interaction prototype and does NOT implement these military systems in production.

Review: https://wayfinderandco0-cell.github.io/century-of-empires/v115-town-pan-controls.html
