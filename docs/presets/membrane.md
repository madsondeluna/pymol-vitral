## Membrane presets

Ten presets, rendered below from `memb/bilbo_preview.pdb`: a mixed bilayer of
six lipid species plus cardiolipin, 64k atoms, written with a zero B column,
which is what a molecular dynamics frame looks like. The `paper` argument works
the same way here.

```
load memb/bilbo_preview.pdb
run /path/to/pymol-molviz/molviz.pml
```

### `preset_memb1` stratified spheres

General reading, layer organization.

```
preset_memb1
```

| Element | Representation |
|---|---|
| Lipid | spheres, scale 0.55, heads at 0.66 |
| Colour | one per chemical moiety: head, phosphate, glycerol, tail |
| Ions | opaque spheres, scale 0.5 |
| Water | molecular surface at transparency 0.62 |

The gap between spheres is what preserves the distinction between the four layers, which a full spacefill erases.

| Side | Top |
|---|---|
| ![Side](../img/memb1_lado.png) | ![Top](../img/memb1_cima.png) |

### `preset_memb2` solid spacefill

Occupied volume, the barrier.

```
preset_memb2
```

| Element | Representation |
|---|---|
| Lipid | spheres at van der Waals radius, scale 1.0 |
| Colour | one per leaflet |
| Ions | spheres at real radius, consistent with the lipid |
| Water | molecular surface at transparency 0.78 |

Shows occupied volume and packing. Internal organization disappears by construction: what you see is the barrier.

| Side | Top |
|---|---|
| ![Side](../img/memb2_lado.png) | ![Top](../img/memb2_cima.png) |

### `preset_memb3` licorice with highlighted ions

Ion to polar head interaction.

```
preset_memb3
```

| Element | Representation |
|---|---|
| Lipid | sticks, radius 0.30, heads as spheres at 0.45 |
| Colour | one per chemical moiety |
| Ions | opaque core with a translucent shell at 0.72, suggesting solvation |
| Water | translucent spheres, scale 0.35 |

Licorice lets the tail conformation show, which spacefill hides.

| Side | Top |
|---|---|
| ![Side](../img/memb3_lado.png) | ![Top](../img/memb3_cima.png) |

### `preset_memb4` ghost bilayer

Inserted peptide.

```
preset_memb4
```

| Element | Representation |
|---|---|
| Lipid | molecular surface at transparency 0.58 over thin sticks, radius 0.16 |
| Colour | one per chemical moiety |
| Ions | spheres with an inflated mesh, radius 3.0 |
| Water | off, deliberately |
| Protein | shown if present |

Preserves the membrane outline without hiding what is inside it. The water is off on purpose: the solvent surface would cover the object of interest.

| Side | Top |
|---|---|
| ![Side](../img/memb4_lado.png) | ![Top](../img/memb4_cima.png) |

### `preset_memb5` continuous hydrophobic core

Illustration, large systems.

```
preset_memb5
```

| Element | Representation |
|---|---|
| Lipid | tails as a single gaussian isosurface, heads and phosphates as spheres at 0.75 |
| Colour | tail orange, head green, phosphate amber |
| Ions | opaque spheres, scale 0.85 |
| Water | continuous gaussian field |

Replaces thousands of tail atoms with one smooth surface. Lightest preset for large systems and the closest to scientific illustration. The isolevel comes from the map histogram, not a fixed value, and it falls back to thin sticks if the map comes out empty.

| Side | Top |
|---|---|
| ![Side](../img/memb5_lado.png) | ![Top](../img/memb5_cima.png) |

### `preset_memb6` fast navigation

Not a figure.

```
preset_memb6
```

| Element | Representation |
|---|---|
| Lipid | lines, width 1.2 |
| Colour | one per lipid species |
| Ions | dots |
| Water | off |
| Ambient occlusion | off |

Exists because ray tracing and ambient occlusion make rotation unusable on a large system. Frame the scene here, then apply an expensive preset.

| Side | Top |
|---|---|
| ![Side](../img/memb6_lado.png) | ![Top](../img/memb6_cima.png) |

### `preset_memb7` cross-section

The bilayer interior.

```
preset_memb7
```

| Element | Representation |
|---|---|
| Lipid | central slab in spacefill, scale 1.0 |
| Colour | one per chemical moiety, exposed on the cut face |
| Ions | spheres within 8 A of the slab |
| Water | off |
| Camera | along the cut axis |

The cut is a coordinate selection, not the camera clipping plane, so rotating afterwards does not change what is exposed. Takes the axis: `preset_memb7 0` for x, `1` for y, `2` for z.

| Side | Top |
|---|---|
| ![Side](../img/memb7_lado.png) | ![Top](../img/memb7_cima.png) |

### `preset_memb8` annular lipids

Protein to lipid contact.

```
preset_memb8
```

| Element | Representation |
|---|---|
| Lipid in contact | licorice, radius 0.24, opaque |
| Rest of the bilayer | sticks, radius 0.10, transparency 0.72 |
| Colour | contacts by moiety, the rest neutral grey |
| Ions | small spheres, scale 0.4 |
| Water | off |

Answers which lipids touch the protein. Needs a protein in the session, and takes the contact radius: `preset_memb8 7.0`.

| Side | Top |
|---|---|
| ![Side](../img/memb8_lado.png) | ![Top](../img/memb8_cima.png) |

### `preset_memb9` separated leaflets

Leaflet asymmetry and thickness.

```
preset_memb9
```

| Element | Representation |
|---|---|
| Upper leaflet | molecular surface at transparency 0.45 |
| Lower leaflet | molecular surface, second colour |
| Phosphates | spheres, scale 0.55, marking both planes |
| Ions | spheres, scale 0.5 |
| Water | off |

The two surfaces let the separation between the phosphate planes be read by eye, and a composition difference between leaflets shows up as a volume difference. The midplane comes from the mean z of the phosphates.

| Side | Top |
|---|---|
| ![Side](../img/memb9_lado.png) | ![Top](../img/memb9_cima.png) |

### `preset_memb10` two colours, for print

Reduction to one column, black and white.

```
preset_memb10
```

| Element | Representation |
|---|---|
| Lipid tails | gaussian isosurface, dark |
| Heads and phosphates | spheres, scale 0.8, light |
| Ions | off |
| Water | off |

Two colours only, separated by lightness rather than hue, and nothing secondary competing for attention. Everything that is not the bilayer leaves the scene.

| Side | Top |
|---|---|
| ![Side](../img/memb10_lado.png) | ![Top](../img/memb10_cima.png) |

