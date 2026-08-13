# Plano: separação em módulos e implementação da Tarefa 2

## Contexto

O Momentum hoje é um programa só, o da Tarefa Optativa 1 de PME0100 (campo de
momentos de uma força), com os cinco módulos ocupando a raiz do pacote. A Tarefa
Optativa 2, cujo enunciado está em [tarefa_2.md](tarefa_2.md), pede um programa
diferente: reduzir um sistema de `n` forças aplicadas a um corpo rígido,
calcular resultante, momentos em dois polos, torque em um eixo, invariante
escalar, caracterizar o sistema, achar o eixo central e o momento mínimo, e
desenhar duas figuras por sistema.

As duas tarefas compartilham muita coisa: álgebra vetorial, cena 3D em
Matplotlib e a montagem do PDF com capa, figuras, listagem de código e rodapé. O
objetivo é separar esse tronco comum em `momentum/comum/`, mover a tarefa 1 para
`momentum/tarefa_1/` sem mudar o PDF que ela gera, e implementar a tarefa 2 em
`momentum/tarefa_2/` reaproveitando o comum.

Decisões já tomadas:

| Assunto | Decisão |
| --- | --- |
| Estrutura | `comum/` + `tarefa_1/` + `tarefa_2/` |
| Configuração | dois arquivos, `config_tarefa_1.toml` e `config_tarefa_2.toml` |
| Linha de comando | subcomandos `tarefa1` e `tarefa2`, sem argumento roda as duas, um PDF para cada |
| Alcance da tarefa 2 | classifica nas 4 categorias e ainda detecta sozinho forças concorrentes, coplanares e paralelas |

## Etapa A: separação em módulos

Nenhuma mudança de comportamento. Ao final, `uv run momentum tarefa1` produz o
mesmo documento de hoje, só que em `saida/tarefa_1.pdf`.

### Estrutura final

```
momentum/
├── __init__.py            versão do pacote
├── __main__.py            linha de comando com subcomandos
├── comum/
│   ├── __init__.py
│   ├── vetores.py         álgebra vetorial
│   ├── cena.py            primitivas de figura 3D
│   └── documento.py       esqueleto do PDF
├── tarefa_1/
│   ├── __init__.py
│   ├── config.py  campo.py  desenho.py  relatorio.py
└── tarefa_2/
    ├── __init__.py
    ├── config.py  sistema.py  desenho.py  relatorio.py
```

### `comum/vetores.py`

Recebe, sem alteração, o que hoje está em [momentum/campo.py](momentum/campo.py):
`versor`, `base_do_plano`, `momento` (a convenção `M(O) = (P - O) x F` já é
exatamente a que a tarefa 2 precisa) e `pe_da_perpendicular`.

Ganha uma função nova, generalização de `extremos_da_linha_de_acao`, que a
tarefa 2 usa para desenhar o eixo `Au` e o eixo central:

```python
def segmento_da_reta(ponto, direcao, comprimento) -> tuple[np.ndarray, np.ndarray]
```

### `comum/cena.py`

Extrai de [momentum/desenho.py](momentum/desenho.py) o que hoje está embutido na
função `figura`, que é um bloco de 60 linhas sem nenhum helper reaproveitável:

| Função | Origem |
| --- | --- |
| `Vista` (dataclass: nome, descricao, projecao, elevacao, azimute, zoom) | hoje em `config.py`, sem o campo `axial` |
| `angulos_axiais(n)` | `_angulos_axiais`, sem mudança |
| `cubo_envolvente(pontos, folga)` | `_cubo_envolvente`, sem mudança |
| `criar_eixos(vista)` | novo: `plt.figure`, `add_subplot(projection="3d")`, `set_proj_type`, `view_init` |
| `finalizar(ax, pontos, vista, titulo)` | novo: limites cúbicos, `set_box_aspect`, rótulos x/y/z, ticks, título, `subplots_adjust` |
| `seta(ax, origem, vetor, cor, rotulo=None, ...)` | novo: envolve `ax.quiver` mais o `ax.text` do rótulo |
| `segmento(ax, a, b, cor, ls, lw)` | novo: envolve o idioma `ax.plot(*zip(a, b))` |
| `marcar_ponto(ax, p, cor, rotulo)` | novo: `ax.scatter` mais `ax.text` |
| `legenda(ax, marcas)` | `_legenda`, recebendo a lista de marcas em vez das cores fixas da tarefa 1 |
| `paralelepipedo(ax, canto, dimensoes, cor, alpha)` | novo, para a tarefa 2: as 6 faces com `Poly3DCollection` |

