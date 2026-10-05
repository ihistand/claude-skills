---
name: stl-generator
description: Generate 3D-printable STL files for woodworking jigs and fixtures with build123d (Python CAD). Use when the user wants a circle-cutting trammel or lampshade-ring jig, an angle wedge, spacing or setup blocks, a drilling guide, a router template, an alignment or assembly fixture, or any custom 3D-printed woodworking aid. Ships ready scripts plus a print-readiness check that refuses STLs that would misprint. Default build volume is an Elegoo Neptune 4 Pro (220 x 220 x 260 mm usable), overridable per printer. Metric units.
---

# STL Generator for Woodworking Jigs

Design jigs as parametric build123d scripts and export STLs that print right the
first time. The deliverable is the STL: the printer matters only for whether the part
fits the bed and which clearances hold, and both are parameters.

## Running build123d

The scripts live in `${CLAUDE_SKILL_DIR}/scripts/` (this skill's folder). Run them
with uv, which needs no setup and works on any Python version:

```bash
uv run --with build123d python ${CLAUDE_SKILL_DIR}/scripts/spacing_block.py 10
```

Without uv: create a venv and `pip install build123d`, then run with that venv's
python. Write the STLs into the user's working directory (or where they ask), never
into the skill's own folder.

## Ready scripts

All three take `--bed XxYxZ` for a printer other than the default, `-o` for the output
name, and `--help` for every option and its default. The examples below shorten the
command to `python scripts/...`; run them the uv way shown above. Each script is
tested and ends in the print-readiness check, so its output needs no extra measuring.

**`scripts/circle_cutting_jig.py`**: a router trammel for discs and rings.

```bash
python scripts/circle_cutting_jig.py 300 250 --mount <BC>:<N>   # ring: 300 OD, 250 ID
python scripts/circle_cutting_jig.py 200 --bit 12.7              # disc only, 1/2" bit
```

A plate screws to the router; an arm carries one pivot hole per cut, placed for the
bit (outer edge at D/2 + bit/2, inner edge at D/2 - bit/2), so the circle comes out at
the size asked for. Before running it, ask the user for two things you cannot assume:
the bit's cutting diameter, and the router sub-base screw pattern (bolt-circle
diameter `<BC>` and screw count `<N>`, measured on their router). If they cannot say
yet, generate it anyway with the 1/4" default bit and no `--mount`, and tell them both
assumptions: a plate without screw holes can be drilled using the router's own
sub-base as a template.

For a ring, the **outer edge is cut first and the inner edge last**: the inner cut
frees the center disc that holds the pivot pin, so nothing can pivot after it. Tell
the user so, and to fix the blank to a sacrificial board so neither piece shifts once
cut free. The script prints the cut order too.

**`scripts/angle_wedge.py`**: holds work at an exact angle.

```bash
python scripts/angle_wedge.py 15
python scripts/angle_wedge.py 22.5 --depth 80 --width 40
```

Prints on its side so the slope is traced in XY, not stair-stepped by layers. Height
follows from the angle, never the reverse, so the angle is exact; if a steep angle
makes it too tall for the bed, the check refuses it and you should lower `--depth`.

**`scripts/spacing_block.py`**: setup and spacing blocks, single or matched sets.

```bash
python scripts/spacing_block.py 10
python scripts/spacing_block.py --set 5,10,15,20
```

Measuring faces stay flat (engraved label, side scallops, one chamfered corner as an
orientation mark). Every block in a set rests on the bed. Heights that are not a
multiple of the 0.2 mm layer height get a warning, because they cannot print exactly.

## Custom jigs

Read `references/build123d_patterns.md` and `references/printer_specs.md` before
writing code; they hold the clearances, minimum sizes, and the build123d idioms that
keep a part on the bed. Then:

- **Export with `export_checked`** from `scripts/printcheck.py`, not a bare
  `export_stl`. Copy `printcheck.py` next to the custom script so the two travel
  together, rather than importing it from the skill's folder. It refuses an invalid
  shape, a solid that would print in mid-air, or a part too big for the bed at any
  rotation, and rotates the part when only a diagonal fits. If it refuses, change the design (split a long jig into stages that register
  on each other, or shrink it); never hand over an STL it rejected.
- **Verify by measuring the solid, not by re-reading the code.** Probe hole positions
  with `is_inside`, heights with `bounding_box()`, angles from a face's normal. An
  earlier version of this skill shipped scripts that ran cleanly and built a trammel
  with no pivot hole and a 45 degree wedge that measured 26.6; only measuring catches that.

## Design rules that matter for woodworking

- **Reference faces stay flat.** Any face that sits on or against the work is a
  measuring surface. Engrave labels (never emboss) and put them on faces that do not
  touch the work.
- **No knife edges.** A tapered end thinner than about 1 mm will not print. Add a
  short vertical toe; it does not change the slope's angle.
- **Precision features go in XY.** Holes whose axis is vertical print round; slopes
  and angles drawn in the XY plane are as accurate as the printer gets. Orient the
  part so the dimension that matters is in XY.
- **Clearance by fit.** Pivot pins and bushings: +0.1 to 0.2 mm. Screws: +0.3 to
  0.5 mm. Drill guides: the bit plus 0.1 to 0.2 mm, so the bit cannot wander.
- **Split a hole row by indexing, not by a second jig.** When a row of holes is longer
  than the bed, make a shorter jig and have the user move it along, dropping a pin
  through its first hole into the last hole already drilled. The spacing stays exact
  across the move.
- **Mirror text on faces that print face-down.** Text engraved on a face that sits on
  the bed in print orientation reads backwards when viewed from that side, unless the
  sketch is mirrored in the model.
- **Repeated drilling wears plastic.** A drill guide used more than a handful of times
  should take a steel bushing (press-fit, sized from the bushing's OD) rather than
  guide the bit in bare PLA.

## Handing over the result

Give the user:
- the STL's full path, its size, and the solid count (from `export_checked`'s output)
- print orientation (as exported: the STL is already in print orientation),
  perimeters and infill, and whether supports are needed (they should not be)
- which dimensions to check with calipers after printing, and, for anything that must
  fit (pins, hardware, bushings), a suggestion to print a small test piece of just
  that feature first; clearances vary between printers and filaments

If they may want to edit it in CAD later, also export a STEP with `export_step`.
