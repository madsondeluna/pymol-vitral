# pymol-molviz

Visualization presets for PyMOL, aimed at molecular simulation systems: lipid
bilayers, proteins and peptides. The package splits the loaded system into
independent objects, applies a calibrated material and exposes numbered presets
that combine one representation per component.

Requirements: PyMOL 2.x, open-source or incentive. No external dependencies.

## Getting started

Three steps, in this order: load the system, load the protocol, apply a preset.
The order matters. The protocol splits whatever is already in the session, so
loading it before the structure leaves it with nothing to split.

### 1. Load the system

From the PyMOL command line. One line at a time: the Qt command bar is
single-line, so a multi-line paste becomes one command.

```
load /path/to/membrane.pdb
```

Anything PyMOL reads works the same way: a protein, a membrane, a solvated box,
a single frame of a trajectory.

```
load /path/to/protein.pdb
load /path/to/frame.pdb
```

From the PDB, without a local file:

```
fetch 4HHB, async=0
```

From the menu, `File > Open` does the same thing.

For a molecular dynamics frame, fix the periodic image before opening PyMOL,
or the protein may sit split across the box edges and the solvation shell comes
out empty:

```
gmx trjconv -s topol.tpr -f traj.xtc -o frame.pdb -pbc mol -center -dump 0
```

### 2. Load the protocol

```
run /path/to/pymol-molviz/molviz.pml
```

It splits the system into objects, prints the counts and applies a starting
preset: membrane if lipids are present, protein otherwise. The log names the
version and the directory it loaded from:

```
[molviz] v1.2.0 carregado de /path/to/pymol-molviz/pymol_molviz
```

Running it again always rereads from disk, so it doubles as the way to pick up
an edit. Add the same line to `~/.pymolrc` to have it in every session, and
then this step disappears: opening PyMOL is enough.

### 3. Apply a preset

```
preset_memb1
preset_prot1
```

Ten of each, listed below. Switching preset does not require reloading
anything: the split already happened, and each preset only changes
representation and colour.

Every preset takes an optional `paper` argument, the column width in
millimetres, which makes the scene come out ready for print in the same line:

```
preset_memb5 paper=85
```

Then colour, water and ions are adjustable without leaving the preset:

```
memb_color leaflet
memb_water off
prot_water shell, 6.0
```

And the figure goes out with:

```
mv_render figure.png, 2000, 1500, 300
```

### What the log tells you

Read the counts after step 2. `obj_lipid` with zero atoms means the residue
list does not cover the system; `examples/diagnostico.pml` lists what is
actually in the file. The protocol also reports two things it corrected on the
way in: atoms whose element it had to infer from the atom name, and residue
names that look like ions but are not.

## Install

No install step. Clone or unpack the repository anywhere; `molviz.pml` resolves
its own directory, so it works from any location.

Requirements: PyMOL 2.x or 3.x, open-source or incentive. No external
dependencies.

## Objects

The split produces one object per component, each with its own enable dot in
the side panel.

| Object | Content |
|---|---|
| `obj_lipid` | lipids, subdivided into `lip_head`, `lip_phos`, `lip_glyc`, `lip_tail` |
| `obj_prot` | protein or peptide |
| `obj_wat` | water |
| `obj_ions` | ions |
| `obj_lig` | ligands |
| `obj_nucl` | nucleic acid |

### How the lipid layers are found

`obj_lipid` is split into four layers, and none of them comes from a list of
atom names: nomenclature varies between CHARMM, Berger, Slipids and GROMOS
while the topology does not.

| Layer | Criterion |
|---|---|
| `lip_phos` | phosphorus plus the oxygens bonded to it |
| `lip_head` | nitrogen and its neighbouring carbons, plus whatever sits beyond the phosphate |
| `lip_glyc` | the remaining ester oxygens and the carbons adjacent to them |
| `lip_tail` | the complement |

The head takes three passes, in this order, and each one only fills what the
previous left empty.

**Nitrogen.** Reaches choline and ethanolamine, so PC and PE resolve
chemically. It is also the only pass that works on coarse-grained systems.

**Position.** Phosphatidylglycerol, phosphatidylinositol, phosphatidylserine
and cardiolipin carry no nitrogen at all, and in a mixed system that leaves
most lipids with no head: the layer disappears from the figure and `moiety`
colouring shows three bands instead of four. What defines a polar head is not
its chemistry, which varies by species, but its position: it is the part facing
the solvent, beyond the phosphate. The comparison is per molecule against its
own phosphorus, not against the mean of the leaflet, because with the mean the
molecules sitting deeper than average lose the head entirely. This assumes the
membrane normal along z, the same premise as `memb_color leaflet`.

**Name.** Two cases escape position, and neither is a failure of it: a head
folded inwards is not beyond the phosphate, and the central glycerol of
cardiolipin sits *between* the two phosphates, so it is more internal than they
are by construction. For those there is a CHARMM dictionary, applied per
species and only where fewer than half the molecules were left uncovered. The
log says when it fires.

Measured on a mixed system of 200 lipids across six species plus cardiolipin:

| Passes | Lipids with a head |
|---|---|
| Nitrogen only | 29 per cent |
| Nitrogen and position | 84 per cent |
| All three | 100 per cent |