O `matplotlib.use("Agg")` antes de importar o pyplot passa a viver aqui, e essa
ordem precisa ser preservada.

A tarefa 1 estende a vista comum para manter a câmera axial:

```python
@dataclass
class Vista(cena.Vista):
    axial: bool = False  # alinha a câmera com a linha de ação de F
```

### `comum/documento.py`

Recebe de [momentum/relatorio.py](momentum/relatorio.py) tudo que não é texto da
tarefa 1: as constantes `AUTOR`, `ID_USP`, `DISCIPLINA`, `LARGURA_CODIGO`,
`ESTILO_CODIGO`, e as funções `estilos`, `vetor`, `codigo_colorido` e
`paginas_do_codigo`, todas já genéricas hoje.

Passa a expor, além delas:

- `capa(subtitulo, tarefa, parametros, explicacao, estilos)`, com o mesmo layout
  atual (título Momentum, subtítulo, disciplina, autor, seções de parâmetros, de
  explicação e de créditos), recebendo os textos de cada tarefa.
- `pagina_de_figura(figura, titulo, legenda, dpi, estilos)`, desacoplada do
  `cfg.vistas` (hoje `_paginas_das_figuras` casa figuras e vistas por `zip`, o
  que não serve para a tarefa 2, que tem duas figuras diferentes por caso).
- `tabela(cabecalho, linhas, larguras)`, código novo. Não existe nenhum uso de
  `Table` ou `TableStyle` no repositório hoje. Estilo sóbrio: cabeçalho em
  negrito com fundo cinza claro, grade fina, fonte 8, alinhamento à esquerda na
  primeira coluna e à direita nos números.
- `rodape_de(tarefa)`, fábrica que devolve o callback do rodapé com o nome da
  tarefa, já que `TAREFA` deixa de ser constante de módulo.
- `gerar_pdf(tarefa, conteudo, arquivos, caminho)`, que monta o
  `SimpleDocTemplate`, concatena `conteudo + paginas_do_codigo(arquivos)` e
  chama o `build` com o rodapé.

### `momentum/__main__.py`

Argparse com subcomandos. Sem subcomando, roda as duas tarefas em sequência.

```
uv run momentum                      gera os dois PDFs
uv run momentum tarefa1              só a tarefa 1
uv run momentum tarefa2 -c meu.toml -s outro.pdf
```

Cada subcomando mantém `-c/--config` e `-s/--saida`, e o `--version` continua no
parser principal. A resolução do config segue a regra atual: caminho explícito
que não existe é erro, config padrão ausente cai nos valores embutidos.

`_arquivos_do_codigo` precisa mudar de qualquer forma, porque o glob raso
`Path(__file__).parent.glob("*.py")` não enxerga subpacotes. Passa a receber o
nome do subpacote da tarefa e devolve `__init__.py`, `__main__.py`, os arquivos
de `comum/`, os do subpacote pedido e o TOML usado. Assim o apêndice de cada PDF
lista só o programa que gerou aquele documento, sem o código da outra tarefa.

### Renomeações e ajustes

- `config.toml` vira `config_tarefa_1.toml` com `git mv`, preservando o histórico.
- `saida_pdf` padrão da tarefa 1 passa a ser `saida/tarefa_1.pdf`.
- A primeira linha do cabeçalho de licença, hoje "Momentum - visualização do
  campo de momentos de uma força", vira "Momentum - programas das tarefas
  optativas de PME0100 Mecânica I" em todos os módulos.

## Etapa B: implementação da Tarefa 2

### `tarefa_2/sistema.py`, a matemática

Todas as fórmulas em cima de `comum/vetores.py`:

| Saída do enunciado | Cálculo |
| --- | --- |
| a) Resultante | `R = Σ F_i` |
| b) Momento no polo Q | `M_Q = Σ (P_i - Q) x F_i`, somando `vetores.momento(Q, P_i, F_i)` |
| c) Momento no polo A | mesma soma com o polo A, e o programa confere a identidade de transporte `M_A = M_Q + (Q - A) x R` |
| d) Torque no eixo Au | `T = M_A . u`, com `u` normalizado na leitura da configuração |
| e) Invariante escalar | `I = R . M_Q`, e o programa confere que `R . M_A` dá o mesmo |
| f) Caracterização | ver tabela abaixo |
| g) Eixo central e momento mínimo | ponto `E = Q + (R x M_Q) / |R|²`, direção `versor(R)`, `M_min = (I / |R|²) R` |

