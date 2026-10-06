#!/usr/bin/env python3
"""
Replacement threaded light globe: a hollow sphere on a threaded collar that screws
into a fixture in place of a glass globe (the "fitter" globes on porch and ceiling
lights).

Every dimension comes from measuring the original with calipers. Bare numbers are
mm; add "in" for inches (5.700in), or pass --inches to make bare numbers inches.

    python threaded_globe.py --inches --diameter 5.700 --height 6.2 \\
        --crest 3.235 --root 3.110 --pitch 0.232 --collar 0.713 --bore 2.825

A hollow sphere cannot print in one piece without supports on its outside: the
shell overhangs past 45 degrees below the equator and is flat on top. So by default
the globe is split at the equator into two halves that join with a half-lap and
glue, each printed rim-down so any supports stand inside, where their marks are
least visible. --one-piece prints it whole, collar down, with outside supports.

--collar-test writes only the threaded collar, which prints in under an hour: screw
it into the fixture before committing to the full globe.

Outputs <prefix>_upper.stl and <prefix>_lower.stl (or <prefix>.stl with
--one-piece, or <prefix>_collar_test.stl), already in print orientation.
"""

import argparse
import math
import sys

from build123d import (
    Align,
    Axis,
    BuildLine,
    BuildPart,
    BuildSketch,
    Cylinder,
    Helix,
    Line,
    Mode,
    Plane,
    Polyline,
    Pos,
    Rot,
    Sphere,
    ThreePointArc,
    Vector,
    make_face,
    revolve,
    sweep,
    export_step,
)

from printcheck import add_bed_arg, export_checked

INCH = 25.4
LAP = 4.0  # height of the half-lap joint at the equator
LAP_GAP = 0.15  # radial clearance in the lap, for glue
THREAD_OVERLAP = 0.3  # thread profile sinks this far into the collar so they fuse
MIN_COLLAR_WALL = 2.0


class Spec:
    """All dimensions in mm, derived values included."""

    def __init__(self, a):
        self.R = a.diameter / 2
        self.H = a.height
        self.wall = a.wall
        self.r_crest = (a.crest - a.clearance) / 2
        self.r_root = (a.root - a.clearance) / 2
        self.pitch = a.pitch
        self.collar = a.collar
        self.thread_len = a.thread_length or a.collar
        self.r_bore = a.bore / 2
        self.left_hand = a.left_hand

        self.depth = self.r_crest - self.r_root
        self.z_c = self.H - self.R  # sphere center = the equator
        self.r_neck = self.r_crest
        self.z_join = self.z_c - math.sqrt(self.R**2 - self.r_neck**2)  # outer sphere meets neck
        ri = self.R - self.wall
        self.z_join_in = self.z_c - math.sqrt(ri**2 - self.r_bore**2)  # inner sphere meets bore

    def problems(self):
        p = []
        if self.r_root >= self.r_crest:
            p.append("thread root must be smaller than the crest diameter")
        if self.pitch >= self.thread_len:
            p.append(
                f"pitch {self.pitch:.2f} mm is longer than the threaded length {self.thread_len:.2f} mm, "
                "so the thread would not make one turn. Pitch is the distance from one crest to the next: "
                "measure across several crests and divide by the number of gaps"
            )
        if self.r_root - self.r_bore < MIN_COLLAR_WALL:
            p.append(
                f"collar wall would be {self.r_root - self.r_bore:.1f} mm (root minus bore); "
                f"at least {MIN_COLLAR_WALL} mm is needed to print and hold the thread"
            )
        if self.r_neck >= self.R:
            p.append("the collar is wider than the globe")
        elif self.z_join < self.collar:
            p.append(
                f"overall height {self.H:.1f} mm is too short: the sphere would cut into the collar. "
                "Measure from the collar's rim to the very top of the globe"
            )
        if self.z_c - self.collar < LAP + 5 and not p:
            p.append("the equator is too close to the collar to split there; use --one-piece")
        return p


