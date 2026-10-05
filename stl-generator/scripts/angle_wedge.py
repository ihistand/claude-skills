#!/usr/bin/env python3
"""
Angle wedge: holds a workpiece at an exact angle for angled cuts, drilling, and glue-ups.

The STL is in PRINT orientation, lying on its side. The wedge's profile is drawn in
the XY plane, so the slope is traced by the nozzle instead of stair-stepped by
layers, and the angle is as accurate as the printer's XY motion. Stand it on its
long flat face to use it.

The slope rises at exactly the requested angle: depth is fixed and height follows
from it (never the other way round), so a 45 degree wedge is 45 degrees. A short
vertical toe keeps the thin end printable without changing the angle, and an
optional lip at the low end stops the workpiece sliding off.

    python angle_wedge.py 15                      # 15 degrees, 60 mm deep, 80 mm wide
    python angle_wedge.py 22.5 --depth 80 --width 40 -o wedge_22.5deg.stl
    python angle_wedge.py 30 --no-lip
"""

import argparse
import math

from build123d import BuildPart, BuildSketch, Locations, Mode, Plane, Polygon, Text, extrude

from printcheck import add_bed_arg, export_checked

TOE = 2.0  # vertical height of the thin end, so it is not a knife edge
LIP_ALONG = 4.0  # lip thickness along the slope
LIP_UP = 3.0  # lip height above the slope


def fmt(value):
    return f"{value:g}"


def wedge_profile(angle_deg, depth, lip=True):
    """Points of the side profile: x runs along the base, y is up in use."""
    a = math.radians(angle_deg)
    height = TOE + depth * math.tan(a)
    u = (math.cos(a), math.sin(a))  # up the slope
    n = (-math.sin(a), math.cos(a))  # out of the slope
    p0 = (0.0, TOE)  # bottom of the slope

    pts = [(0.0, 0.0), (depth, 0.0), (depth, height)]
    if lip:
        a1 = (p0[0] + LIP_ALONG * u[0], p0[1] + LIP_ALONG * u[1])
        pts += [
            a1,
            (a1[0] + LIP_UP * n[0], a1[1] + LIP_UP * n[1]),
            (p0[0] + LIP_UP * n[0], p0[1] + LIP_UP * n[1]),
        ]
    pts.append(p0)
    return pts, height


def angle_wedge(angle_deg, depth=60.0, width=80.0, lip=True, label=True):
    pts, height = wedge_profile(angle_deg, depth, lip)
    a = math.radians(angle_deg)

    with BuildPart() as wedge:
        with BuildSketch():
            Polygon(*pts, align=None)
        extrude(amount=width)

        if label:
            # Engrave on the upper side face (a non-working face), in the widest
            # part of the triangle, sized to the room available there.
            x_c = depth * 0.62
            room = TOE + x_c * math.tan(a)
            font = min(8.0, room * 0.45, depth * 0.12)
            if font >= 3.0:
                with BuildSketch(Plane.XY.offset(width)):
                    with Locations((x_c, room / 2)):
                        Text(f"{fmt(angle_deg)}°", font_size=font)
                extrude(amount=-0.6, mode=Mode.SUBTRACT)
            else:
                print(f"  note: a {fmt(angle_deg)} deg wedge this size has no room for a legible label; left blank")

    return wedge.part, height


class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    """Keep the docstring's layout and show each option's default."""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=HelpFormatter)
    parser.add_argument("angle", type=float, help="slope angle in degrees (0 < angle < 90)")
    parser.add_argument("--depth", type=float, default=60.0, help="base length along the slope direction, mm")
    parser.add_argument("--width", type=float, default=80.0, help="width across the slope, mm")
    parser.add_argument("--no-lip", action="store_true", help="omit the stop lip at the low end")
    parser.add_argument("-o", "--output")
    add_bed_arg(parser)
    args = parser.parse_args()

    if not 0 < args.angle < 90:
        parser.error("angle must be between 0 and 90 degrees")

    part, height = angle_wedge(args.angle, args.depth, args.width, lip=not args.no_lip)
    print(
        f"Angle wedge: {fmt(args.angle)} deg, {fmt(args.depth)} mm deep x {fmt(args.width)} mm wide, "
        f"{height:.1f} mm tall in use (printed on its side)"
    )
    export_checked(part, args.output or f"wedge_{fmt(args.angle)}deg.stl", args.bed)


if __name__ == "__main__":
    main()
