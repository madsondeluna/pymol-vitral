## Colour, water and ions

```
memb_color   moiety | leaflet | type | depth
memb_water   off | surface | spheres | field
memb_split
memb_protein
prot_color   ss | chain | charge | hydro | bfactor | rainbow
prot_water   off | shell | spheres | surface | field
prot_ions    off | spheres | vdw | halo | mesh | shell
prot_split
prot_auto
prot_restore_b
```

`shell` exists in the protein module only. It shows water or ions within a
radius of the solute, selected by `byres`.

## Material, lighting and output

```
mv_material
mv_ao          off | soft | medium | strong | extreme
mv_shadows     off | soft | medium | hard
mv_realism     studio | depth | dramatic | flat
mv_desaturate  0.18
mv_paper       85
mv_grayscale   1
mv_extent      obj_lipid
mv_render      figure.png, 2000, 1500, 300
mv_reload
```

`mv_reload` re-imports the package from disk. Running `molviz.pml` again does
not: `import` finds the package already in `sys.modules` and hands back what is
in memory, so an edit appears to have no effect and a preset keeps printing the
previous version's message.

Ambient occlusion is on in every preset except `preset_memb6`, which turns it
off to keep navigation responsive. `ambient_occlusion_scale` is the sampling
distance in angstrom; PyMOL defaults to 25, which is calibrated for spheres and
saturates on a protein surface, where wide cavities come out as black patches.
The levels here sample between 8 and 22. Measured in both regimes: on membrane
spheres 12 and 25 render indistinguishably, and on a surface only the lower
value is usable. It does not reach cartoon: PyMOL bakes it
into sphere and surface geometry only, so a cartoon-based preset carries no
contact relief.

Each level sets several parameters at once. `mv_realism` overrides
`mv_shadows`, which overrides `mv_ao`: apply them from general to specific.
`mv_paper` takes a column width in millimetres, turns off cast shadows, sets
orthoscopic projection and prints the target resolution.

`mv_grayscale` rewrites every named colour in use to its own BT.601 luminance
and puts the originals back on the way out. PyMOL has no grayscale setting, so
a gradient applied by `spectrum` stays coloured and the log says how many
colours it could not reach.