def shell(s):
    """The globe without threads: one revolved profile, collar at z = 0."""
    ri = s.R - s.wall
    with BuildPart() as part:
        with BuildSketch(Plane.XZ):  # sketch x = radius, sketch y = height
            with BuildLine():
                Polyline(
                    (s.r_bore, 0),
                    (s.r_root, 0),
                    (s.r_root, s.collar),
                    (s.r_neck, s.collar),
                    (s.r_neck, s.z_join),
                )
                ThreePointArc((s.r_neck, s.z_join), (s.R, s.z_c), (0, s.H))
                Line((0, s.H), (0, s.H - s.wall))
                ThreePointArc((0, s.H - s.wall), (ri, s.z_c), (s.r_bore, s.z_join_in))
                Line((s.r_bore, s.z_join_in), (s.r_bore, 0))
            make_face()
        revolve(axis=Axis.Z)
    return part.part


def thread(s):
    """Rounded ridge (crest about as wide as the gap) swept along a helix on the collar."""
    z0 = (s.collar - s.thread_len) + s.pitch / 2
    z1 = s.collar - s.pitch / 2
    if z1 <= z0:
        z1 = z0 + 1e-3
    half = 0.49 * s.pitch
    n = 24
    pts = [(-half, -THREAD_OVERLAP)]
    for i in range(n + 1):
        u = -half + 2 * half * i / n
        pts.append((u, s.depth * (1 + math.cos(2 * math.pi * u / s.pitch)) / 2))
    pts.append((half, -THREAD_OVERLAP))

    with BuildPart() as part:
        with BuildLine() as path:
            Helix(pitch=s.pitch, height=z1 - z0, radius=s.r_root, center=(0, 0, z0), lefthand=s.left_hand)
        wire = path.wires()[0]
        start, tangent = wire.position_at(0), wire.tangent_at(0)
        # Sketch y must point radially outward for either hand: y = z x x, so x = outward x z.
        outward = Vector(start.X, start.Y, 0).normalized()
        with BuildSketch(Plane(start, x_dir=outward.cross(tangent), z_dir=tangent)):
            with BuildLine():
                Polyline(*pts, close=True)
            make_face()
        sweep(path=wire, is_frenet=True)
        # Nothing may hang below the rim.
        Cylinder(s.R * 2, 50, align=(Align.CENTER, Align.CENTER, Align.MAX), mode=Mode.SUBTRACT)
    return part.part


