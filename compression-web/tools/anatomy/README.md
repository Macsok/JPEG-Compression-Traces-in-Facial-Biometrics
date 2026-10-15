# Pixel inspection bench (Anatomy Figure)

Concept: a scanning bridge travels over a mounted 8 × 8 grayscale sample;
its position selects one of eight columns. The readout and highlighted pixels
share that column index. This is an illustration of a JPEG block, not inference
or a simulation of the application's feature extraction.

Parts, before geometry: four feet, base, gasket, deck, sample socket, sample
plate, 64 pixel inlays, two rail foundations, two rails, four end stops, four
rail fasteners, two sliding shoes, two bridge uprights, bridge beam, sensor
housing, sensor window, sensor cap, four bridge fasteners, ruler strip, label
plate, two label fasteners, control plinth, two square keys, four key surrounds,
eight ventilation slots, perimeter groove and corner screw engravings.
The grid inlays are flat; the structural parts are solid shaded prisms.

The base supports the sample and rails. Shoes sit on the rails, uprights on
the shoes, and the beam on the uprights. The sensor clears the sample over
the complete travel. Layer order: base, rear rail, sample, front rail, bridge.
Only the bridge translates, along the rails. No WebGL or runtime dependency.

Run `node tools/build-inspector.mjs` from this directory's application root
to rebuild the checked-in template. Node is only needed when editing geometry.
The browser uses the generated SVG and `app/static/inspector.js`.

Geometry kit and CSS vendored from https://github.com/wheresryan22/anatomy
(MIT; license in this directory). Styles inherit the application's theme.
