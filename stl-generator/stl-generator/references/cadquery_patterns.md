# CadQuery Reference for STL Generation

## Core Concepts

### Workplane-Based Modeling
CadQuery uses a fluent API with method chaining. Start with a workplane, build 2D sketches, then extrude to 3D.

```python
import cadquery as cq

# Basic box
box = cq.Workplane("XY").box(10, 20, 30)

# Sketch then extrude
part = (
    cq.Workplane("XY")
    .rect(50, 50)
    .extrude(10)
)
```

### Coordinate Systems
- **XY plane**: Standard horizontal plane (default for most operations)
- **XZ plane**: Vertical plane (front view)
- **YZ plane**: Vertical plane (side view)

## Common Patterns for Jigs

### Pattern 1: Base Plate with Holes

```python
def create_base_with_holes(width, depth, thickness, hole_positions):
    """
    Create a rectangular base plate with mounting holes.
    
    Args:
        width, depth, thickness: Dimensions in mm
        hole_positions: List of (x, y, diameter) tuples
    """
    base = cq.Workplane("XY").box(width, depth, thickness)
    
    # Add holes
    for x, y, dia in hole_positions:
        base = (
            base.faces(">Z")
            .workplane()
            .center(x, y)
            .circle(dia / 2)
            .cutThruAll()
        )
    
    return base
```

### Pattern 2: Raised Guide Walls

```python
def add_guide_walls(base, wall_thickness, wall_height):
    """
    Add perimeter walls to a base for guiding workpieces.
    """
    # Get base dimensions
    bb = base.val().BoundingBox()
    width = bb.xlen
    depth = bb.ylen
    base_height = bb.zlen
    
    walls = (
        cq.Workplane("XY")
        .workplane(offset=base_height)
        .rect(width + 2 * wall_thickness, depth + 2 * wall_thickness)
        .rect(width, depth)
        .extrude(wall_height)
    )
    
    return base.union(walls)
```

### Pattern 3: Angled Slots for Bits/Blades

```python
def add_tool_slot(part, slot_width, slot_depth, angle_degrees=0):
    """
    Add a slot for router bit or saw blade clearance.
    
    Args:
        part: Base CadQuery object
        slot_width: Width of slot (mm)
        slot_depth: How deep to cut (mm)
        angle_degrees: Angle from horizontal (for beveled slots)
    """
    bb = part.val().BoundingBox()
    base_height = bb.zlen
    
    slot = (
        cq.Workplane("XY")
        .workplane(offset=base_height / 2)
        .rect(bb.xlen + 10, slot_width)
        .extrude(slot_depth)
    )
    
    if angle_degrees != 0:
        slot = slot.rotate((0, 0, 0), (1, 0, 0), angle_degrees)
    
    return part.cut(slot)
```

### Pattern 4: Alignment Pins/Locators

```python
def add_alignment_pins(base, positions, pin_diameter=6, pin_height=10):
    """
    Add cylindrical alignment pins at specified positions.
    
    Args:
        base: Base part
        positions: List of (x, y) tuples for pin centers
        pin_diameter: Diameter of pins (mm)
        pin_height: Height of pins above base (mm)
    """
    bb = base.val().BoundingBox()
    base_height = bb.zlen
    
    for x, y in positions:
        pin = (
            cq.Workplane("XY")
            .workplane(offset=base_height)
            .center(x, y)
            .circle(pin_diameter / 2)
            .extrude(pin_height)
        )
        base = base.union(pin)
    
    return base
```

### Pattern 5: Chamfers and Fillets

```python
# Add chamfer to all edges
part = part.edges().chamfer(1.0)

# Add fillet to specific edges (top edges only)
part = part.edges("|Z").fillet(2.0)

# Fillet selection by position
part = part.edges(">Z").fillet(2.0)  # Edges on top face
```

## Selection Techniques

### Face Selection
```python
.faces(">Z")    # Top face (highest Z)
.faces("<Z")    # Bottom face (lowest Z)
.faces(">X")    # Right face
.faces("<X")    # Left face
.faces("|Z")    # All faces parallel to Z axis (vertical faces)
```

### Edge Selection
```python
.edges("|Z")    # Vertical edges
.edges("|X")    # Edges parallel to X
.edges(">Z")    # Edges on top face
```

## Boolean Operations

```python
# Union (combine)
result = part1.union(part2)

# Cut (subtract)
result = part1.cut(part2)

# Intersection
result = part1.intersect(part2)
```

## Transformations

```python
# Translate
part = part.translate((10, 20, 5))

# Rotate (center point, axis vector, angle in degrees)
part = part.rotate((0, 0, 0), (0, 0, 1), 45)

# Mirror
part = part.mirror("XY")
```

## Arrays and Patterns

### Linear Pattern
```python
# Create 5 copies spaced 20mm apart in X
for i in range(5):
    copy = part.translate((i * 20, 0, 0))
    if i == 0:
        result = copy
    else:
        result = result.union(copy)
```

### Circular Pattern
```python
import math

def circular_pattern(part, count, radius):
    """Create circular pattern of parts."""
    result = None
    for i in range(count):
        angle = (360 / count) * i
        x = radius * math.cos(math.radians(angle))
        y = radius * math.sin(math.radians(angle))
        
        copy = part.translate((x, y, 0))
        
        if result is None:
            result = copy
        else:
            result = result.union(copy)
    
    return result
```

## Text and Labels

```python
# Embossed text (raised)
part = (
    part.faces(">Z")
    .workplane()
    .text("LABEL", fontsize=10, distance=1)
)

# Debossed text (recessed)
part = (
    part.faces(">Z")
    .workplane()
    .text("LABEL", fontsize=10, distance=-1)
)
```

## Common Mistakes to Avoid

1. **Forgetting workplane offset**: When adding features to top of part, offset workplane
   ```python
   # Wrong
   .workplane().circle(5)  # Starts at Z=0
   
   # Right  
   .faces(">Z").workplane().circle(5)  # Starts at top face
   ```

2. **Wrong boolean order**: Order matters for cuts
   ```python
   # Creates hole
   base.faces(">Z").circle(5).cutThruAll()
   
   # Doesn't work (no face selected yet)
   base.circle(5).cutThruAll()
   ```

3. **Lost reference**: Need to chain or reassign
   ```python
   # Wrong (original 'part' unchanged)
   part.faces(">Z").circle(5).cutThruAll()
   
   # Right
   part = part.faces(">Z").circle(5).cutThruAll()
   ```

## Export Options

```python
import cadquery as cq

# Export to STL (for 3D printing)
cq.exporters.export(part, "output.stl")

# Export to STEP (for CAD interchange)
cq.exporters.export(part, "output.step")

# Export to DXF (2D drawings)
cq.exporters.export(part, "output.dxf")
```

## Woodworking Jig Specific Tips

1. **Add draft angles for easier removal**: Use `.extrude(height, taper=2)` for parts that nest
2. **Clearance holes**: Always add 0.3-0.5mm to hardware diameter
3. **Reference edges**: Raised by 3-5mm for easy visual alignment
4. **Finger reliefs**: Semicircular cutouts for picking up spacers
5. **Orientation marks**: Small notch or chamfer to indicate "front"
6. **Material-friendly features**: Avoid sharp internal corners that might mark wood
