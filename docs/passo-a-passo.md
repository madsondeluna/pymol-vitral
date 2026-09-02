# Passo a passo

Guia de execucao. Cada fluxo e uma sequencia numerada de comandos, na ordem em
que devem ser digitados na linha de comando do PyMOL.

Para a referencia completa dos presets, ver `docs/presets.md`. Para as
limitacoes do PyMOL que afetam o resultado, ver `docs/limitacoes.md`.

Substitua `/caminho/pymol-molviz/` pelo local real do repositorio em todos os
exemplos.

Um unico comando carrega tudo, membranas e proteinas:

```
run /caminho/pymol-molviz/molviz.pml
```

---

## Fluxo 1 — Visualizar uma membrana

**1. Abrir o PyMOL e carregar a estrutura.**
Pelo menu `File > Open`, ou pela linha de comando:

```
load /caminho/membrana.pdb
```

**2. Carregar a biblioteca.**

```
run /caminho/pymol-molviz/molviz.pml
```

Ele divide o sistema, aplica o `preset_memb1` e imprime as contagens. A ordem
importa: carregue a estrutura antes do script.

**3. Conferir as contagens no log.**
Procure a linha que comeca com `[membrane]`. Se `obj_lipid` vier com zero
atomos, a lista de residuos nao cobre o seu sistema — pule para o Fluxo 6.

**4. Testar os presets.**

```
preset_memb1
preset_memb2
preset_memb3
preset_memb4
preset_memb5
preset_memb6
```

**5. Trocar o esquema de cor, se quiser.**

```
memb_color leaflet
```

**6. Enquadrar a cena** com o mouse, ou:

```
orient obj_lipid
zoom obj_lipid, 3
```

**7. Ver o material real.**
O viewport nao mostra o modelo especular nem o antialiasing.

```
ray 1600, 1200
```

**8. Mostrar ou ocultar componentes.**
Clique no ponto ao lado de `obj_wat`, `obj_ions` ou `obj_lipid` no painel
lateral. Ou por comando:

```
disable obj_wat
enable obj_wat
```

---

## Fluxo 2 — Visualizar uma proteina

**1. Carregar a estrutura.**

```
load /caminho/proteina.pdb
```

**2. Carregar a biblioteca.**

```
run /caminho/pymol-molviz/molviz.pml
```

Ele decide o preset inicial pelo tamanho: abaixo de 60 residuos abre em
all-atom por carga, acima abre em cartoon.

**3. Conferir o log.**
A linha `[prot]` traz os objetos criados e o numero de residuos. Se aparecer
`estrutura secundaria atribuida com dss`, o arquivo nao tinha registros
HELIX/SHEET e o script os calculou.

**4. Testar os presets.**

```
preset_prot1
preset_prot2
preset_prot3
preset_prot4
preset_prot5
```

**5. Trocar o esquema de cor.**

```
prot_color charge
prot_color hydro
prot_color chain
```

**6. Renderizar.**

```
ray 1600, 1200
```

---

## Fluxo 3 — Peptideo, com foco na anfipaticidade

Para peptideos antimicrobianos e outros peptideos curtos, onde a informacao
esta na cadeia lateral e nao na topologia global.

**1. Carregar o peptideo.**

```
load /caminho/peptideo.pdb
```

**2. Carregar a biblioteca.**

```
run /caminho/pymol-molviz/molviz.pml
```

Abaixo de 60 residuos ele ja abre no `preset_prot6`.

**3. Ver a segregacao de carga.**

```
preset_prot6
```

Azul sao basicos, vermelho acidos, amarelo apolares, azul claro polares.

**4. Comparar com a superficie de hidrofobicidade.**

```
preset_prot3
```

Se as duas faces se separam nos dois esquemas, a anfipaticidade e real; se
so aparece em um, vale investigar antes de afirmar.

**5. Girar para achar a face.**
Arraste com o botao esquerdo. Para alinhar o eixo da helice na horizontal:

```
orient obj_prot
turn x, 90
```

**6. Renderizar as duas vistas** para comparar lado a lado:

```
mv_render face_a.png, 1200, 900
turn y, 180
mv_render face_b.png, 1200, 900
```

---

## Fluxo 4 — Proteina solvatada, saida de dinamica molecular

**1. Corrigir a imagem periodica antes de abrir o PyMOL.**
No terminal, com o GROMACS:

```
gmx trjconv -s topol.tpr -f traj.xtc -o frame.pdb -pbc mol -center -dump 0
```

Sem isso, a proteina pode estar partida entre bordas da caixa, e a camada de
solvatacao sai vazia ou errada.

**2. Carregar o frame.**

```
load /caminho/frame.pdb
```

**3. Carregar a biblioteca.**

```
run /caminho/pymol-molviz/molviz.pml
```

**4. Aplicar o preset de sistema solvatado.**

```
preset_prot7
```

Ele mostra so a agua a 4 A da proteina e os ions a 6 A. O resto do solvente e
bulk e fica oculto.

**5. Ajustar o raio da camada, se necessario.**

