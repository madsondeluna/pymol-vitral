## Protein presets

Ten presets, rendered below from `prot/4hhb.pdb`, haemoglobin: four chains,
four haems, 221 waters. Every one takes an optional `paper` argument, the
column width in millimetres, which makes the scene come out ready for print in
the same line: `preset_prot3 paper=85`.

```
load prot/4hhb.pdb
run /path/to/pymol-molviz/molviz.pml
```

### `preset_prot1` cartoon by secondary structure

Domain topology.

```
preset_prot1
```

| Element | Representation |
|---|---|
| Protein | cartoon: oval for sheet, automatic for helix, loop elsewhere |
| Colour | helix blue, sheet red, loop white |
| Ligands | sticks, radius 0.22 |
| Ions | spheres, scale 0.45 |
| Water | off |

The only preset that communicates global topology. Cartoon receives no ambient occlusion in PyMOL, so this is the scene with the least contact relief.

| Side | Top |
|---|---|
| ![Side](../img/prot1_lado.png) | ![Top](../img/prot1_cima.png) |

### `preset_prot2` cartoon under a ghost surface

Binding site.

```
preset_prot2
```

| Element | Representation |
|---|---|
| Protein | cartoon under a molecular surface at transparency 0.55 |
| Colour | secondary structure |
| Ligands | sticks, radius 0.22, visible through the surface |
| Ions | spheres, scale 0.45 |
| Water | off |

Keeps the molecular outline without losing the fold. An opaque surface would bury the ligand.

| Side | Top |
|---|---|
| ![Side](../img/prot2_lado.png) | ![Top](../img/prot2_cima.png) |

### `preset_prot3` solid surface by hydrophobicity

Interaction face, amphipathicity.

```
preset_prot3
```

| Element | Representation |
|---|---|
| Protein | solid molecular surface, solvent radius 1.4 |
| Colour | Kyte-Doolittle gradient |
| Ligands | sticks, radius 0.22 |
| Ions | spheres, scale 0.45 |
| Water | off |

The surface does receive ambient occlusion, so this is the scene with the most relief. It writes to the B-factor column; `prot_restore_b` puts the original values back.

| Side | Top |
|---|---|
| ![Side](../img/prot3_lado.png) | ![Top](../img/prot3_cima.png) |

### `preset_prot4` spacefill by chain

Complex architecture.

```
preset_prot4
```

| Element | Representation |
|---|---|
| Protein | spheres at van der Waals radius, scale 1.0 |
| Colour | one per chain, from an eight-colour cycle |
| Ligands | spheres at van der Waals radius |
| Ions | spheres, scale 0.45 |
| Water | off |

Occupied volume and packing. In a multi-chain complex this is the most direct way to show the arrangement of the assembly.

| Side | Top |
|---|---|
| ![Side](../img/prot4_lado.png) | ![Top](../img/prot4_cima.png) |

### `preset_prot5` putty by b-factor

Flexibility.

```
preset_prot5
```

| Element | Representation |
|---|---|
| Protein | cartoon in putty mode, thickness 0.6 to 3.5, radius 0.35 |
| Colour | B-factor as deposited |
| Ligands | sticks, radius 0.22 |
| Ions | spheres, scale 0.45 |
| Water | off |

Thickness encodes the B-factor: a flexible region comes out thick and red. Valid for experimental structures. On a predicted model the B column usually carries pLDDT, whose scale means the opposite.

| Side | Top |
|---|---|
| ![Side](../img/prot5_lado.png) | ![Top](../img/prot5_cima.png) |

### `preset_prot6` all-atom licorice by charge

Peptides.

```
preset_prot6
```

| Element | Representation |
|---|---|
| Protein | all-atom sticks, radius 0.20, side chain helper off |
| Colour | basic blue, acidic red, polar light blue, apolar yellow |
| Ligands | sticks, radius 0.22 |
| Ions | spheres, scale 0.45 |
| Water | off |

For peptides, where cartoon says little: there is no global topology to summarise and the information is in the side chain. Above 60 residues it warns and the scene becomes an illegible mass.

| Side | Top |
|---|---|
| ![Side](../img/prot6_lado.png) | ![Top](../img/prot6_cima.png) |

### `preset_prot7` solvated system

MD box, solvation shell.

```
preset_prot7
```

| Element | Representation |
|---|---|
| Protein | cartoon, oval sheet and loop |
| Colour | secondary structure |
| Water | only within 4.0 A of the protein, selected by `byres` |
| Ions | only within 6.0 A of the protein |
| Ligands | sticks, radius 0.22 |

Discards bulk water and ions, which in a typical box are more than 90 per cent of the atoms and hide the solute entirely. Takes the shell radius: `preset_prot7 6.0`.

| Side | Top |
|---|---|
| ![Side](../img/prot7_lado.png) | ![Top](../img/prot7_cima.png) |

### `preset_prot8` full box

The simulated system as a whole.

```
preset_prot8
```

| Element | Representation |
|---|---|
| Protein | molecular surface |
| Colour | formal charge |
| Water | surface at transparency 0.72, inflated oxygen radius |
| Ions | opaque core with a translucent solvation shell |
| Ligands | sticks, radius 0.22 |

Illustrates box dimensions and the solute to solvent ratio. It does not serve to analyse the protein: the solvent volume covers it by construction.

| Side | Top |
|---|---|
| ![Side](../img/prot8_lado.png) | ![Top](../img/prot8_cima.png) |

### `preset_prot9` simulation box, measured

Box dimensions.

```
preset_prot9
```

| Element | Representation |
|---|---|
| Protein | molecular surface |
| Colour | formal charge |
| Water | gaussian field at transparency 0.82 |
| Ions | spheres, scale 0.45 |
| Box | twelve edges drawn as lines, from the extent of what is loaded |

The box comes from the extent of the loaded system rather than a CRYST1 record, which MD frames often lack. It prints the dimensions to the log, ready for the caption.

| Side | Top |
|---|---|
| ![Side](../img/prot9_lado.png) | ![Top](../img/prot9_cima.png) |

### `preset_prot10` interface in licorice

Where two chains, or protein and ligand, touch.

```
preset_prot10
```

| Element | Representation |
|---|---|
| Protein | cartoon at transparency 0.72, side chain helper on |
| Colour | secondary structure |
| Contacts | side chains in opaque sticks, radius 0.20 |
| Contact colour | carbon by residue class, everything else by element |
| Ligands | sticks, radius 0.24, own carbon colour |
| Water | off |

With more than two chains it shows the pair with the largest contact and hides the rest: a tetramer puts three different interfaces in one frame and none of them reads. Takes the pair: `preset_prot10 cadeias=A C`. Surface is the wrong representation here, because a closed surface hides the contact area, which sits between the two parts.

| Side | Top |
|---|---|
| ![Side](../img/prot10_lado.png) | ![Top](../img/prot10_cima.png) |

