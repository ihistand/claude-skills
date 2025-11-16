#!/usr/bin/env python3
"""
Generate angle guide wedges for compound cuts and assembly jigs.
Useful for lampshade frames and angled joinery.
"""

import cadquery as cq
import sys
import math


def create_angle_wedge(
    angle_degrees: float,
    width: float = 80.0,
    depth: float = 60.0,
    height: float = 30.0,
    add_reference_edge: bool = True,
):
    """
    Create an angle guide wedge.
    
    Args:
        angle_degrees: Angle of the wedge (degrees from horizontal)
        width: Width of the wedge base (mm)
        depth: Depth of the wedge (mm)
        height: Maximum height of the wedge (mm)
        add_reference_edge: Add a raised reference edge
    """
    angle_rad = math.radians(angle_degrees)
    
    # Calculate the wedge profile
    wedge_height = min(depth * math.tan(angle_rad), height)
    
    # Create wedge body using loft
    base = cq.Workplane("XY").rect(width, depth)
    
    # Create top profile (angled)
    top = (
        cq.Workplane("XY")
        .workplane(offset=wedge_height)
        .center(0, -depth / 2 + depth)
        .rect(width, 0.1)
    )
    
    # Create the wedge using a simple extrude with taper
    wedge = (
        cq.Workplane("XY")
        .rect(width, depth)
        .extrude(wedge_height, taper=-angle_degrees)
    )
    
    # Alternative: Create wedge as a solid using points
    points = [
        (-width / 2, -depth / 2, 0),
        (width / 2, -depth / 2, 0),
        (width / 2, depth / 2, 0),
        (-width / 2, depth / 2, 0),
        (-width / 2, -depth / 2, wedge_height),
        (width / 2, -depth / 2, wedge_height),
        (width / 2, depth / 2, 0),
        (-width / 2, depth / 2, 0),
    ]
    
    # Simpler approach: Create wedge profile and extrude
    wedge = (
        cq.Workplane("XZ")
        .moveTo(-depth / 2, 0)
        .lineTo(depth / 2, 0)
        .lineTo(depth / 2, wedge_height)
        .lineTo(-depth / 2, 0)
        .close()
        .extrude(width)
        .translate((0, 0, -width / 2))
        .rotate((0, 0, 0), (0, 0, 1), 90)
    )
    
    if add_reference_edge:
        # Add raised reference edge along hypotenuse
        edge_thickness = 3
        edge_height = 5
        
        # Calculate edge position along the sloped surface
        edge = (
            cq.Workplane("XY")
            .center(0, 0)
            .rect(edge_thickness, depth)
            .extrude(edge_height)
            .translate((0, 0, wedge_height / 2))
            .rotate((0, -depth / 2, wedge_height / 2), (0, depth / 2, 0), -angle_degrees)
        )
        
        wedge = wedge.union(edge)
    
    # Add text label with angle
    try:
        wedge = (
            wedge.faces(">Z")
            .workplane()
            .text(
                f"{angle_degrees}°",
                fontsize=8,
                distance=-1,
                halign="center",
                valign="center",
            )
        )
    except:
        pass  # Text might fail in some CadQuery versions
    
    return wedge


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: angle_wedge.py <angle_degrees> [output.stl]")
        print("Example: angle_wedge.py 15 wedge_15deg.stl")
        sys.exit(1)
    
    angle = float(sys.argv[1])
    output = sys.argv[2] if len(sys.argv) > 2 else f"wedge_{int(angle)}deg.stl"
    
    print(f"Generating {angle}° angle wedge")
    
    wedge = create_angle_wedge(angle_degrees=angle)
    
    # Export to STL
    cq.exporters.export(wedge, output)
    print(f"✓ STL saved to: {output}")
