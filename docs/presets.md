# Referência dos presets

Cada preset é uma combinação de representações, escolhida para responder a um
tipo de pergunta. Nenhum é melhor que os outros em abstrato: o critério é o que
a figura precisa comunicar.

Para a sequência de comandos, ver `passo-a-passo.md`.

## Membranas

| Comando | Lipídeo | Íons | Água | Responde a |
|---|---|---|---|---|
| `preset_memb1` | esferas com folga (0.55), cor por camada química | esferas opacas médias | superfície translúcida | leitura geral, organização em camadas |
| `preset_memb2` | spacefill em raio de van der Waals, cor por folheto | spacefill em raio real | superfície muito translúcida | volume ocupado, barreira |
| `preset_memb3` | licorice com cabeças em esfera | núcleo opaco com casca de solvatação | esferas translúcidas | interação íon com cabeça polar |
| `preset_memb4` | superfície translúcida com licorice interno | esfera com malha de raio inflado | desligada | peptídeo inserido |
| `preset_memb5` | caudas como isosuperfície contínua, cabeças em esfera | esferas opacas grandes | campo gaussiano | ilustração, sistema grande |
| `preset_memb6` | linhas, cor por espécie | pontos | desligada | navegação, não figura |
| `preset_memb7` | fatia central em spacefill, cor por camada | esferas, só as da fatia | desligada | o interior da bicamada, corte transversal |
| `preset_memb8` | os que tocam a proteína em licorice, o resto fantasma | esferas pequenas | desligada | lipídeos anelares, contato proteína-lipídeo |
| `preset_memb9` | uma superfície translúcida por folheto, fosfatos em esfera | esferas médias | desligada | assimetria e espessura dos folhetos |
| `preset_memb10` | caudas escuras em isosuperfície, cabeças claras em esfera | desligados | desligada | redução para uma coluna, impressão em P&B |

`preset_memb4` e `preset_memb6` desligam a água deliberadamente: no primeiro
porque a superfície do solvente esconderia o peptídeo inserido, no segundo
porque ele existe para navegar rápido.

`preset_memb5` é ao mesmo tempo o mais leve e o mais próximo da estética de
ilustração científica, por trocar milhares de átomos de cauda por uma única
isosuperfície. O nível dessa isosuperfície é derivado do histograma do mapa,
não fixo: um valor fixo falha em silêncio quando a resolução gaussiana muda.

### Argumentos

Todo preset aceita `paper`, a largura de coluna em milímetros. Sem ele o preset
só define representação e cor, e a iluminação fica como estava: é o modo de
explorar na tela, com `mv_paper` depois se a figura for adiante. Com ele a cena
já sai pronta para impressão numa linha só.

```
preset_memb5
preset_memb5 paper=85
preset_memb5 paper=170
```

`preset_memb7` aceita `eixo`, 0 para x, 1 para y (padrão) e 2 para z. O corte é
uma seleção por coordenada e não o plano de recorte da câmera, então girar a
cena depois não muda o que está exposto.

`preset_memb8` aceita o raio de contato em angstrom, padrão 5.0, e precisa de
proteína na sessão. `preset_memb9` precisa de fosfatos para achar o plano
médio.

### Cor

```
memb_color moiety | leaflet | type | depth
```

- **moiety**: cabeça, fosfato, glicerol, cauda
- **leaflet**: folheto superior e inferior
- **type**: uma cor por espécie lipídica, para membranas mistas
- **depth**: gradiente contínuo na normal, para inspecionar interdigitação

### Água

```
memb_water off | surface | spheres | field
```

`surface` infla o raio dos oxigênios e desenha a superfície molecular. É mais
previsível que `field`, que usa mapa gaussiano e exige calibrar o nível.

## Proteínas e peptídeos

| Comando | Proteína | Responde a |
|---|---|---|
| `preset_prot1` | cartoon, hélice azul, folha vermelha, alça branca | topologia de domínio |
| `preset_prot2` | cartoon com superfície translúcida por fora | sítio de ligação |
| `preset_prot3` | superfície sólida, gradiente Kyte-Doolittle | face de interação, anfipaticidade |
| `preset_prot4` | spacefill, cor por cadeia | arquitetura de complexo |
| `preset_prot5` | putty, espessura e cor pelo fator B | flexibilidade |
| `preset_prot6` | all-atom licorice, cor por carga | peptídeos |
| `preset_prot7` | cartoon com camada de solvatação e íons próximos | caixa de MD |
| `preset_prot8` | superfície por carga dentro do volume de solvente | ilustrar o sistema simulado |
| `preset_prot9` | superfície, campo de solvente e as doze arestas da caixa | dimensões da caixa, proporção soluto/solvente |
| `preset_prot10` | superfície translúcida, resíduos de contato opacos e em sticks | onde duas cadeias, ou proteína e ligante, se tocam |

