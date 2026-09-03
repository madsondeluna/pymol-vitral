# Passo a passo

Guia de execução. Cada fluxo é uma sequência de comandos, na ordem em que devem
ser digitados na linha de comando do PyMOL. As linhas iniciadas por `#` são
comentário e o PyMOL as ignora, então copiar a linha do comentário junto com a
do comando é inofensivo.

Copie uma linha por vez. A barra de comando da interface Qt é de linha única, e
uma colagem de várias linhas vira um comando só. Para rodar um bloco inteiro,
salve num arquivo `.pml` e chame com `@arquivo.pml`.

Comentário no fim de uma linha de comando não funciona. `set sphere_scale, 0.55
# nota` faz o PyMOL tentar converter `0.55 # nota` em número e falhar. Por isso
a explicação vem sempre na linha de cima.

Substitua `/caminho/pymol-vitral/` pelo local real do repositório.

Para a referência completa, ver `presets.md`. Para os problemas conhecidos, ver
`limitacoes.md`.

## Fluxo 1. Membrana, escolhendo o preset

Carregue a estrutura antes do script. A ordem importa: o script divide o que já
estiver na sessão.

```
load /caminho/membrana.pdb
run /caminho/pymol-vitral/molviz.pml
```

Ele aplica o `preset_memb1` e imprime as contagens. Procure a linha que começa
com `[membrane]`. Se `obj_lipid` vier com zero átomos, a lista de resíduos não
cobre o seu sistema: pule para o Fluxo 6.

Os seis presets, um por vez. Cada um responde a uma pergunta diferente:

```
# Leitura geral. Esferas com folga, uma cor por camada química: cabeça,
# fosfato, glicerol, cauda. A folga é o que preserva a distinção que o
# spacefill cheio apaga. Água em superfície translúcida.
preset_memb1

# Volume ocupado e empacotamento. Raio de van der Waals real, uma cor por
# folheto. A organização interna some por construção: o que se vê é a barreira.
preset_memb2

# Interação íon com cabeça polar. Licorice deixa ver a conformação das caudas,
# e os íons ganham núcleo opaco com casca de solvatação. Água em esferas.
preset_memb3

# Peptídeo inserido. Superfície translúcida por fora, licorice fino por dentro,
# então o contorno da membrana fica sem esconder o que está dentro dela.
# A água fica desligada de propósito: a superfície do solvente cobriria o alvo.
preset_memb4

# Ilustração e sistema grande. As caudas viram uma isosuperfície gaussiana
# única, no lugar de milhares de átomos. É o mais leve e o mais próximo da
# estética de ilustração científica.
preset_memb5

# Navegação, não figura. Linhas, pontos, oclusão ambiente desligada. Existe
# para girar e enquadrar a cena antes de aplicar um preset caro.
preset_memb6

# Corte transversal. Uma fatia central do sistema em spacefill, com cabeça,
# fosfato, glicerol e cauda expostos na face cortada. O corte é uma seleção
# por coordenada, então girar a cena depois não muda o que está exposto.
preset_memb7

# O mesmo corte, no eixo x em vez do y. Aceita 0 para x, 1 para y, 2 para z.
preset_memb7 eixo=0

# Lipídeos anelares. Os que tocam a proteína ficam em licorice colorido e o
# resto da membrana vira fantasma. Precisa de proteína na sessão.
preset_memb8

# O mesmo, com outro raio de contato em angstrom.
preset_memb8 raio=7.0

# Assimetria e espessura. Um folheto por superfície translúcida, em cores
# distintas, com os fosfatos em esfera marcando os dois planos.
preset_memb9

# Para reduzir a uma coluna e imprimir em preto e branco. Duas cores só,
# separadas por claridade e não por matiz, sem água nem íons competindo.
preset_memb10
```

Todo preset aceita `paper`, a largura de coluna em milímetros. Sem ele a
iluminação fica como está, para explorar na tela. Com ele a cena já sai no modo
de periódico:

```
# explorar na tela, e decidir depois
preset_memb5

# já sair pronto para coluna simples
preset_memb5 paper=85

# largura dupla
preset_memb5 paper=170
```

Trocar o esquema de cor, sem trocar de preset:

```
# cabeça, fosfato, glicerol, cauda
memb_color moiety

# folheto superior contra folheto inferior
memb_color leaflet

# uma cor por espécie lipídica, para membrana mista
memb_color type

# gradiente contínuo na normal, para ver interdigitação
memb_color depth
```

Trocar o tratamento da água:

```
# previsível: infla o raio dos oxigênios e desenha a superfície molecular
memb_water surface

# esferas individuais
memb_water spheres

# campo gaussiano contínuo, exige calibrar o nível
memb_water field

memb_water off
```

Enquadrar, conferir o material e alternar componentes:

```
orient obj_lipid
zoom obj_lipid, 3

# o viewport não mostra especular nem antialiasing
ray 1600, 1200

disable obj_wat
enable obj_wat
```

## Fluxo 2. Proteína, escolhendo o preset

