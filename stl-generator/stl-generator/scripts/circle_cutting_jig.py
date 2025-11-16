#!/usr/bin/env python3
"""
Generate a circle cutting jig for router or trim tools.
Perfect for creating lampshade rings and circular frames.
"""

import cadquery as cq
import sys


def create_circle_jig(
    outer_diameter: float,
    inner_diameter: float,
    thickness: float = 10.0,
    guide_width: float = 20.0,
    guide_height: float = 8.0,
    slot_width: float = 8.0,
    center_hole_diameter: float = 8.0,
):
    """
    Create a circle cutting jig.
    
    Args:
        outer_diameter: Outer diameter of the circle to cut (mm)
        inner_diameter: Inner diameter of the circle to cut (mm)
        thickness: Base plate thickness (mm)
        guide_width: Width of the guide ring (mm)
        guide_height: Height of guide walls (mm)
        slot_width: Width of router bit slot (mm)
        center_hole_diameter: Diameter of center pivot hole (mm)
    """
    # Create base plate
    base = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2 + guide_width)
        .extrude(thickness)
    )
    
    # Cut out inner circle
    base = base.faces(">Z").circle(inner_diameter / 2).cutThruAll()
    
    # Cut center pivot hole
    base = base.faces(">Z").workplane().circle(center_hole_diameter / 2).cutThruAll()
    
    # Create guide ring on top
    guide = (
        cq.Workplane("XY")
        .workplane(offset=thickness)
        .circle(outer_diameter / 2 + guide_width)
        .circle(outer_diameter / 2)
        .extrude(guide_height)
    )
    
    # Add alignment marks every 45 degrees
    for angle in range(0, 360, 45):
        mark = (
            cq.Workplane("XY")
            .workplane(offset=thickness)
            .transformed(rotate=(0, 0, angle))
            .center(outer_diameter / 2 + guide_width / 2, 0)
            .rect(2, guide_width)
            .extrude(guide_height + 1)
        )
        guide = guide.cut(mark)
    
    # Add router bit slot (radial)
    slot = (
        cq.Workplane("XY")
        .workplane(offset=thickness)
        .center(0, 0)
        .rect((outer_diameter / 2 + guide_width), slot_width)
        .extrude(guide_height + thickness + 1)
    )
    
    result = base.union(guide).cut(slot)
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: circle_cutting_jig.py <outer_diameter_mm> <inner_diameter_mm> [output.stl]")
        print("Example: circle_cutting_jig.py 300 250 lampshade_jig.stl")
        sys.exit(1)
    
    outer_d = float(sys.argv[1])
    inner_d = float(sys.argv[2])
    output = sys.argv[3] if len(sys.argv) > 3 else "circle_jig.stl"
    
    print(f"Generating circle cutting jig: OD={outer_d}mm, ID={inner_d}mm")
    
    jig = create_circle_jig(outer_diameter=outer_d, inner_diameter=inner_d)
    
    # Export to STL
    cq.exporters.export(jig, output)
    print(f"✓ STL saved to: {output}")
