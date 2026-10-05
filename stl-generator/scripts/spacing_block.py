#!/usr/bin/env python3
"""
Precision spacing / setup blocks for consistent gaps, reveals, and bit-height setup.

The top and bottom faces are the measuring faces, so they stay flat: the label is
engraved (height is unchanged), the finger scallops run vertically through the
sides, and the orientation mark is a chamfer on one vertical corner.

    python spacing_block.py 10                       # one 10 mm block, 50 x 30 footprint
    python spacing_block.py 10 --width 40 --depth 25 -o spacer_10mm.stl
    python spacing_block.py --set 5,10,15,20 -o spacer_set.stl
"""

import argparse
import math

from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Cylinder,
    Locations,
    Mode,
    Plane,
    Pos,
    Text,
    chamfer,
    extrude,
)

from printcheck import LAYER_HEIGHT, add_bed_arg, export_checked

GAP = 5.0  # between blocks in a set


def fmt(value):
    """10.0 -> '10', 12.5 -> '12.5'"""
    return f"{value:g}"


def spacing_block(height, width=50.0, depth=30.0, label=True):
    """One block resting on z=0, `height` mm tall between its measuring faces."""
    scallop_r = min(depth * 0.25, 8.0)
    with BuildPart() as block:
        Box(width, depth, height, align=(Align.CENTER, Align.CENTER, Align.MIN))

        # Finger scallops through the full height on both long sides.
        with Locations((0, depth / 2), (0, -depth / 2)):
            Cylinder(scallop_r, height, align=(Align.CENTER, Align.CENTER, Align.MIN), mode=Mode.SUBTRACT)

        # Orientation mark: chamfer the front-left vertical corner.
        corner = (
            block.edges()
            .filter_by(Axis.Z)
            .sort_by(Axis.X)[0:2]
            .sort_by(Axis.Y)[0]
        )
        chamfer(corner, length=min(3.0, width / 10, depth / 10))

        if label:
            # Engraved, so the block's height stays exact. Shallow on thin blocks.
            engrave = min(0.6, height / 4)
            font = min(8.0, depth - 2 * scallop_r - 2, width / 5)
            if font >= 3.0:
                with BuildSketch(Plane.XY.offset(height)):
                    Text(f"{fmt(height)}", font_size=font)
                extrude(amount=-engrave, mode=Mode.SUBTRACT)
            else:
                print(f"  note: {fmt(height)} mm block is too small to label legibly; left blank")
    return block.part


def spacing_set(heights, width=50.0, depth=30.0, bed_x=220.0):
    """Several blocks laid out in rows that fit the bed, all on z=0."""
    per_row = max(1, int((bed_x + GAP) // (width + GAP)))
    parts = []
    for i, h in enumerate(sorted(heights)):
        row, col = divmod(i, per_row)
        parts.append(Pos(col * (width + GAP), row * (depth + GAP), 0) * spacing_block(h, width, depth))
    result = parts[0]
    for p in parts[1:]:
        result = result + p  # disjoint solids, one STL
    return result


def warn_layer_multiple(heights):
    for h in heights:
        layers = h / LAYER_HEIGHT
        if abs(layers - round(layers)) > 1e-6:
            lo, hi = math.floor(layers) * LAYER_HEIGHT, math.ceil(layers) * LAYER_HEIGHT
            print(
                f"  warning: {fmt(h)} mm is not a multiple of the {LAYER_HEIGHT} mm layer height; "
                f"at that layer height it prints as {fmt(round(lo, 3))} or {fmt(round(hi, 3))} mm"
            )


class HelpFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    """Keep the docstring's layout and show each option's default."""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=HelpFormatter)
    parser.add_argument("height", type=float, nargs="?", help="block height in mm (the spacing it sets)")
    parser.add_argument("--set", help="comma-separated heights for a matched set, e.g. 5,10,15,20")
    parser.add_argument("--width", type=float, default=50.0)
    parser.add_argument("--depth", type=float, default=30.0)
    parser.add_argument("-o", "--output")
    add_bed_arg(parser)
    args = parser.parse_args()

    if args.set:
        heights = [float(h) for h in args.set.split(",")]
        output = args.output or "spacer_set_" + "-".join(fmt(h) for h in sorted(heights)) + "mm.stl"
        print(f"Spacing block set: {', '.join(fmt(h) for h in sorted(heights))} mm")
        part = spacing_set(heights, args.width, args.depth, args.bed[0])
    elif args.height:
        heights = [args.height]
        output = args.output or f"spacer_{fmt(args.height)}mm.stl"
        print(f"Spacing block: {fmt(args.width)} x {fmt(args.depth)} x {fmt(args.height)} mm")
        part = spacing_block(args.height, args.width, args.depth)
    else:
        parser.error("give a height, or --set h1,h2,...")

    warn_layer_multiple(heights)
    export_checked(part, output, args.bed)


if __name__ == "__main__":
    main()
