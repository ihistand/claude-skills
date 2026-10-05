# build123d Patterns for Jigs

Every snippet here runs as-is on build123d 0.10 through 0.13. Start each script with
`from build123d import *`, and end it with `export_checked` from `scripts/printcheck.py`,
not a bare `export_stl` (see "Export" below for why).

## Build on the bed: z = 0 up

A slicer drops the whole model so its lowest point touches the bed. If one solid
starts higher than another, that solid prints in mid-air. So model every part from
z = 0 upward, and put flat reference faces on z = 0.

`Box` and `Cylinder` are centered on all three axes by default, which puts half the
part below the bed. Pass `align` to rest them on z = 0:

```python
from build123d import *

ON_BED = (Align.CENTER, Align.CENTER, Align.MIN)

with BuildPart() as base:
    Box(120, 80, 6, align=ON_BED)            # z from 0 to 6, centered in X and Y
    Cylinder(10, 20, align=ON_BED)           # a post, also from z = 0
```

## Holes

`Hole` drills down (-Z) from the current location, through the whole part by default.
To drill from the top, put the location on the top face:

```python
from build123d import *

T = 6
with BuildPart() as plate:
    Box(100, 60, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((-35, 0, T), (35, 0, T)):
        Hole(radius=5.3 / 2)                                 # M5 clearance, through
    with Locations((0, 0, T)):
        CounterBoreHole(radius=3.3 / 2, counter_bore_radius=3.2, counter_bore_depth=3)
```

Screws that come up through the face that slides on the work need their countersink
on the bottom so the heads sit flush. Flip the location to drill upward from z = 0:

```python
from build123d import *

T = 6
with BuildPart() as plate:
    Box(100, 60, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations(Location((0, 0, 0), (180, 0, 0))):        # bottom face, drilling up
        with PolarLocations(20, 3, start_angle=-90):           # flipped: first hole lands at +90 deg
            CounterSinkHole(radius=4.5 / 2, counter_sink_radius=9 / 2, depth=T)
```

The flip mirrors Y, so angles passed to `PolarLocations` come out mirrored. Check where
holes landed (see "Verify by measuring") instead of trusting the angle you wrote.

Holes only cut the part of the builder they are in. A `Hole` inside a nested
`BuildPart` cuts that (empty) nested part, not your jig, so it silently does nothing.

## Profiles: sketch, then extrude

For anything with an exact angle or a custom outline, draw the 2D profile and
extrude it. Angles come out exact because they are computed, not approximated:

```python
import math
from build123d import *

angle, depth, toe, width = 15, 60, 2, 80
rise = toe + depth * math.tan(math.radians(angle))
with BuildPart() as wedge:
    with BuildSketch():
        Polygon((0, 0), (depth, 0), (depth, rise), (0, toe), align=None)
    extrude(amount=width)
```

`align=None` keeps the polygon's coordinates as written; the default re-centers it.

## Fences, walls, and pins

Join features to the base with ordinary `Box`/`Cylinder` calls at the right height:

```python
from build123d import *

T, FENCE_H = 6, 15
with BuildPart() as jig:
    Box(150, 100, T, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((0, -50 + 4, T)):                                 # fence along the back edge
        Box(150, 8, FENCE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((-50, 10, T), (50, 10, T)):                        # 6 mm alignment pins
        Cylinder(3, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
```

## Labels: engrave, never emboss, and keep them off reference faces

Raised (embossed) text on a face that touches the work changes the jig's dimension
and marks the wood. Engrave instead, on a face that does not touch the work:

```python
from build123d import *

H = 10
with BuildPart() as block:
    Box(50, 30, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with BuildSketch(Plane.XY.offset(H)):                  # sketch on the top face
        Text("10", font_size=8)
    extrude(amount=-0.6, mode=Mode.SUBTRACT)               # 0.6 mm deep
```

Text under about 3 mm tall is not legible at a 0.4 mm nozzle; leave it off and say so
rather than printing a smudge. Rotate a label with `Location((x, y), angle)` inside
`Locations`.

## Edge selection: chamfers and fillets

```python
from build123d import *

with BuildPart() as block:
    Box(50, 30, 10, align=(Align.CENTER, Align.CENTER, Align.MIN))
    fillet(block.edges().filter_by(Axis.Z), radius=2)                # round the 4 vertical edges
    chamfer(block.edges().group_by(Axis.Z)[-1], length=0.5)          # ease the top edges
```

- `edges().filter_by(Axis.Z)`: edges parallel to Z (the vertical ones)
- `edges().group_by(Axis.Z)[-1]`: the edges at the highest Z (the top face's edges)
- `faces().sort_by(Axis.Z)[-1]`: the top face

Fillet or chamfer before cutting holes and text near those edges; filleting after
complex boolean cuts is the most common cause of a build123d exception.

## Several parts in one STL

Lay separate parts out side by side, each resting on z = 0, and add them together:

```python
from build123d import *

parts = [Box(40, 20, h, align=(Align.CENTER, Align.CENTER, Align.MIN)) for h in (5, 10, 15)]
plate = parts[0]
for i, p in enumerate(parts[1:], start=1):
    plate = plate + Pos(i * 45, 0, 0) * p
```

## Verify by measuring

A script that runs without errors can still build the wrong part. Measure the
result instead of re-reading the code:

```python
from build123d import *

with BuildPart() as plate:
    Box(100, 60, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))
    with Locations((35, 0, 6)):
        Hole(radius=2.65)
p = plate.part

bb = p.bounding_box()
assert abs(bb.min.Z) < 1e-6                       # rests on the bed
assert len(p.solids()) == 1                       # one piece, nothing floating
assert not p.is_inside(Vector(35, 0, 3))          # the hole is where intended
assert p.is_inside(Vector(35 + 2.8, 0, 3))        # and no bigger than intended
```

Probe the features that matter for the jig to work: hole positions, the actual angle
of a slope (from a face's `normal_at()`), the height of a reference face.

## Export

```python
from build123d import *
from printcheck import export_checked, parse_bed

with BuildPart() as guide:
    Box(100, 60, 6, align=(Align.CENTER, Align.CENTER, Align.MIN))

export_checked(guide.part, "drill_guide.stl")                         # default bed, 220 x 220 x 260
export_checked(guide.part, "drill_guide.stl", parse_bed("250x210x210"))
```

`export_checked` refuses to write an STL that would misprint: an invalid shape, a
solid starting above the bed, or a part too big for the bed at any rotation. It rotates
the part about Z when that is the only way it fits, and prints the size, solid count,
and weight. Copy `scripts/printcheck.py` next to your script so the import works and the two
travel together.

To also hand over an editable CAD file, `export_step(part, "drill_guide.step")`.
