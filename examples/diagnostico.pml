# Diagnostico de sistema com nomenclatura desconhecida.
# Rode quando obj_lipid vier vazio ou as camadas nao receberem cor.

python
from pymol import cmd

resn_count = {}
cmd.iterate("all", "resn_count[resn] = resn_count.get(resn, 0) + 1",
            space={"resn_count": resn_count})
print("Residuos mais frequentes:")
for resn, n in sorted(resn_count.items(), key=lambda kv: -kv[1])[:25]:
    print("  %-6s %d" % (resn, n))

names = {}
cmd.iterate("not polymer", "names.setdefault(resn, set()).add(name)",
            space={"names": names})
print()
print("Nomes de atomo por residuo (nao polimerico):")
for resn, ns in sorted(names.items()):
    print("  %s (%d nomes): %s" % (resn, len(ns), " ".join(sorted(ns))))

print()
for resn, n in sorted(resn_count.items(), key=lambda kv: -kv[1])[:5]:
    n_at = cmd.count_atoms("resn %s" % resn)
    n_res = len(set(cmd.get_model("resn %s" % resn).get_residues()))
    if n_res:
        print("  %s: %.1f atomos por residuo (~12 = Martini, ~50 = all-atom)"
              % (resn, n_at / float(n_res)))
python end
