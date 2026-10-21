# Century of Empires — V113 checkpoint (Oct 20/21 2026)

The user supplied physical iPhone screenshots of V112 that show two issues:
1. A false thin diagonal road across the rocky river north of the existing bridge; previous drawn routes wrongly followed it.
2. Camera panning at Town zoom exposed a large unrendered blurry/blank band beneath the illustration. Some local route alignment still needed.

V113 isolated prototype: v113-bridge-camera-repair.html (created separately from V109-V112; all preexisting versions, V94 gameplay and campaign saves untouched).
- Retains the approved V109 embedded village illustration and most previously accepted northern road path.
- Bridge branch forks at visual-road junction [437,742], approaches the physical stone bridge [364,753], traverses it to around [611,803].
- Far-bank proposed trail now continues *along the lower southeast side*, to artwork edge [1100,842], instead of diagonally crossing the river again. Narrow low-opacity dirt overlay uses exactly the navigable branch centerline after the bridge.
- South main route is separate and exits lower image edge [315,842].
- Town camera span set to 90% of art height and clamped against image bounds at closest zoom to prevent large blank bands when panning. At wider scales geographic map remains pannable.
- Route selection, march/halt, debug dots, zoom views and army inspector retained; full military game is NOT integrated.

Verification: GitHub source readback, JavaScript compile, simulated DOM initialization, 2-route selection, movement toggling, close camera boundary passed. Newly added scripts/qa_v113_bridge_camera.py and .github/workflows/qa-v113-bridge-camera.yml for mobile Chromium/WebKit but PASSING RESULTS UNCONFIRMED. Actual iPhone visual correctness pending new user screenshots. No claim that a real historical far-bank road exists; this is a proposed tactical layout / illustration, not verified georeferenced historical passage.

Required next:
1. Open v113 on iPhone: choose Town, Cross bridge, Show route, March. Confirm route stays on stone bridge and south edge, and dragging does not reveal bottom blank area.
2. If still wrong, STOP guessing coordinates. Rebuild/repaint artwork and road as ONE authored geo-aligned asset and derive the game route from same authored geometry. User prioritizes realism and refuses painted roads disconnected from path.
3. Beyond map edge, route must connect to next seamless geography/tile; unfinished.
4. Integrate approved zoom camera with actual game V94, maintaining army functions across zoom. An army of 4 component units may split into 4 real clickable units with separate positions, orders, morale/strength/readiness/supplies and merge, without adding soldiers. Halt, entrench, redirect, force march, retreat, terrain combat retained.

Review URL: https://wayfinderandco0-cell.github.io/century-of-empires/v113-bridge-camera-repair.html