def lap_band(s, r_in, r_out, z_lo, z_hi):
    """A spherical shell band between radii r_in..r_out (from the globe center), z_lo..z_hi."""
    band = (Pos(0, 0, s.z_c) * Sphere(r_out)) - (Pos(0, 0, s.z_c) * Sphere(r_in))
    slab = Pos(0, 0, z_lo) * Cylinder(s.R * 2, z_hi - z_lo, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return band & slab


def split(globe, s):
    """Upper and lower halves at the equator, joined by a half-lap: the lower half carries
    the inner tongue, the upper half the matching outer lip."""
    big = s.R * 3
    below = Pos(0, 0, s.z_c) * Cylinder(big, big, align=(Align.CENTER, Align.CENTER, Align.MAX))
    above = Pos(0, 0, s.z_c) * Cylinder(big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    lower = globe & below
    upper = globe & above

    mid = s.R - s.wall / 2
    tongue = lap_band(s, s.R - s.wall, mid - LAP_GAP / 2, s.z_c, s.z_c + LAP)
    socket = lap_band(s, s.R - s.wall - 0.5, mid + LAP_GAP / 2, s.z_c - 1, s.z_c + LAP + 0.2)
    return upper - socket, lower + tongue


def length(text, inches):
    t = text.strip().lower()
    for suffix, scale in (("mm", 1.0), ("in", INCH), ('"', INCH)):
        if t.endswith(suffix):
            return float(t[: -len(suffix)]) * scale
    return float(t) * (INCH if inches else 1.0)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    m = parser.add_argument_group("measurements of the original (bare numbers: mm, or inches with --inches)")
    m.add_argument("--diameter", required=True, help="globe outer diameter at its widest")
    m.add_argument("--height", required=True, help="overall height, collar rim to the top of the globe")
    m.add_argument("--crest", required=True, help="collar diameter over the tops of the thread ridges")
    m.add_argument("--root", required=True, help="collar diameter in the bottom of a thread groove")
    m.add_argument("--pitch", required=True, help="crest-to-crest distance (measure several, divide)")
    m.add_argument("--collar", required=True, help="collar height, rim to where the glass curves out")
    m.add_argument("--bore", required=True, help="inside diameter of the opening at the rim")
    m.add_argument("--thread-length", help="length of the threaded part of the collar (default: --collar)")
    parser.add_argument("--inches", action="store_true", help="bare numbers are inches")
    parser.add_argument("--wall", default="2.0", help="sphere wall thickness, mm (1.5 lets more light through)")
    parser.add_argument(
        "--clearance", default="0.2", help="mm taken off the thread diameters so the print screws in (default 0.2)"
    )
    parser.add_argument("--left-hand", action="store_true", help="left-hand thread (most are right-hand)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--one-piece", action="store_true", help="one part, collar down; needs outside supports")
    mode.add_argument("--collar-test", action="store_true", help="only the threaded collar, to test the fit")
    parser.add_argument("-o", "--output", default="globe", help="file name prefix (default: globe)")
    parser.add_argument("--step", action="store_true", help="also write <prefix>.step, the whole globe, for CAD")
    add_bed_arg(parser)
    a = parser.parse_args()

    for name in ("diameter", "height", "crest", "root", "pitch", "collar", "bore", "thread_length"):
        value = getattr(a, name)
        if value is not None:
            setattr(a, name, length(value, a.inches))
    a.wall, a.clearance = float(a.wall), float(a.clearance)

    s = Spec(a)
    problems = s.problems()
    if problems:
        print("Cannot build this globe:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        sys.exit(1)

    turns = (s.thread_len - s.pitch) / s.pitch + 1
    print(
        f"Globe {s.R * 2:.1f} mm on a {s.r_crest * 2:.2f} mm collar (thread {s.depth:.2f} mm deep, "
        f"{s.pitch:.2f} mm pitch, ~{turns:.1f} turns, {'left' if s.left_hand else 'right'}-hand); "
        f"neck {s.z_join - s.collar:.1f} mm; {s.H:.1f} mm tall overall"
    )
    neck = s.z_join - s.collar
    if neck > 3:
        print(
            f"  note: the overall height leaves a {neck:.1f} mm straight neck between the collar and the sphere. "
            "That matches a globe with a short neck; if the glass curves out right at the collar, "
            "re-measure the overall height (rim to the very top)"
        )
    print(
        f"  print: PETG (ASA outdoors), LED bulbs only; 0.2 mm layers; the {s.wall:g} mm wall prints solid "
        "(4+ perimeters), so infill does not matter"
    )

    globe = shell(s) + thread(s)
    if a.step:
        export_step(globe, f"{a.output}.step")
        print(f"STEP saved to {a.output}.step (whole globe, as installed)")

    if a.collar_test:
        top = s.collar + 3
        cut = Pos(0, 0, top) * Cylinder(s.R * 3, s.H, align=(Align.CENTER, Align.CENTER, Align.MIN))
        ring = globe - cut
        print("Collar test: print it rim-down, screw it into the fixture, adjust --clearance if needed")
        export_checked(ring, f"{a.output}_collar_test.stl", a.bed)
    elif a.one_piece:
        print("One piece, collar down: enable supports (they will touch the outside of the shade)")
        export_checked(globe, f"{a.output}.stl", a.bed)
    else:
        upper, lower = split(globe, s)
        print("Upper half: rim down. Supports, build-plate only, stand inside the dome")
        export_checked(Pos(0, 0, -s.z_c) * upper, f"{a.output}_upper.stl", a.bed)
        print("Lower half: rim down, collar up. Supports, build-plate only, stand inside")
        export_checked(Rot(180, 0, 0) * lower, f"{a.output}_lower.stl", a.bed)  # export_checked rests it on the bed
        print(
            f"Join: the lower half's inner tongue ({LAP:.0f} mm) slides into the upper half's lip; "
            "glue with clear epoxy or CA"
        )


if __name__ == "__main__":
    main()
