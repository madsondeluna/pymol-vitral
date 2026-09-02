# Gallery

Every preset in three orientations, rendered by `tests/make_gallery.py`.
The command under each one is what produces that scene: paste it into the
PyMOL command line after loading the system and the protocol.

## Protein presets

Rendered from `prot/4hhb.pdb` with the command shown under each row.

```
load prot/4hhb.pdb
run /path/to/pymol-molviz/molviz.pml
```

### `preset_prot1`

Domain topology. Cartoon by secondary structure: helix blue, sheet red, loop white.

```
preset_prot1
```

| side | top | corner |
|---|---|---|
| ![preset_prot1 lado](img/prot1_lado.png) | ![preset_prot1 cima](img/prot1_cima.png) | ![preset_prot1 quina](img/prot1_quina.png) |

### `preset_prot2`

Binding site. Same cartoon under a translucent surface, so a ligand stays visible inside.

```
preset_prot2
```

| side | top | corner |
|---|---|---|
| ![preset_prot2 lado](img/prot2_lado.png) | ![preset_prot2 cima](img/prot2_cima.png) | ![preset_prot2 quina](img/prot2_quina.png) |

### `preset_prot3`

Interaction face. Solid surface with a Kyte-Doolittle gradient. Writes to the B column; `prot_restore_b` undoes it.

```
preset_prot3
```

| side | top | corner |
|---|---|---|
| ![preset_prot3 lado](img/prot3_lado.png) | ![preset_prot3 cima](img/prot3_cima.png) | ![preset_prot3 quina](img/prot3_quina.png) |

### `preset_prot4`

Complex architecture. Spacefill at van der Waals radius, one colour per chain.

```
preset_prot4
```

| side | top | corner |
|---|---|---|
| ![preset_prot4 lado](img/prot4_lado.png) | ![preset_prot4 cima](img/prot4_cima.png) | ![preset_prot4 quina](img/prot4_quina.png) |

### `preset_prot5`

Flexibility. Putty: thickness encodes the B-factor. Inverts on predicted models carrying pLDDT.

```
preset_prot5
```

| side | top | corner |
|---|---|---|
| ![preset_prot5 lado](img/prot5_lado.png) | ![preset_prot5 cima](img/prot5_cima.png) | ![preset_prot5 quina](img/prot5_quina.png) |

### `preset_prot6`

Peptides. All-atom licorice coloured by formal charge. Above 60 residues it warns and stays illegible.

```
preset_prot6
```

| side | top | corner |
|---|---|---|
| ![preset_prot6 lado](img/prot6_lado.png) | ![preset_prot6 cima](img/prot6_cima.png) | ![preset_prot6 quina](img/prot6_quina.png) |

### `preset_prot7`

MD box. Cartoon plus water within 4 A and ions within 6 A; bulk solvent discarded.

```
preset_prot7
```

| side | top | corner |
|---|---|---|
| ![preset_prot7 lado](img/prot7_lado.png) | ![preset_prot7 cima](img/prot7_cima.png) | ![preset_prot7 quina](img/prot7_quina.png) |

### `preset_prot8`

The simulated system as a whole. Surface inside the solvent volume.

```
preset_prot8
```

| side | top | corner |
|---|---|---|
| ![preset_prot8 lado](img/prot8_lado.png) | ![preset_prot8 cima](img/prot8_cima.png) | ![preset_prot8 quina](img/prot8_quina.png) |

### `preset_prot9`

Box dimensions. Surface, solvent field and the twelve box edges, measured into the log.

```
preset_prot9
```

| side | top | corner |
|---|---|---|
| ![preset_prot9 lado](img/prot9_lado.png) | ![preset_prot9 cima](img/prot9_cima.png) | ![preset_prot9 quina](img/prot9_quina.png) |

### `preset_prot10`

Interface. Translucent cartoon with the contact side chains in opaque licorice, on the chain pair with the largest contact.

```
preset_prot10
```

| side | top | corner |
|---|---|---|
| ![preset_prot10 lado](img/prot10_lado.png) | ![preset_prot10 cima](img/prot10_cima.png) | ![preset_prot10 quina](img/prot10_quina.png) |

