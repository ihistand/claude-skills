# STL Generator Skill - Installation Guide

## What You Got

A complete Claude Code skill for generating 3D printable woodworking jigs optimized for your Elegoo Neptune 4 Pro.

## Installation

1. **Download the skill file**: `stl-generator.skill`
2. **In Claude Code**, import the skill:
   - Click the skills icon in the sidebar
   - Select "Import Skill"
   - Choose `stl-generator.skill`

## What It Does

Generates STL files for woodworking jigs using CadQuery (Python-based parametric CAD). Optimized for your printer specs:
- **Elegoo Neptune 4 Pro**: 225×225×265mm build volume
- **Layer height**: 0.2mm
- **All measurements**: Metric (millimeters)

## Pre-Built Jigs

### 1. Circle Cutting Jig
Perfect for lampshade rings and circular frames.

**Example prompt**:
> "Create a circle cutting jig for a 300mm diameter lampshade with 280mm inner diameter"

### 2. Angle Wedges
For compound cuts and angled assembly.

**Example prompt**:
> "Make a 15 degree angle wedge for my lampshade angle"

### 3. Spacing Blocks
Precision spacers for consistent gaps.

**Example prompt**:
> "Generate a set of spacing blocks in 5mm, 10mm, 15mm, and 20mm heights"

## Custom Jigs

The skill can create any custom jig you describe. Just explain what you need:

**Example prompts**:
> "Create a router template for cutting a rectangular mortise 100mm × 30mm"

> "Make an alignment jig with pins for gluing up lampshade ribs"

> "Design a clamping caul with finger reliefs for a 200mm wide panel"

## Quick Test

Try this prompt:
> "Create a 10mm spacing block"

Claude will generate the STL and provide a download link.

## Design Constraints (Built-In)

The skill knows these limitations:
- Min wall thickness: 2-3mm
- Min feature size: 1.0mm
- Hardware clearances: +0.3-0.5mm
- Max build: 220×220mm effective print area

## What's Included

- **3 pre-built scripts**: Circle jig, angle wedge, spacing blocks
- **Printer specifications**: Your Neptune 4 Pro settings
- **CadQuery patterns**: Common woodworking jig designs
- **Design guidelines**: Print-optimized best practices

## Example Output

Included `lampshade_example_300mm.stl` - a 300mm OD circle cutting jig demonstration.

Import this into OrcaSlicer to see the quality of output!

## Recommended Print Settings

- **Layer height**: 0.2mm
- **Infill**: 20% (good strength/speed balance for jigs)
- **Perimeters**: 3-4 walls
- **Top/bottom**: 4-5 layers
- **Material**: PLA (adequate for woodworking jigs)

## Tips

1. **Be specific**: Include dimensions in your prompts
2. **Describe the purpose**: Helps Claude optimize the design
3. **Mention constraints**: "Must fit a 1/2 inch router bit" or "needs M5 bolt holes"
4. **Ask for modifications**: "Make it 5mm taller" or "add finger reliefs"

## Troubleshooting

**"Module 'cadquery' not found"**
- Claude will install it automatically when needed

**Part too large for bed**
- Mention the size constraint: "Must fit on a 220mm print bed"
- Claude can split designs or suggest alternatives

**Need supports**
- Ask: "Can you orient this to minimize supports?"

## Advanced Usage

Once comfortable with pre-built jigs, you can request completely custom designs:

> "Create a tapered lampshade assembly jig that holds 12 ribs at 30-degree angles around a 250mm base circle, with 3mm spacing slots and alignment pins"

The skill will write custom CadQuery code to generate exactly what you need.

## Questions?

Just ask Claude! The skill includes comprehensive documentation on:
- CadQuery programming patterns
- Woodworking jig best practices
- Print optimization strategies
- Hardware integration standards

Enjoy your new jig-making capability! 🛠️