Caracterização, com as comparações feitas por tolerância:

| `R` | `I` | Sistema |
| --- | --- | --- |
| nulo | momento nulo | nulo |
| nulo | momento não nulo | redutível a um binário |
| não nulo | `I = 0` | redutível a uma única força |
| não nulo | `I ≠ 0` | redutível a força mais binário |

O eixo central existe exatamente quando `R` não é nulo, e a divisão por `|R|²`
fica atrás dessa verificação, que é o ponto onde uma singularidade apareceria.

Detecção da disposição das forças, que o programa resolve sozinho em vez de
aceitar rótulos escritos à mão:

- Paralelas: todas as forças não nulas têm produto vetorial nulo com a primeira.
- Concorrentes: um ponto `X` está na linha de ação de `F_i` quando
  `F_i x (X - P_i) = 0`, ou seja `skew(F_i) X = F_i x P_i`. Empilhar as `n`
  equações em um sistema `3n x 3`, resolver por `np.linalg.lstsq` e aceitar se o
  resíduo for desprezível. O ponto de concorrência entra na tabela.
- Coplanares: existe plano `(n, d)` com `n . F_i = 0` e `n . P_i = d` para todo
  `i`. Montar a matriz com as linhas `[F_i, 0]` e `[P_i, -1]`, tirar o menor
  vetor singular por SVD e aceitar se o menor valor singular for desprezível.

As três condições implicam `I = 0`, então servem também de conferência cruzada
da caracterização.

Tolerância: as comparações com zero usam `atol = tolerancia * escala`, com a
escala tirada dos módulos das forças e das distâncias do próprio caso, para que
a classificação não dependa das unidades escolhidas. `tolerancia` fica na
configuração, com padrão `1e-9`.

A função de entrada é `reduzir(caso, tolerancia) -> Reducao`, uma dataclass com
`R`, `M_Q`, `M_A`, `torque`, `I`, `tipo`, `disposicao`, `eixo_central` e
`momento_minimo`, os dois últimos podendo ser `None`.

### `tarefa_2/config.py`

```toml
tolerancia = 1e-9
saida_pdf = "saida/tarefa_2.pdf"
dpi = 200

[solido]              # paralelepípedo onde ficam os pontos de aplicação
canto = [0.0, 0.0, 0.0]
dimensoes = [4.0, 3.0, 2.0]

[cores]               # forca, resultante, momento, eixo_au, eixo_central, polo, solido

[[vistas]]            # vistas padrão, cada caso pode ter as suas

[[casos]]
nome = "Sistema nulo"
descricao = "..."
forcas = [[...], [...]]
pontos = [[...], [...]]
polo_q = [...]
polo_a = [...]
versor_u = [...]
```

Mesmo padrão da tarefa 1: dataclasses `Caso`, `Solido` e `Config`, conversão
para `np.ndarray` e validação no `__post_init__`, `carregar` com `tomllib`. As
validações são `n >= 1`, mesma quantidade de forças e de pontos, versor `u` não
nulo (normalizado na leitura) e tolerância positiva.

### Os oito casos de exemplo

O enunciado exige provar as 4 categorias, com subexemplos de forças
concorrentes, coplanares e paralelas dentro da categoria c, e verificar `n = 1`.

| # | Caso | O que exercita |
| --- | --- | --- |
| 1 | duas forças opostas na mesma linha de ação | sistema nulo |
| 2 | duas forças opostas em linhas paralelas distintas | binário |
| 3 | uma única força, `n = 1` | ausência de singularidade, eixo central igual à linha de ação |
| 4 | três forças cujas linhas passam por um vértice | concorrentes |
| 5 | três forças sobre uma face do sólido | coplanares |
| 6 | três forças verticais em pontos diferentes | paralelas |
| 7 | um binário de momento perpendicular a uma terceira força | única força no caso geral, sem ser concorrente, coplanar nem paralelo |
| 8 | três forças em arestas reversas do sólido | força mais binário, o torsor geral |

Os pontos de aplicação ficam em vértices, arestas e faces do paralelepípedo,
como o enunciado sugere. O caso 7 é construído a partir da observação de que um
binário com momento perpendicular à força restante mantém `I = 0` sem tornar o
sistema concorrente, coplanar ou paralelo.

### `tarefa_2/desenho.py`

Duas figuras por caso, ambas montadas com as primitivas de `comum/cena.py`:

- `figura_reducao` (item h): Oxyz, o paralelepípedo em traço leve, as forças
  `F_i` como setas nos pontos `P_i` rotulados, os polos `Q` e `A`, o eixo `Au`
  como reta tracejada passando por `A`, a resultante `R` desenhada em `Q` quando
  não nula, e os momentos `M_Q` e `M_A` quando não nulos.
