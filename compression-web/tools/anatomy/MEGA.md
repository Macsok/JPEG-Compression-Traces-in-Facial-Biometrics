# Compression engine — Anatomy Hero

Concept: an exposed image-processing instrument on a machined motherboard.
A moving bridge selects a column on an 8 × 8 sample, a processor die carries
that selection onward through surface traces, and an eight-channel output bank
indicates the selected column. The diagram is illustrative, not model telemetry.

The instrument is fixed in the viewport. Page scroll changes the camera crop
from the sensor to the processor and then to the output bank. Pointer movement
adds a small eased offset. An explicit scan slider, automatic-tour pause, and
three camera presets provide equivalent keyboard controls. Reduced motion
disables the tour, camera travel and pointer parallax.

Parts planned before geometry (about 140 structural solids):

- Chassis: four feet, four pads, two-layer base, PCB, four PCB supports, eight
  corner fasteners, eight edge standoffs, two perimeter strips, two handles with
  four mounting blocks, two front connector shells and their inset tongues.
- Sensor: socket, sample tray, 64 flat pixel inlays, two rail beds, two guide
  rails, four end stops, two shoes, two uprights, crossbeam, sensor body, lens
  window, top cap, two mounting plates, ruler and its mounting screws.
- Processor: socket, package, exposed die, four hold-down clamps, eight flat
  terminal banks, two VRM blocks, eight regulator packages, six square
  capacitor packages, one heat spreader and twelve separate cooling fins.
- Memory: two sockets, two upright DIMM boards, eight chips, four end catches,
  eight flat contact strips, etched bus tracks.
- Output: daughterboard, four supports, eight channel housings with inset
  windows, eight contact pads, eight signal cells, two retaining clips and
  their fasteners, an engraved identification plate.

Surface details: PCB tracks end at plated pads; all vents and grooves are
closed contours; scale ticks touch a ruler edge; screws are flat engravings.
Parts are shaded prisms. There are no tubes, unsupported floating slabs or
rounded bodies needing the lathe audit. Static overlapping assemblies are
painted by depth; the moving sensor's layer sits above the tray and rails,
with its complete travel kept clear of the neighboring processor and memory.

Build with `node tools/build-engine.mjs`. The generated SVG is checked in.
No build kit, third-party JS, font or image is downloaded by the page.
