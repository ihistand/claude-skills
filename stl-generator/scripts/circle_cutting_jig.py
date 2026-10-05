#!/usr/bin/env python3
"""
Circle-cutting trammel for a router: cut discs and rings (lampshade rings, round
frames, tabletops) by swinging the router around a pivot pin.

A round plate screws to the router in place of (or under) its sub-base; an arm runs
out to one pivot hole per cut. Each hole is placed for the bit, not the circle's
center line:

  - outer edge (the disc you keep is inside the cut): pivot = D/2 + bit/2
  - inner edge (a hole; the part you keep is outside): pivot = D/2 - bit/2

so a 300 mm outer diameter really comes out 300 mm. Drive a pin of the same diameter
as --pin into the workpiece center, drop the arm's hole over it, and rout.

For a ring, cut the OUTER edge first and the inner edge last: the inner cut frees the
center disc that holds the pivot pin, so nothing can pivot after it. Fix the blank to
a sacrificial board (screws or double-sided tape outside the ring, and into the
center disc) so neither piece shifts once it is cut free.

    python circle_cutting_jig.py 300 250 --mount 82:3     # ring: 300 OD, 250 ID
    python circle_cutting_jig.py 200 --bit 12.7            # disc only, 1/2" bit
    python circle_cutting_jig.py 300 250 --mount 82:3 --screw 4.5 --head 9

--mount BOLT_CIRCLE:COUNT matches the router's sub-base screw pattern. Measure it on
the actual router (the screw holes' circle diameter and how many there are); without
it the plate has no screw holes and the script says so.
"""

import argparse

from build123d import (
    Align,
    Box,
    BuildPart,
    BuildSketch,
    CounterSinkHole,
    Cylinder,
    Hole,
    Location,
    Locations,
    Mode,
    Plane,
    PolarLocations,
    Text,
    extrude,
)

from printcheck import add_bed_arg, export_checked

THICKNESS = 6.0  # plate and arm
ARM_WIDTH = 30.0
END_MARGIN = 12.0  # material past the outermost pivot hole
PIN_CLEARANCE = 0.2  # snug slide fit on the pivot pin
LABEL_DEPTH = 0.6


def fmt(value):
    return f"{value:g}"


def pivot_radii(outer_d, inner_d, bit):
    cuts = [("outer", outer_d, outer_d / 2 + bit / 2)]
    if inner_d:
        cuts.append(("inner", inner_d, inner_d / 2 - bit / 2))
    return cuts