- `figura_eixo_central` (item i), só quando o eixo central existe: Oxyz, o
  sólido, as forças, os pontos, o polo `Q`, o momento `M_Q`, o eixo central em
  destaque, e sobre ele a resultante `R` e o momento mínimo `M_E`.

Cada figura usa `cubo_envolvente` alimentado com todos os pontos desenhados,
inclusive os 8 vértices do sólido e as pontas das setas, para a caixa continuar
cúbica. As vistas vêm da configuração, com ângulos escolhidos caso a caso para a
figura ficar legível, como o enunciado pede.

### `tarefa_2/relatorio.py`

Documento montado com `comum/documento.py`:

1. Capa com identificação, explicação do que o programa calcula e uma tabela
   resumo dos oito casos com a classificação de cada um, que mostra de relance
   que as 4 categorias estão cobertas.
2. Para cada caso, uma página com a descrição, a tabela de entrada (`i`, `F_i`,
   `P_i`, e abaixo `Q`, `A`, `u`) e a tabela de resultados (`R`, `M_Q`, `M_A`,
   torque em `Au`, `I`, caracterização, disposição detectada, eixo central e
   momento mínimo), seguida das figuras, uma por página.
3. O código-fonte, pelo mesmo `paginas_do_codigo` de hoje.

### Infraestrutura

- `pyproject.toml`: versão para `2.0.0`, o que dispara a release no workflow, e
  descrição atualizada para as duas tarefas.
- [.github/workflows/momentum.yml](.github/workflows/momentum.yml): o passo de
  execução continua `uv run momentum`, o artefato passa a apontar para `saida/`
  com os dois PDFs, e o `gh release create` recebe os dois arquivos.
- [README.md](README.md): tabela de estrutura, seção de uso com os subcomandos,
  seção de configuração com os dois TOMLs, e uma seção sobre a tarefa 2.
- [AGENTS.md](AGENTS.md): remover a nota de que o código da tarefa 1 ainda ocupa
  a raiz do pacote e descrever a divisão em `comum/`, `tarefa_1/` e `tarefa_2/`.

## Verificação

Antes de começar, guardar o PDF atual como referência:

```sh
uv run momentum && cp saida/momentum.pdf /tmp/referencia.pdf
```

Depois da etapa A, o PDF da tarefa 1 deve ser equivalente ao de referência,
mesma contagem de páginas e mesmas figuras:

```sh
uv run momentum tarefa1
pdfinfo saida/tarefa_1.pdf | grep Pages   # comparar com o de referência
```

Comparação byte a byte não serve, porque o PDF carrega data de geração.

Depois da etapa B:

```sh
uv run momentum              # gera os dois PDFs sem erro
uv run momentum tarefa2
```

Conferências numéricas, rodadas sobre os casos configurados:

- `M_A` calculado pela soma direta bate com `M_Q + (Q - A) x R`.
- `R . M_Q` bate com `R . M_A`, isto é, o invariante independe do polo.
- No eixo central, `M(E)` é paralelo a `R` e `|M(E)| <= |M(Q)|`.
- Caso 1: tudo nulo, classificado como nulo, sem divisão por zero.
- Caso 3 (`n = 1`): `I = 0`, eixo central coincide com a linha de ação de `F_1`
  e o momento mínimo é nulo.
- Casos 4, 5 e 6: a disposição detectada é a esperada e `I = 0` em todos.
- Caso 8: `I ≠ 0` e o momento mínimo é paralelo a `R`.

Essas conferências entram como um passo do próprio `reduzir`, levantando
`ValueError` quando uma identidade falha, de modo que uma configuração errada
apareça na execução em vez de virar número errado na tabela.

## Commits

Seguindo o AGENTS.md, um commit por arquivo criado ou alterado, conventional
commits sem escopo e sem `Co-authored-by`. Ordem sugerida:

Etapa A: `refactor:` para cada módulo movido para `comum/` e para `tarefa_1/`,
depois `refactor:` da linha de comando, `build:` da renomeação do TOML e
`ci:`/`docs:` dos ajustes de saída.

Etapa B: `feat:` para `config.py`, `sistema.py`, `desenho.py` e `relatorio.py`
da tarefa 2, `feat:` para o `config_tarefa_2.toml` com os casos, e por fim
`build:`, `ci:` e `docs:` para versão, workflow, README e AGENTS.md.
