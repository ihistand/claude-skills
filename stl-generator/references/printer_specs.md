# Printer Profile and Design Constraints

The deliverable is an STL, so the printer only matters in two places: whether the part
fits the bed, and the clearances a nozzle and material can hold. The defaults below
are for the printer these were tested on, an **Elegoo Neptune 4 Pro**, with a 0.4 mm
nozzle and PLA. For another printer, pass `--bed XxYxZ` to any script (or `parse_bed`
in custom code) and treat the clearances as a starting point for a test print.

## Build volume
- Nominal: 225 x 225 x 265 mm
- **Usable (the default): 220 x 220 x 260 mm**, leaving room for a skirt or brim
- A long part that misses the bed straight can still fit on the diagonal (up to about
  300 mm for a narrow arm); `export_checked` tries rotations automatically.

## Print settings assumed
- Layer height 0.2 mm, nozzle 0.4 mm, PLA
- 3 to 4 perimeters and 20 to 40% infill for jigs; 100% for small parts that take
  clamping pressure, such as spacing blocks
- PLA softens around 55 to 60 C: not for jigs left in a hot car or near a heat gun

## Accuracy you can rely on
- XY: about +/-0.1 to 0.2 mm. Z: the nearest layer (0.2 mm steps), so a height that
  is not a multiple of the layer height prints a little over or under.
- **Profiles drawn in XY are the most accurate.** That is why the angle wedge prints
  on its side: its slope is traced by the nozzle instead of stair-stepped by layers.
- Vertical holes (axis along Z) print round but slightly undersized; horizontal holes
  sag at the top. Put precision holes vertical.
- The first layer spreads slightly ("elephant's foot"). For a reference face on the bed,
  a 0.4 mm chamfer on the bottom edges, or the slicer's elephant-foot compensation,
  keeps it from flaring.

## Clearances
| Fit | Add to the nominal size | Use for |
|---|---|---|
| Press fit | -0.1 to 0.0 mm | pins that should stay put |
| Slide fit | +0.1 to +0.2 mm | pivot pins, guide bushings |
| Loose fit | +0.3 to +0.5 mm | screws and bolts passing through |

Fit is printer-specific. For anything that must fit, print a small test coupon of
just that feature first (a 10 mm-thick plate with the hole) before the full jig.

## Minimums
- Wall: 0.8 mm is two perimeters and prints; 2 to 3 mm for anything that takes load
- Feature: 1 mm; holes: 2 mm diameter
- Engraved text: at least 3 mm tall, 0.4 to 0.6 mm deep
- Flat reference base: at least 5 mm thick so it stays flat
- Overhang: up to 45 degrees without supports; bridges up to about 30 mm

## Hardware clearance holes
| Hardware | Hole |
|---|---|
| M3 | 3.3 mm |
| M4 | 4.3 mm |
| M5 | 5.3 mm |
| M6 | 6.4 mm |
| #6 wood screw | 3.7 mm |
| #8 wood screw | 4.5 mm |
| #10 wood screw | 5.1 mm |
| 1/4"-20 bolt | 6.6 mm |

Countersink diameter: about twice the screw diameter (9 mm for a #8 flat-head).

## Router and tool clearances
- Bit clearance slot or hole: the bit's **cutting** diameter plus at least 2 mm
  (the shank is irrelevant; the cutter is what passes through). A 1/4" (6.35 mm)
  straight bit needs 8.5 mm or more; a 1/2" (12.7 mm) bit needs 15 mm or more.
- Template guide bushings: 5/8" (15.9 mm) OD is the most common; match the user's set.
- Router sub-base screw patterns vary by model. Ask for the measured bolt-circle
  diameter and screw count; never guess one.
- Clamp access: 25 mm or more of clear space for a clamp jaw.

## Rough print times at 0.2 mm
- Small (50 x 50 x 10 mm): 1 to 2 hours
- Medium (100 x 100 x 20 mm): 4 to 6 hours
- Large (200 x 200 x 30 mm): 12 to 18 hours

These are ballpark figures; the slicer's estimate is the one to quote.
