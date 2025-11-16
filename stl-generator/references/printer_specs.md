# Elegoo Neptune 4 Pro - Printer Specifications

## Build Volume
- **X-axis**: 225 mm
- **Y-axis**: 225 mm  
- **Z-axis**: 265 mm
- **Effective print area**: ~220 x 220 x 260 mm (accounting for margins)

## Print Settings
- **Layer height**: 0.2 mm (standard)
- **Nozzle diameter**: 0.4 mm (standard)
- **Minimum wall thickness**: 0.8 mm (2 perimeters)
- **Maximum overhang angle**: 45° without supports
- **Bridging capability**: ~30 mm for PLA

## Material Properties (PLA)
- **Typical use case**: Functional jigs and fixtures
- **Layer adhesion**: Good at 0.2mm layers
- **Dimensional accuracy**: ±0.2 mm
- **Heat resistance**: Up to ~60°C
- **Recommended wall count**: 3-4 for structural parts

## Design Constraints for Woodworking Jigs

### General Guidelines
1. **Minimum feature size**: 1.0 mm (2.5x nozzle diameter)
2. **Hole diameters**: Add 0.3-0.5 mm clearance for hardware
3. **Text depth**: 0.4-0.6 mm for embossed text
4. **Fillet radius**: Minimum 1.0 mm for internal corners
5. **Wall thickness**: 2.0-3.0 mm minimum for structural integrity

### Functional Tolerances
- **Tight fit**: -0.1 to 0.0 mm (for press-fit parts)
- **Slide fit**: +0.1 to +0.2 mm (for moving parts)
- **Loose fit**: +0.3 to +0.5 mm (for assembly clearance)

### Specific to Woodworking Jigs
1. **Base stability**: Minimum 5mm thickness for flat reference surfaces
2. **Router bit clearance**: 10-12mm slots for standard 1/4" and 1/2" bits
3. **Clamp access**: 25mm+ clearance for standard clamps
4. **Screw holes**: 
   - M3: 3.3 mm hole
   - M4: 4.3 mm hole  
   - M5: 5.3 mm hole
   - #8 wood screw: 4.5 mm hole
5. **Material contact surfaces**: Smooth finish, avoid text/features that mar wood

### Print Orientation Recommendations
- **Maximum strength**: Layer lines perpendicular to load direction
- **Best surface finish**: Print face-down on bed
- **Overhangs**: Orient to minimize supports (keep < 45° angle)
- **Functional surfaces**: Print against bed for best flatness

### Support Requirements
- **Angles > 45°**: Require supports
- **Bridging**: Keep spans < 30 mm
- **Support gap**: 0.2 mm for easy removal
- **Avoid supports on**: Functional reference surfaces

## Common Hardware Sizes (for reference holes)

### Metric Hardware
- M3 x 0.5: 3.3 mm clearance hole
- M4 x 0.7: 4.3 mm clearance hole
- M5 x 0.8: 5.3 mm clearance hole
- M6 x 1.0: 6.4 mm clearance hole

### Imperial Hardware  
- #6 wood screw: 3.7 mm clearance hole
- #8 wood screw: 4.5 mm clearance hole
- #10 wood screw: 5.1 mm clearance hole
- 1/4"-20: 6.6 mm clearance hole

### Router Bits (for slot sizing)
- 1/4" shank: 6.35 mm (use 7-8 mm slots)
- 1/2" shank: 12.7 mm (use 13-14 mm slots)
- Template guides: Typically 5/8" (16mm) OD

## Material Usage Estimation
- **PLA density**: ~1.24 g/cm³
- **Typical infill**: 20% for jigs (good strength/material balance)
- **Wall lines**: 3-4 perimeters
- **Top/bottom layers**: 4-5 layers (0.8-1.0 mm)

## Print Time Estimation (rough guidelines)
- Small jig (50x50x10mm): ~1-2 hours
- Medium jig (100x100x20mm): ~4-6 hours
- Large jig (200x200x30mm): ~12-18 hours

*These are estimates; actual time depends on geometry complexity and print settings.*