```
load /caminho/proteina.pdb
run /caminho/pymol-vitral/molviz.pml
```

O preset inicial sai do tamanho: abaixo de 60 resíduos abre em all-atom por
carga, acima abre em cartoon. Na linha `[prot]` do log estão os objetos criados
e o número de resíduos. Se aparecer `estrutura secundaria atribuida com dss`, o
arquivo não trazia registros HELIX e SHEET e o script os calculou.

Os oito presets:

```
# Topologia de domínio. Hélice azul, folha vermelha, alça branca. É o único que
# comunica topologia global. Cartoon não recebe oclusão ambiente no PyMOL, então
# esta é a cena com menos relevo do conjunto.
preset_prot1

# Sítio de ligação. Mesmo cartoon, com superfície translúcida por fora: o
# ligante continua visível por dentro, o que uma superfície opaca impediria.
preset_prot2

# Face de interação e anfipaticidade. Superfície sólida com gradiente
# Kyte-Doolittle. Recebe oclusão ambiente, então é a cena com mais relevo.
# Escreve na coluna B; prot_restore_b desfaz.
preset_prot3

# Arquitetura de complexo. Spacefill, uma cor por cadeia.
preset_prot4

# Flexibilidade. Putty: a espessura codifica o fator B, região flexível fica
# grossa e vermelha. Vale para estrutura experimental. Em modelo predito a
# coluna B costuma trazer pLDDT, cuja escala significa o oposto.
preset_prot5

# Peptídeos. All-atom licorice colorido por carga, que expõe a anfipaticidade
# direto na cadeia lateral. Acima de 60 resíduos vira massa ilegível, e o
# comando avisa no log quando é o caso.
preset_prot6

# Caixa de dinâmica molecular. Cartoon mais a água a 4 A e os íons a 6 A da
# proteína. Descarta o solvente de bulk, que numa caixa típica passa de 90%
# dos átomos e esconde o soluto.
preset_prot7

# Ilustrar o sistema simulado inteiro: dimensão da caixa, proporção entre
# soluto e solvente. Não serve para analisar a proteína, porque o volume de
# solvente a cobre por construção.
preset_prot8

# Caixa de simulação documentada: soluto em superfície, solvente como campo, e
# as doze arestas da caixa desenhadas. As dimensões vão para o log, prontas
# para a legenda. A caixa sai do extent do que está carregado, e não de um
# CRYST1, que frame de dinâmica molecular costuma não ter.
preset_prot9

# Interface de contato. O corpo vira cartoon translúcido, como no preset_prot1,
# e as cadeias laterais que tocam a outra parte vêm para a frente em licorice
# opaco. Com mais de duas cadeias, mostra o par de maior contato e esconde o
# resto. Serve tanto a proteína-proteína quanto a proteína-ligante.
preset_prot10

# Escolher outro par de cadeias.
preset_prot10 cadeias=A C

# Raio de contato maior, para pegar a segunda camada.
preset_prot10 raio=6.0
```

Aqui também vale o `paper`: `preset_prot9 paper=170` sai direto no modo de
periódico, em largura dupla.

Esquemas de cor:

```
# estrutura secundária
prot_color ss

# uma cor por cadeia
prot_color chain

# básicos azul, ácidos vermelho, polares claros, apolares amarelo
prot_color charge

# gradiente Kyte-Doolittle, sobrescreve a coluna B
prot_color hydro

# fator B como está no arquivo
prot_color bfactor

# gradiente do N para o C terminal
prot_color rainbow

# devolve os fatores B originais depois de hydro
prot_restore_b
```

Solvente e íons:

```
# só a água dentro do raio, selecionada por byres para não exibir meia molécula
prot_water shell, 4.0

prot_water spheres
prot_water surface
prot_water off

# só os íons dentro do raio
prot_ions shell, 6.0

# núcleo opaco com casca translúcida
prot_ions halo

# malha, marca a posição sem ocultar o que está atrás
prot_ions mesh

prot_ions off
```

## Fluxo 3. Peptídeo, com foco na anfipaticidade

Para peptídeos antimicrobianos e outros peptídeos curtos, onde a informação
está na cadeia lateral e não na topologia global.

```
load /caminho/peptideo.pdb
run /caminho/pymol-vitral/molviz.pml
```

Abaixo de 60 resíduos ele já abre no `preset_prot6`.

```
# segregação de carga: azul básicos, vermelho ácidos, amarelo apolares,
# azul claro polares
preset_prot6

# a mesma pergunta pela superfície de hidrofobicidade
preset_prot3
```

Se as duas faces se separam nos dois esquemas, a anfipaticidade é real. Se
aparece em um só, vale investigar antes de afirmar.

Alinhar o eixo da hélice na horizontal e renderizar as duas faces:

```
orient obj_prot
turn x, 90
mv_render face_a.png, 1200, 900
turn y, 180
mv_render face_b.png, 1200, 900
```

## Fluxo 4. Proteína solvatada, saída de dinâmica molecular