def circle_jig(outer_d, inner_d=None, bit=6.35, pin=6.0, plate_d=110.0, bit_hole=32.0, mount=None,
               screw=4.5, head=9.0):
    cuts = pivot_radii(outer_d, inner_d, bit)
    plate_r = plate_d / 2
    hole_r = (pin + PIN_CLEARANCE) / 2
    min_r = plate_r + hole_r + 3
    for name, d, r in cuts:
        if r < min_r:
            raise SystemExit(
                f"{name} diameter {fmt(d)} mm puts the pivot at {r:.1f} mm, under the {fmt(plate_d)} mm plate "
                f"(needs >= {min_r:.1f}). Use a smaller --plate, or cut this circle another way."
            )
    if inner_d and inner_d >= outer_d:
        raise SystemExit("inner diameter must be smaller than outer diameter")

    arm_end = max(r for _, _, r in cuts) + END_MARGIN

    with BuildPart() as jig:
        Cylinder(plate_r, THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN))
        Box(arm_end, ARM_WIDTH, THICKNESS, align=(Align.MIN, Align.CENTER, Align.MIN))

        # Bit clearance at the router's center.
        Cylinder(bit_hole / 2, THICKNESS, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Pivot holes, one per cut.
        with Locations(*[(r, 0, THICKNESS) for _, _, r in cuts]):
            Hole(hole_r)

        # Router screws come up through the bottom (the face that slides on the
        # work), so their countersinks are on the bottom and the heads sit flush.
        if mount:
            bolt_circle, count = mount
            with Locations(Location((0, 0, 0), (180, 0, 0))):  # on the bottom face, drilling up
                with PolarLocations(bolt_circle / 2, count, start_angle=-90):  # flipped: lands at +90
                    CounterSinkHole(radius=screw / 2, counter_sink_radius=head / 2, depth=THICKNESS)

        # Engrave each pivot's diameter on the top face, just inboard of its hole,
        # reading across the arm. Skip any label that would run into another hole.
        for name, d, r in cuts:
            x = r - hole_r - 6
            if any(abs(x - other) < hole_r + 5 for _, _, other in cuts if other != r) or x < plate_r + 4:
                print(f"  note: no room to label the {fmt(d)} mm pivot; it is the {name}-edge hole at {r:.1f} mm")
                continue
            with BuildSketch(Plane.XY.offset(THICKNESS)):
                with Locations(Location((x, 0), 90)):
                    Text(f"{'OD' if name == 'outer' else 'ID'} {fmt(d)}", font_size=5)
            extrude(amount=-LABEL_DEPTH, mode=Mode.SUBTRACT)

    return jig.part, cuts


def parse_mount(text):
    try:
        bc, n = text.split(":")
        return float(bc), int(n)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--mount must be BOLT_CIRCLE:COUNT, e.g. 82:3, got {text!r}")


class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    """Keep the docstring's layout and show each option's default."""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=HelpFormatter)
    parser.add_argument("outer", type=float, help="outer diameter to cut, mm (the disc's edge)")
    parser.add_argument("inner", type=float, nargs="?", help="inner diameter to cut, mm (a ring's hole)")
    parser.add_argument("--bit", type=float, default=6.35, help="router bit cutting diameter, mm (6.35 = 1/4 in)")
    parser.add_argument("--pin", type=float, default=6.0, help="pivot pin diameter, mm")
    parser.add_argument("--plate", type=float, default=110.0, help="router mounting plate diameter, mm")
    parser.add_argument("--bit-hole", type=float, default=32.0, help="bit clearance hole diameter, mm")
    parser.add_argument("--mount", type=parse_mount, help="router sub-base screws as BOLT_CIRCLE:COUNT, e.g. 82:3")
    parser.add_argument("--screw", type=float, default=4.5, help="screw clearance hole, mm")
    parser.add_argument("--head", type=float, default=9.0, help="countersink diameter for the screw heads, mm")
    parser.add_argument("-o", "--output")
    add_bed_arg(parser)
    args = parser.parse_args()

    if args.mount and args.mount[0] / 2 + args.head / 2 > args.plate / 2 - 2:
        parser.error("the --mount bolt circle does not fit inside --plate; enlarge the plate")
    if args.mount and args.mount[0] / 2 - args.head / 2 < args.bit_hole / 2 + 2:
        parser.error("the --mount bolt circle runs into the bit hole; shrink --bit-hole")

    part, cuts = circle_jig(
        args.outer, args.inner, args.bit, args.pin, args.plate, args.bit_hole, args.mount, args.screw, args.head
    )
    print(f"Circle-cutting trammel for a {fmt(args.bit)} mm bit:")
    for name, d, r in cuts:
        print(f"  {name} edge {fmt(d)} mm -> pivot hole {r:.2f} mm from the bit's center")
    if args.inner:
        print("  cut order: outer edge first, inner edge LAST (the inner cut frees the disc holding the pin)")
    if not args.mount:
        print(
            "  warning: no --mount given, so the plate has no screw holes; measure the router's sub-base "
            "pattern, or drill the plate using the sub-base as a template"
        )

    name = f"circle_jig_{fmt(args.outer)}" + (f"_{fmt(args.inner)}" if args.inner else "") + "mm.stl"
    export_checked(part, args.output or name, args.bed)


if __name__ == "__main__":
    main()