```
prot_water shell, 6.0
prot_ions shell, 8.0
```

**6. Se a camada vier vazia**, o log avisa. A causa quase sempre e imagem
periodica; volte ao passo 1.

**7. Para ilustrar a caixa inteira** em vez de analisar a proteina:

```
preset_prot8
```

---

## Fluxo 5 — Preparar uma figura para artigo

**1. Escolher e aplicar o preset** que responde a pergunta da figura.

```
preset_memb5
```

**2. Enquadrar com cuidado.**
Este e o passo que mais afeta o resultado e o unico que nenhum script faz por
voce. Gire, aproxime e centralize ate a figura comunicar o ponto sozinha.

**3. Trocar para o modo periodico.**

```
mv_paper 85
```

Use 85 para coluna simples, 170 para largura dupla. Ele imprime no log a
resolucao alvo em pixels e a linha de render pronta.

**4. Testar em escala de cinza.**

```
mv_grayscale 1
ray 1000, 750
```

Se duas cores colapsarem no mesmo tom, diferencie por claridade e nao apenas
por matiz. Depois:

```
mv_grayscale 0
```

**5. Pegar as dimensoes para a legenda.**

```
mv_extent obj_lipid
```

**6. Renderizar na resolucao final.**
Use os numeros que o passo 3 imprimiu:

```
mv_render figura.png, 1004, 753, 300
```

**7. Conferir o arquivo** antes de submeter: fundo branco, sem corte nas
bordas, texto da legenda coerente com as dimensoes medidas.

---

## Fluxo 6 — Sistema com nomenclatura desconhecida

Quando `obj_lipid` vem vazio, ou quando as camadas nao recebem cor.

**1. Listar os residuos presentes.**

```
stored.r = {}
iterate all, stored.r[resn] = stored.r.get(resn, 0) + 1
print(sorted(stored.r.items(), key=lambda kv: -kv[1])[:30])
```

**2. Listar os nomes de atomo por residuo.**

```
stored.n = {}
iterate not polymer, stored.n.setdefault(resn, set()).add(name)
print("\n".join("%s (%d): %s" % (k, len(v), " ".join(sorted(v))) for k, v in stored.n.items()))
```

**3. Estimar se e coarse-grained.**
Divida o numero de atomos de um lipideo pelo numero de moleculas dele. Perto
de 12 e Martini; perto de 50 e all-atom.

**4. Editar o dicionario correspondente.**
Em `pymol_molviz/membrane.py`, os dicionarios `LIPID_RESN` e `CG_NAMES` ficam
no topo do arquivo. Adicione os residuos que apareceram no passo 1.

**5. Recarregar.**

```
delete obj_*
run /caminho/pymol-molviz/molviz.pml
```

---

## Fluxo 7 — Ajustar iluminacao

**1. Comecar pela oclusao ambiente**, que da o relevo de contato.

```
mv_ao soft
mv_ao medium
mv_ao strong
```

Rode `ray` depois de cada um para comparar. O viewport mostra a oclusao, mas
nao o brilho especular.

**2. Adicionar sombra projetada,** se a cena tiver um objeto destacado.

```
mv_shadows soft
ray 1600, 1200
```

Sombras so aparecem no `ray`. Em cena homogenea, como uma bicamada pura, elas
tendem a virar ruido — considere manter em `off`.

**3. Ajustar o conjunto de uma vez,** se preferir.

```
mv_realism studio
```

**4. Ordem importa.**
`memb_shadows` sobrescreve `ambient` e `direct` definidos por `memb_ao`, e
`memb_realism` sobrescreve os dois. Aplique do mais geral para o mais
especifico.

---

## Fluxo 8 — Recomecar do zero

Quando a sessao acumulou objetos e selecoes de tentativas anteriores.

**1. Limpar os objetos derivados.**

```
delete obj_*
delete sel_*
delete lip_*
delete map_*
delete surf_*
```

**2. Reabilitar o objeto original.**
Os scripts o desabilitam, nao deletam. No painel ele aparece esmaecido.

```
enable nome_do_objeto
```

**3. Ou apagar tudo e recarregar.**

```
delete all
load /caminho/estrutura.pdb
run /caminho/pymol-molviz/molviz.pml
```

---

## Fluxo 9 — Carregar automaticamente em toda sessao

**1. Criar ou editar o `~/.pymolrc`.**
No terminal:

```
nano ~/.pymolrc
```

**2. Adicionar as linhas:**

```
run /caminho/pymol-molviz/molviz.pml
run /caminho/pymol-molviz/molviz.pml
```

**3. Salvar** com Ctrl+O, Enter, Ctrl+X.

Os comandos passam a existir em toda sessao. Note que os scripts tambem tentam
aplicar um preset ao carregar; com a sessao vazia isso e inofensivo, apenas
imprime `nada carregado`.

Se preferir que nao apliquem nada automaticamente, mova os arquivos para uma
pasta estavel (nao Downloads) e comente as duas ultimas linhas de cada um.