Corrija a imagem periódica antes de abrir o PyMOL. Sem isso a proteína pode
estar partida entre bordas da caixa, e a camada de solvatação sai vazia ou
errada. No terminal, com o GROMACS:

```
gmx trjconv -s topol.tpr -f traj.xtc -o frame.pdb -pbc mol -center -dump 0
```

Depois:

```
load /caminho/frame.pdb
run /caminho/pymol-vitral/molviz.pml

# água a 4 A e íons a 6 A da proteína, o resto do solvente oculto
preset_prot7

# aumentar a camada, se ela vier fina demais
prot_water shell, 6.0
prot_ions shell, 8.0

# para ilustrar a caixa inteira, em vez de analisar a proteína
preset_prot8
```

Se a camada vier vazia, o log avisa. A causa quase sempre é imagem periódica:
volte ao `trjconv`.

## Fluxo 5. Preparar uma figura para artigo

```
preset_memb5
```

Enquadre com cuidado. É o passo que mais afeta o resultado e o único que nenhum
script faz por você. Gire, aproxime e centralize até a figura comunicar o ponto
sozinha.

```
# 85 para coluna simples, 170 para largura dupla. Imprime no log a resolução
# alvo em pixels e a linha de render já pronta.
mv_paper 85

# teste de impressão em preto e branco, obrigatório
mv_grayscale 1
ray 1000, 750
mv_grayscale 0

# dimensões da cena, para a legenda
mv_extent obj_lipid

# resolução final, com os números que mv_paper imprimiu
mv_render figura.png, 1004, 753, 300
```

Se duas cores colapsarem no mesmo tom na escala de cinza, diferencie por
claridade, não apenas por matiz. Antes de submeter, confira o arquivo: fundo
branco, sem corte nas bordas, legenda coerente com as dimensões medidas.

## Fluxo 6. Sistema com nomenclatura desconhecida

Quando `obj_lipid` vem vazio, ou quando as camadas não recebem cor.

```
stored.r = {}
iterate all, stored.r[resn] = stored.r.get(resn, 0) + 1
print(sorted(stored.r.items(), key=lambda kv: -kv[1])[:30])
```

```
stored.n = {}
iterate not polymer, stored.n.setdefault(resn, set()).add(name)
print("\n".join("%s (%d): %s" % (k, len(v), " ".join(sorted(v))) for k, v in stored.n.items()))
```

Divida o número de átomos de um lipídeo pelo número de moléculas dele. Perto de
12 é Martini, perto de 50 é all-atom.

Os dicionários `LIPID_RESN` e `CG_NAMES` ficam no topo de
`pymol_molviz/membrane.py`. Adicione os resíduos que apareceram e recarregue:

```
delete obj_*
run /caminho/pymol-vitral/molviz.pml
```

## Fluxo 7. Ajustar iluminação

Comece pela oclusão ambiente, que dá o relevo de contato. Rode `ray` depois de
cada nível: o viewport mostra a oclusão, mas não o brilho especular.

```
mv_ao soft
mv_ao medium
mv_ao strong
```

Sombra projetada só aparece no `ray`, e em cena homogênea, como uma bicamada
pura, tende a virar ruído. A maciez custa tempo: `soft` usa seis luzes, `hard`
usa uma.

```
mv_shadows soft
ray 1600, 1200
```

Para ajustar o conjunto de uma vez:

```
mv_realism studio
```

A ordem importa. `mv_realism` sobrescreve `mv_shadows`, que sobrescreve
`mv_ao`. Aplique do mais geral para o mais específico.

## Fluxo 8. Recomeçar do zero

Quando a sessão acumulou objetos e seleções de tentativas anteriores.

```
delete obj_*
delete sel_*
delete lip_*
delete map_*
delete surf_*
```

O objeto original é desabilitado, não deletado: no painel ele aparece
esmaecido.

```
enable nome_do_objeto
```

Ou apague tudo e recarregue:

```
delete all
load /caminho/estrutura.pdb
run /caminho/pymol-vitral/molviz.pml
```

## Fluxo 9. Carregar automaticamente em toda sessão

Uma linha em `~/.pymolrc` registra os comandos em toda sessão. O arquivo fica
no seu home, fora do repositório, e é onde moram os caminhos desta máquina.

```
nano ~/.pymolrc
```

Conteúdo:

```
run /caminho/pymol-vitral/molviz.pml
```

Salve com Ctrl+O, Enter, Ctrl+X. Com a sessão vazia o script não altera nada,
apenas imprime que não há estrutura carregada.

Atalhos para as sequências de `examples/` entram no mesmo arquivo, com o
caminho já resolvido:

```
alias fig_membrana, @/caminho/pymol-vitral/examples/figura_membrana.pml
alias fig_peptideo, @/caminho/pymol-vitral/examples/figura_peptideo.pml
alias fig_md,       @/caminho/pymol-vitral/examples/md_solvatada.pml
alias diagnostico,  @/caminho/pymol-vitral/examples/diagnostico.pml
```