## Membrane presets

Rendered from `memb/bilbo_preview.pdb` with the command shown under each row.

```
load memb/bilbo_preview.pdb
run /path/to/pymol-molviz/molviz.pml
```

### `preset_memb1`

General reading. Spheres at scale 0.55, one colour per chemical moiety, water as a translucent surface.

```
preset_memb1
```

| side | top | corner |
|---|---|---|
| ![preset_memb1 lado](img/memb1_lado.png) | ![preset_memb1 cima](img/memb1_cima.png) | ![preset_memb1 quina](img/memb1_quina.png) |

### `preset_memb2`

Occupied volume. Spacefill at van der Waals radius, coloured by leaflet.

```
preset_memb2
```

| side | top | corner |
|---|---|---|
| ![preset_memb2 lado](img/memb2_lado.png) | ![preset_memb2 cima](img/memb2_cima.png) | ![preset_memb2 quina](img/memb2_quina.png) |

### `preset_memb3`

Ion to polar head. Licorice with heads as spheres; ions get an opaque core and a solvation shell.

```
preset_memb3
```

| side | top | corner |
|---|---|---|
| ![preset_memb3 lado](img/memb3_lado.png) | ![preset_memb3 cima](img/memb3_cima.png) | ![preset_memb3 quina](img/memb3_quina.png) |

### `preset_memb4`

Inserted peptide. Translucent surface over thin sticks, water off so it does not cover the target.

```
preset_memb4
```

| side | top | corner |
|---|---|---|
| ![preset_memb4 lado](img/memb4_lado.png) | ![preset_memb4 cima](img/memb4_cima.png) | ![preset_memb4 quina](img/memb4_quina.png) |

### `preset_memb5`

Illustration and large systems. Tails as a single gaussian isosurface, heads as spheres.

```
preset_memb5
```

| side | top | corner |
|---|---|---|
| ![preset_memb5 lado](img/memb5_lado.png) | ![preset_memb5 cima](img/memb5_cima.png) | ![preset_memb5 quina](img/memb5_quina.png) |

### `preset_memb6`

Navigation, not a figure. Lines and dots, ambient occlusion off.

```
preset_memb6
```

| side | top | corner |
|---|---|---|
| ![preset_memb6 lado](img/memb6_lado.png) | ![preset_memb6 cima](img/memb6_cima.png) | ![preset_memb6 quina](img/memb6_quina.png) |

### `preset_memb7`

Cross-section. A central slab in spacefill, with the camera along the cut axis. Takes `eixo`: 0 for x, 1 for y, 2 for z.

```
preset_memb7
```

| side | top | corner |
|---|---|---|
| ![preset_memb7 lado](img/memb7_lado.png) | ![preset_memb7 cima](img/memb7_cima.png) | ![preset_memb7 quina](img/memb7_quina.png) |

### `preset_memb8`

Annular lipids. The ones touching the protein in licorice, the rest ghosted. Needs a protein in the session.

```
preset_memb8
```

| side | top | corner |
|---|---|---|
| ![preset_memb8 lado](img/memb8_lado.png) | ![preset_memb8 cima](img/memb8_cima.png) | ![preset_memb8 quina](img/memb8_quina.png) |

### `preset_memb9`

Leaflet asymmetry and thickness. One translucent surface per leaflet, phosphates marking the planes.

```
preset_memb9
```

| side | top | corner |
|---|---|---|
| ![preset_memb9 lado](img/memb9_lado.png) | ![preset_memb9 cima](img/memb9_cima.png) | ![preset_memb9 quina](img/memb9_quina.png) |

### `preset_memb10`

Print and one-column reduction. Dark tails as isosurface, light heads as spheres, nothing else.

```
preset_memb10
```

| side | top | corner |
|---|---|---|
| ![preset_memb10 lado](img/memb10_lado.png) | ![preset_memb10 cima](img/memb10_cima.png) | ![preset_memb10 quina](img/memb10_quina.png) |

