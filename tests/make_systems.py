"""Sistemas sinteticos para testar os presets.

Nenhum e fisicamente realista: sao o suficiente para exercitar cada caminho de
codigo. Os fatores B saem 0.00 de proposito, que e o que a dinamica molecular
escreve, e foi o que quebrou o mapa gaussiano do preset_memb5.

    python3 tests/make_systems.py [destino]
"""
import os
import sys

# POPC simplificado: colina, fosfato, glicerol e duas caudas de carbono.
# Coordenadas relativas ao fosforo, em angstrom. Sao 33 atomos por lipideo,
# acima do corte de 25 que separa all-atom de coarse-grained.
POPC = [
    ("N", "N", 0.0, 0.0, 4.4), ("C11", "C", 0.9, 0.5, 3.5),
    ("C12", "C", -0.9, 0.4, 3.4), ("P", "P", 0.0, 0.0, 2.2),
    ("O11", "O", 1.3, 0.2, 1.6), ("O12", "O", -1.3, 0.1, 1.6),
    ("O21", "O", 0.4, 1.0, 0.4), ("O22", "O", -0.4, -1.0, 0.3),
    ("C1", "C", 0.0, 0.0, -0.6), ("C2", "C", 0.6, 0.7, -1.8),
    ("C3", "C", -0.6, -0.7, -1.9), ("C4", "C", 0.5, 0.6, -3.1),
    ("C5", "C", -0.5, -0.6, -3.2), ("C6", "C", 0.4, 0.5, -4.5),
    ("C7", "C", -0.4, -0.5, -4.6), ("C8", "C", 0.3, 0.3, -5.9),
    ("C9", "C", -0.3, -0.3, -6.0),
]
for _k in range(8):
    _z = -7.2 - _k * 1.25
    POPC.append(("C%d" % (10 + 2 * _k), "C", 0.35, 0.35, _z))
    POPC.append(("C%d" % (11 + 2 * _k), "C", -0.35, -0.35, _z - 0.1))

# Peptideo helicoidal minimo, so backbone mais CB, alternando residuos
# carregados e apolares para os esquemas de carga terem o que separar.
HELIX_RESN = ["LYS", "LEU", "ALA", "GLU", "LEU", "ARG",
              "ILE", "ASP", "PHE", "LYS", "VAL", "GLU"]


class Writer(object):
    def __init__(self):
        self.lines = []
        self.serial = 1
        self.resi = 1

    def atom(self, resn, name, elem, x, y, z, chain="A"):
        # resName ocupa 18-21 e chainID 22: POPC tem quatro caracteres e nao
        # cabe nas tres colunas do padrao estrito, que e como os PDB de
        # membrana saem na pratica.
        self.lines.append(
            "ATOM  %5d %-4s %-4s%1s%4d    %8.3f%8.3f%8.3f%6.2f%6.2f          %2s"
            % (self.serial, name, resn, chain, self.resi, x, y, z,
               1.00, 0.00, elem.rjust(2)))
        self.serial += 1

    def save(self, path):
        open(path, "w").write("\n".join(self.lines + ["END"]) + "\n")
        return self.serial - 1


def bilayer(w, nx=6, ny=6, spacing=8.0, z_head=18.0, x0=0.0):
    for sign in (1, -1):
        for i in range(nx):
            for j in range(ny):
                for name, elem, dx, dy, dz in POPC:
                    w.atom("POPC", name, elem, x0 + i * spacing + dx,
                           j * spacing + dy, sign * (z_head + dz))
                w.resi += 1


def helix(w, x0=0.0, y0=0.0, z0=0.0, chain="B", n=None):
    """Helice alfa aproximada: 100 graus e 1.5 A de passo por residuo."""
    import math
    resns = HELIX_RESN if n is None else (HELIX_RESN * 4)[:n]
    for k, resn in enumerate(resns):
        ang = math.radians(100.0 * k)
        r = 2.3
        cx, cy = x0 + r * math.cos(ang), y0 + r * math.sin(ang)
        cz = z0 + 1.5 * k
        for name, elem, dx, dy, dz in (("N", "N", -0.6, 0.0, -0.5),
                                       ("CA", "C", 0.0, 0.0, 0.0),
                                       ("C", "C", 0.6, 0.2, 0.5),
                                       ("O", "O", 1.1, -0.5, 1.0),
                                       ("CB", "C", 0.2, 1.4, -0.4)):
            w.atom(resn, name, elem, cx + dx, cy + dy, cz + dz, chain)
        w.resi += 1


def solvent(w, count, x_span, y_span, z_levels, z0, spacing=3.2):
    for k in range(count):
        i = k % x_span
        j = (k // x_span) % y_span
        lvl = k // (x_span * y_span)
        z = z0 + (lvl % z_levels) * spacing
        if k % 2:
            z = -z
        w.atom("SOL", "OW", "O", i * 4.0 + 1.5, j * 4.0 + 1.5, z)
        w.resi += 1


def ions(w, count, z):
    for k in range(count):
        w.atom("NA", "NA", "NA", (k % 6) * 8.0, (k // 6) * 16.0,
               z if k % 2 else -z)
        w.resi += 1


def build(dest):
    feitos = []

    # 1. Bicamada com agua e ions, sem proteina.
    w = Writer()
    bilayer(w)
    solvent(w, 600, 6, 6, 8, 30.0)
    ions(w, 12, 27.0)
    p = os.path.join(dest, "membrana.pdb")
    feitos.append((p, w.save(p)))

    # 2. Bicamada com peptideo inserido: exercita preset_memb8 e memb_protein.
    w = Writer()
    bilayer(w)
    helix(w, x0=20.0, y0=20.0, z0=-16.0, chain="B", n=22)
    solvent(w, 400, 6, 6, 6, 30.0)
    ions(w, 12, 27.0)
    p = os.path.join(dest, "membrana_peptideo.pdb")
    feitos.append((p, w.save(p)))

    # 3. Peptideo sozinho, sem agua e sem identificador de cadeia: e o caso
    # que quebrava prot_water, prot_ions e a cor por cadeia.
    w = Writer()
    helix(w, chain=" ", n=12)
    p = os.path.join(dest, "peptideo.pdb")
    feitos.append((p, w.save(p)))

    # 4. Duas cadeias solvatadas com ions: caixa de MD, para preset_prot7,
    # preset_prot9 e a interface do preset_prot10.
    w = Writer()
    helix(w, x0=0.0, y0=0.0, chain="A", n=24)
    helix(w, x0=9.0, y0=2.0, chain="B", n=24)
    solvent(w, 800, 8, 8, 10, 12.0)
    ions(w, 16, 14.0)
    p = os.path.join(dest, "complexo_solvatado.pdb")
    feitos.append((p, w.save(p)))

    return feitos


if __name__ == "__main__":
    destino = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(
        os.path.abspath(__file__))
    for caminho, n in build(destino):
        print("%-28s %d atomos" % (os.path.basename(caminho), n))
