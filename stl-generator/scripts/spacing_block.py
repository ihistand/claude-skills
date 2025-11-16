#!/usr/bin/env python3
"""
Generate precision spacing blocks for assembly and alignment.
Perfect for consistent spacing in lampshade frames and joinery setup.
"""

import cadquery as cq
import sys


def create_spacing_block(
    width: float,
    depth: float,
    height: float,
    add_finger_relief: bool = True,
    add_label: bool = True,
):
    """
    Create a spacing/setup block.
    
    Args:
        width: Block width (mm)
        depth: Block depth (mm)  
        height: Block height/thickness (mm)
        add_finger_relief: Add cutouts for easy pickup
        add_label: Emboss dimensions on top
    """
    # Create main block
    block = cq.Workplane("XY").box(width, depth, height)
    
    if add_finger_relief:
        # Add semicircular cutouts on opposite sides for grip
        relief_diameter = min(height * 1.2, 20)
        
        for side in [-1, 1]:
            relief = (
                cq.Workplane("YZ")
                .workplane(offset=side * width / 2)
                .center(0, -height / 2)
                .circle(relief_diameter / 2)
                .extrude(10)
            )
            block = block.cut(relief)
    
    if add_label:
        # Emboss dimension label on top surface
        label_text = f"{height}mm"
        try:
            block = (
                block.faces(">Z")
                .workplane()
                .text(
                    label_text,
                    fontsize=min(6, height / 2),
                    distance=-0.5,
                    halign="center",
                    valign="center",
                )
            )
        except:
            pass  # Text might fail in some CadQuery versions
    
    # Add orientation marker (small notch on one corner)
    marker = (
        cq.Workplane("XY")
        .workplane(offset=height / 2)
        .center(-width / 2 + 3, -depth / 2 + 3)
        .rect(3, 3)
        .extrude(2)
    )
    block = block.cut(marker)
    
    return block


def create_spacing_set(heights: list, width: float = 50.0, depth: float = 30.0):
    """
    Create a set of spacing blocks with different heights.
    Arranged in a row for printing.
    
    Args:
        heights: List of heights in mm
        width: Block width (mm)
        depth: Block depth (mm)
    """
    spacing = 5  # Gap between blocks
    result = None
    x_offset = 0
    
    for height in sorted(heights):
        block = create_spacing_block(width, depth, height)
        block = block.translate((x_offset, 0, 0))
        
        if result is None:
            result = block
        else:
            result = result.union(block)
        
        x_offset += width + spacing
    
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: spacing_block.py <height_mm> [width_mm] [depth_mm] [output.stl]")
        print("   Or: spacing_block.py set <h1>,<h2>,<h3>... [output.stl]")
        print()
        print("Examples:")
        print("  spacing_block.py 10 50 30 spacer_10mm.stl")
        print("  spacing_block.py set 5,10,15,20 spacer_set.stl")
        sys.exit(1)
    
    if sys.argv[1].lower() == "set":
        # Create a set of blocks
        if len(sys.argv) < 3:
            print("Error: Must specify heights after 'set'")
            sys.exit(1)
        
        heights = [float(h) for h in sys.argv[2].split(",")]
        output = sys.argv[3] if len(sys.argv) > 3 else "spacing_set.stl"
        
        print(f"Generating spacing block set: {heights} mm")
        result = create_spacing_set(heights)
    else:
        # Create single block
        height = float(sys.argv[1])
        width = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
        depth = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
        output = sys.argv[4] if len(sys.argv) > 4 else f"spacer_{int(height)}mm.stl"
        
        print(f"Generating spacing block: {width}x{depth}x{height} mm")
        result = create_spacing_block(width, depth, height)
    
    # Export to STL
    cq.exporters.export(result, output)
    print(f"✓ STL saved to: {output}")