`prot_auto` escolhe entre `preset_prot1` e `preset_prot6` pelo número de
resíduos, com corte em 60.

`preset_prot7` aceita o raio da camada, padrão 4.0. `preset_prot10` aceita o
raio de contato, padrão 4.5, e precisa de duas cadeias ou de um ligante.

`preset_prot9` desenha a caixa a partir do extent do que está carregado, e não
de um registro CRYST1, que frame de dinâmica molecular costuma não ter. As
dimensões vão para o log, prontas para a legenda.

`preset_prot7` e `preset_prot8` respondem a perguntas diferentes: o primeiro
analisa a proteína no contexto do solvente, o segundo ilustra o sistema como um
todo. O segundo não serve para analisar a proteína, porque o volume de solvente
a cobre por construção.

### Cor

```
prot_color ss | chain | charge | hydro | bfactor | rainbow
```

- **ss**: estrutura secundária
- **chain**: uma cor por cadeia
- **charge**: básicos azul, ácidos vermelho, polares claros, apolares amarelo
- **hydro**: gradiente Kyte-Doolittle, sobrescreve a coluna B
- **bfactor**: fator B como está no arquivo
- **rainbow**: gradiente do N para o C terminal

### Solvente e íons

```
prot_water off | shell | spheres | surface | field
prot_ions  off | spheres | vdw | halo | mesh | shell
```

O modo `shell` é o padrão e não existe no módulo de membranas: exibe apenas
água ou íons dentro de um raio da proteína. Numa caixa de MD típica o solvente
de bulk passa de 90% dos átomos e esconde o soluto, enquanto a primeira camada
de solvatação costuma ser o objeto de interesse.

A seleção de água usa `byres`, para não exibir meia molécula quando apenas o
oxigênio cai dentro do raio.

## Iluminação, material e saída

Comandos com prefixo `mv_`, compartilhados pelos dois módulos.

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

A oclusão ambiente fica ligada em todos os presets, menos no `preset_memb6`,
que a desliga para a navegação continuar fluida. Ela não alcança cartoon: o
PyMOL a assa na geometria de esfera e de superfície, então um preset baseado em
cartoon não carrega relevo de contato nenhum. Para figura com relevo, os
caminhos são superfície (`preset_prot3`, `preset_prot9`) ou esferas
(`preset_memb1`, `preset_memb7`).

`mv_grayscale` reescreve cada cor nomeada em uso para a luminância dela, pela
recomendação BT.601, e devolve as originais na saída. O PyMOL não tem ajuste de
escala de cinza, então um gradiente aplicado por `spectrum` continua colorido e
o log diz quantas cores ficaram de fora.

Cada nível ajusta vários parâmetros em conjunto, não um isolado:

**A oclusão ambiente modula o termo ambiente.** Com `ambient` baixo ela está
ligada mas não aparece. Por isso os níveis sobem `ambient` e baixam `direct` ao
mesmo tempo.

**As sombras exigem o oposto:** luz direta forte. Os dois competem pelo mesmo
orçamento de luz, e `soft` e `medium` são os pontos em que convivem.

**A maciez da sombra custa tempo.** O PyMOL não tem raio de fonte de luz: a
penumbra vem de várias luzes projetando sombras sobrepostas. `soft` usa seis
luzes e demora mais que `hard`, que usa uma.

**A ordem importa.** `mv_realism` sobrescreve `mv_shadows`, que sobrescreve
`mv_ao`. Aplique do mais geral para o mais específico.

### Figura de periódico

`mv_paper` difere de `mv_realism` em três pontos deliberados: desliga a sombra
projetada, que vira ruído em figura reduzida; usa projeção ortográfica, porque
perspectiva faz um folheto plano parecer curvo e isso é desonesto numa figura
quantitativa; e restaura a paleta saturada, porque cor saturada separa melhor
as camadas quando a figura cai para a largura de uma coluna.

Ele imprime no log a resolução alvo em pixels e a linha de render pronta.

O teste em escala de cinza não é opcional. Cores de luminância próxima, como o
verde das cabeças contra o laranja das caudas ou o azul das hélices contra o
vermelho das folhas, podem colapsar no mesmo tom. Se ocorrer, diferencie por
claridade, não apenas por matiz.
