# Referencia dos presets

Cada preset e uma combinacao de representacoes, escolhida para responder a um
tipo de pergunta. Nenhum e melhor que os outros em abstrato: o criterio e o que
a figura precisa comunicar.

## Membranas

| Comando | Lipideo | Ions | Agua | Responde a |
|---|---|---|---|---|
| `preset_memb1` | esferas com folga (0.55), cor por camada quimica | esferas opacas medias | superficie translucida | leitura geral, organizacao em camadas |
| `preset_memb2` | spacefill em raio de van der Waals, cor por folheto | spacefill em raio real | superficie muito translucida | volume ocupado, barreira |
| `preset_memb3` | licorice com cabecas em esfera | nucleo opaco com casca de solvatacao | esferas translucidas | interacao ion-cabeca polar |
| `preset_memb4` | superficie translucida com licorice interno | esfera com malha de raio inflado | desligada | peptideo inserido |
| `preset_memb5` | caudas como isosuperficie continua, cabecas em esfera | esferas opacas grandes | campo gaussiano | ilustracao, sistema grande |
| `preset_memb6` | linhas, cor por especie | pontos | desligada | navegacao, nao figura |

`preset_memb4` e `preset_memb6` desligam a agua deliberadamente: no primeiro
porque a superficie do solvente esconderia o peptideo inserido, no segundo
porque ele existe para navegar rapido.

`preset_memb5` e ao mesmo tempo o mais leve e o mais proximo da estetica de
ilustracao cientifica, por trocar milhares de atomos de cauda por uma unica
isosuperficie. O nivel dessa isosuperficie e derivado do histograma do mapa,
nao fixo: um valor fixo falha em silencio quando a resolucao gaussiana muda.

### Cor

```
memb_color moiety | leaflet | type | depth
```

- `moiety` — cabeca, fosfato, glicerol, cauda
- `leaflet` — folheto superior e inferior
- `type` — uma cor por especie lipidica, para membranas mistas
- `depth` — gradiente continuo na normal, para inspecionar interdigitacao

### Agua

```
memb_water off | surface | spheres | field
```

`surface` infla o raio dos oxigenios e desenha a superficie molecular. E mais
previsivel que `field`, que usa mapa gaussiano e exige calibrar o nivel.

## Proteinas e peptideos

| Comando | Proteina | Responde a |
|---|---|---|
| `preset_prot1` | cartoon, helice azul / folha vermelha / alca branca | topologia de dominio |
| `preset_prot2` | cartoon com superficie translucida por fora | sitio de ligacao |
| `preset_prot3` | superficie solida, gradiente Kyte-Doolittle | face de interacao, anfipaticidade |
| `preset_prot4` | spacefill, cor por cadeia | arquitetura de complexo |
| `preset_prot5` | putty, espessura e cor pelo fator B | flexibilidade |
| `preset_prot6` | all-atom licorice, cor por carga | peptideos |
| `preset_prot7` | cartoon + camada de solvatacao + ions proximos | caixa de MD |
| `preset_prot8` | superficie por carga dentro do volume de solvente | ilustrar o sistema simulado |

`prot_auto` escolhe entre `preset_prot1` e `preset_prot6` pelo numero de
residuos, com corte em 60.

`preset_prot7` e `preset_prot8` respondem a perguntas diferentes: o primeiro
analisa a proteina no contexto do solvente, o segundo ilustra o sistema como um
todo. O segundo nao serve para analisar a proteina, porque o volume de solvente
a cobre por construcao.

### Cor

```
prot_color ss | chain | charge | hydro | bfactor | rainbow
```

- `ss` — estrutura secundaria
- `chain` — uma cor por cadeia
- `charge` — basicos azul, acidos vermelho, polares claros, apolares amarelo
- `hydro` — gradiente Kyte-Doolittle; sobrescreve a coluna B
- `bfactor` — fator B como esta no arquivo
- `rainbow` — gradiente N para C

### Solvente e ions

```
prot_water off | shell | spheres | surface | field
prot_ions  off | spheres | vdw | halo | mesh | shell
```

O modo `shell` e o padrao e nao existe no modulo de membranas: exibe apenas
agua ou ions dentro de um raio da proteina. Numa caixa de MD tipica o solvente
de bulk passa de 90% dos atomos e esconde o soluto, enquanto a primeira camada
de solvatacao costuma ser o objeto de interesse.

A selecao de agua usa `byres`, para nao exibir meia molecula quando apenas o
oxigenio cai dentro do raio.

## Iluminacao, material e saida

Comandos com prefixo `mv_`, compartilhados pelos dois modulos.

```
mv_material
mv_ao        off | soft | medium | strong | extreme
mv_shadows   off | soft | medium | hard
mv_realism   studio | depth | dramatic | flat
mv_desaturate 0.18
mv_paper     85
mv_grayscale 1
mv_extent    obj_lipid
mv_render    figura.png, 2000, 1500, 300
```

Cada nivel ajusta varios parametros em conjunto, nao um isolado:

**A oclusao ambiente modula o termo ambiente.** Com `ambient` baixo ela esta
ligada mas nao aparece. Por isso os niveis sobem `ambient` e baixam `direct` ao
mesmo tempo.

**As sombras exigem o oposto:** luz direta forte. Os dois competem pelo mesmo
orcamento de luz, e `soft` e `medium` sao os pontos em que convivem.

**A maciez da sombra custa tempo.** O PyMOL nao tem raio de fonte de luz: a
penumbra vem de varias luzes projetando sombras sobrepostas. `soft` usa seis
luzes e demora mais que `hard`, que usa uma.

**Ordem importa.** `mv_realism` sobrescreve `mv_shadows`, que sobrescreve
`mv_ao`. Aplique do mais geral para o mais especifico.

### Figura de periodico

`mv_paper` difere de `mv_realism` em tres pontos deliberados: desliga a sombra
projetada (ruido em figura reduzida), usa projecao ortografica (perspectiva faz
um folheto plano parecer curvo, o que e desonesto numa figura quantitativa) e
restaura a paleta saturada, porque cor saturada separa melhor as camadas quando
a figura cai para a largura de uma coluna.

Ele imprime no log a resolucao alvo em pixels e a linha de render pronta.

O teste em escala de cinza nao e opcional. Cores de luminancia proxima (o verde
das cabecas contra o laranja das caudas, o azul das helices contra o vermelho
das folhas) podem colapsar no mesmo tom. Se ocorrer, diferencie por claridade,
nao apenas por matiz.
