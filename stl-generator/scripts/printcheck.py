#!/usr/bin/env python3
"""
Print-readiness check and STL export for build123d parts.

Every generator script ends with `export_checked(part, path, bed)`. It refuses to
write an STL that a slicer would print wrong, instead of letting a broken file
reach the printer:

  - the shape is valid (closed, manifold solids)
  - every solid rests on the bed (z = 0); a solid that starts higher prints in mid-air
  - the part fits the bed, rotating it about Z if that is the only way it fits

It also warns, without refusing, about surfaces that slope more than 45 degrees from
vertical (they need supports, a different orientation, or a split) and notes flat
undersides, which bridge fine over short spans.

Use it for custom parts too (run the script from this directory, or put it on sys.path):

    from printcheck import export_checked, parse_bed
    export_checked(part, "jig.stl", parse_bed("220x220x260"))
"""

import argparse
import math
import sys

from build123d import Axis, Pos, export_stl

# Elegoo Neptune 4 Pro: 225 x 225 x 265 mm nominal, less a margin for the
# skirt/brim and clips. Override with --bed for another printer.
DEFAULT_BED = (220.0, 220.0, 260.0)
LAYER_HEIGHT = 0.2
PLA_DENSITY = 1.24  # g/cm^3
Z_TOL = 1e-3
OVERHANG_LIMIT = 45.0  # degrees from vertical a 0.4 mm nozzle bridges without support


def parse_bed(text):
    """'220x220x260' -> (220.0, 220.0, 260.0)"""
    try:
        x, y, z = (float(v) for v in text.lower().split("x"))
    except ValueError:
        raise argparse.ArgumentTypeError(f"bed must look like 220x220x260, got {text!r}")
    return (x, y, z)


def add_bed_arg(parser):
    parser.add_argument(
        "--bed",
        type=parse_bed,
        default=DEFAULT_BED,
        metavar="XxYxZ",
        help="usable build volume in mm; the default is an Elegoo Neptune 4 Pro",
    )


def _is_valid(shape):
    valid = shape.is_valid
    return valid() if callable(valid) else valid  # method in build123d <0.11, property after


def fit_to_bed(part, bed):
    """Return (part, angle) rotated about Z so it fits the bed, or (None, None)."""
    for angle in range(0, 91, 5):
        candidate = part.rotate(Axis.Z, angle) if angle else part
        size = candidate.bounding_box().size
        if size.X <= bed[0] and size.Y <= bed[1]:
            return candidate, angle
    return None, None


def check(part, bed):
    """Return (problems, part_ready_to_export). An empty list means printable."""
    problems = []

    if not _is_valid(part):
        problems.append("shape is not valid (open or self-intersecting); a slicer may print it wrong")

    solids = part.solids()
    if not solids:
        return ["no solids: nothing would print"], part

    bed_z = min(s.bounding_box().min.Z for s in solids)
    for i, s in enumerate(solids):
        lift = s.bounding_box().min.Z - bed_z
        if lift > Z_TOL:
            problems.append(
                f"solid {i + 1} of {len(solids)} starts {lift:.2f} mm above the bed and would print in mid-air"
            )

    # Rest the lowest point on z = 0 so the STL opens on the bed in any slicer.
    if abs(bed_z) > Z_TOL:
        part = Pos(0, 0, -bed_z) * part

    height = part.bounding_box().size.Z
    if height > bed[2]:
        problems.append(f"{height:.1f} mm tall; the printer's Z limit is {bed[2]:.0f} mm")

    fitted, angle = fit_to_bed(part, bed)
    if fitted is None:
        size = part.bounding_box().size
        problems.append(
            f"footprint {size.X:.1f} x {size.Y:.1f} mm does not fit the {bed[0]:.0f} x {bed[1]:.0f} mm bed "
            "at any rotation; make it smaller or split it into parts"
        )
    else:
        if angle:
            print(f"  note: rotated {angle} deg about Z to fit the bed")
        part = fitted

    return problems, part


def overhangs(part, limit_deg=OVERHANG_LIMIT, tolerance=0.05):
    """Down-facing surfaces above the bed, split into two kinds.

    Returns {"slope": (area_mm2, z_min, z_max) or None, "flat": area_mm2}.
    "slope" is surface tilted more than `limit_deg` from vertical: it needs supports
    (or another orientation, or a split), or the printer lays plastic on air. "flat"
    is level undersides: the printer bridges those, which works for short spans
    (ledges, steps, holes) but not wide ones. Faces resting on the bed are excluded.
    """
    sin_limit = math.sin(math.radians(limit_deg))
    verts, tris = part.tessellate(tolerance, 0.1)
    z_bed = part.bounding_box().min.Z
    slope, flat, zs = 0.0, 0.0, []
    for a, b, c in tris:
        n = (verts[b] - verts[a]).cross(verts[c] - verts[a])  # points out of the material
        length = n.length
        if length == 0:
            continue
        down = -n.Z / length
        if down <= sin_limit:
            continue
        tz = (verts[a].Z + verts[b].Z + verts[c].Z) / 3
        if tz - z_bed < Z_TOL * 10:
            continue  # the face on the bed
        if down > 0.999:
            flat += length / 2
        else:
            slope += length / 2
            zs.append(tz)
    # Under 1 mm^2 is tessellation noise, not a real overhang.
    return {
        "slope": (slope, min(zs) - z_bed, max(zs) - z_bed) if slope >= 1.0 else None,
        "flat": flat if flat >= 1.0 else 0.0,
    }


def summarize(part):
    bb = part.bounding_box()
    grams = part.volume / 1000 * PLA_DENSITY
    return (
        f"{bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f} mm, "
        f"{len(part.solids())} solid(s), ~{grams:.0f} g PLA at 100% infill"
    )


def export_checked(part, path, bed=DEFAULT_BED):
    """Check, then export; exit non-zero without writing if the part would misprint."""
    problems, part = check(part, bed)
    if problems:
        print(f"NOT EXPORTED: {path}", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)
    export_stl(part, path)
    print(f"STL saved to {path}: {summarize(part)}")
    hang = overhangs(part)
    if hang["slope"]:
        area, z0, z1 = hang["slope"]
        print(
            f"  warning: {area / 100:.1f} cm^2 of surface slopes past {OVERHANG_LIMIT:.0f} deg from vertical "
            f"(between {z0:.1f} and {z1:.1f} mm up); it needs supports there"
        )
    if hang["flat"]:
        print(
            f"  note: {hang['flat'] / 100:.1f} cm^2 of flat underside; fine as a bridge if no span is "
            "wider than about 30 mm, otherwise support it"
        )
    return part

