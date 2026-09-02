# pymol-molviz

Presets de visualizacao para PyMOL, voltados a sistemas de simulacao molecular:
membranas lipidicas, proteinas e peptideos.

O pacote divide o sistema carregado em objetos independentes, aplica um material
calibrado (plastico opaco, oclusao ambiente, fundo branco) e expoe presets
numerados que combinam representacoes de cada componente. Um unico comando
carrega tudo.

## Instalacao

Nao ha instalacao. Clone ou descompacte o repositorio em qualquer lugar e, de
dentro do PyMOL:

```
run /caminho/pymol-molviz/molviz.pml
```

O arquivo descobre sozinho o diretorio do repositorio e registra os comandos.
Para carregar em toda sessao, adicione a mesma linha ao `~/.pymolrc`.

Requisitos: PyMOL 2.x, open-source ou incentive. Nenhuma dependencia externa.

## Uso

Carregue a estrutura primeiro, depois o pacote. Ele detecta o tipo de sistema e
aplica um preset inicial: membrana se houver lipideos, proteina caso contrario.

```
load sistema.pdb
run /caminho/pymol-molviz/molviz.pml
```

Depois e so trocar de preset:

```
preset_memb5
memb_color leaflet
mv_render figura.png, 2000, 1500, 300
```

Cada componente vira um objeto proprio no painel lateral (`obj_lipid`,
`obj_wat`, `obj_ions`, `obj_prot`), com ponto de enable e botoes A/S/H/L/C para
mostrar e ocultar com um clique.

## Comandos

**Membranas** — `preset_memb1` a `preset_memb6`, `memb_color`, `memb_water`,
`memb_split`, `memb_protein`

**Proteinas** — `preset_prot1` a `preset_prot8`, `prot_color`, `prot_water`,
`prot_ions`, `prot_split`, `prot_restore_b`, `prot_auto`

**Comum** — `mv_material`, `mv_ao`, `mv_shadows`, `mv_realism`,
`mv_desaturate`, `mv_paper`, `mv_grayscale`, `mv_extent`, `mv_render`

## Documentacao

| Arquivo | Conteudo |
|---|---|
| [`docs/passo-a-passo.md`](docs/passo-a-passo.md) | Nove fluxos numerados, comando a comando. Comece por aqui. |
| [`docs/presets.md`](docs/presets.md) | O que cada preset mostra e a que pergunta responde. |
| [`docs/limitacoes.md`](docs/limitacoes.md) | Limitacoes do PyMOL e problemas comuns, com causa e solucao. |
| [`docs/adaptacao.md`](docs/adaptacao.md) | Onde editar para outro force field, outra escala ou um preset novo. |

## Estrutura

```
pymol-molviz/
├── molviz.pml              # ponto de entrada
├── pymol_molviz/
│   ├── __init__.py         # registro dos comandos e deteccao do sistema
│   ├── core.py             # paleta, material, iluminacao, saida
│   ├── membrane.py         # seis presets de membrana
│   └── protein.py          # oito presets de proteina
├── docs/
├── examples/               # sequencias prontas, executaveis com @
└── legacy/                 # scripts anteriores, sem manutencao
```

`core.py` concentra o que os dois modulos compartilham: material, oclusao
ambiente, sombras, modo periodico e exportacao. `membrane.py` e `protein.py`
contem apenas o que e especifico de cada dominio.

## Exemplos

Sequencias completas, executaveis direto:

```
@/caminho/pymol-molviz/examples/figura_membrana.pml
@/caminho/pymol-molviz/examples/figura_peptideo.pml
@/caminho/pymol-molviz/examples/md_solvatada.pml
@/caminho/pymol-molviz/examples/diagnostico.pml
```

O ultimo nao desenha nada: lista residuos, nomes de atomo e a razao atomos por
residuo, para descobrir a nomenclatura de um sistema desconhecido.

## Decisoes de projeto

**Selecoes por criterio quimico, nao por nome de atomo.** A nomenclatura varia
entre CHARMM, Berger, Slipids e Martini; a topologia nao. As camadas de um
lipideo sao definidas por elemento e conectividade, e o modulo cai para nomes
Martini apenas quando detecta um sistema coarse-grained.

**Objetos, nao selecoes.** Selecao serve para aplicar comandos; objeto tem
ponto de enable proprio. A divisao em objetos e o que permite mostrar e ocultar
componentes com um clique.

**Nivel de isosuperficie derivado do histograma.** Um nivel fixo falha em
silencio quando a resolucao gaussiana muda: o `isosurface` nao gera triangulo
nenhum, e objeto vazio nao e registrado pelo PyMOL.

**Fatores B preservados.** Colorir por hidrofobicidade exige escrever na coluna
B, ja que o PyMOL nao tem campo generico por atomo para gradiente. Os valores
originais sao salvos no split e `prot_restore_b` os devolve.

**Um material, varios niveis.** Oclusao ambiente e sombra projetada competem
pelo mesmo orcamento de luz, entao os comandos de ajuste alteram varios
parametros em conjunto em vez de expor cada um isoladamente.

## Licenca

MIT.
