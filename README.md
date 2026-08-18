# Momentum

Programas das tarefas optativas de PME0100 Mecânica I (2026), da Engenharia de
Computação da Escola Politécnica da USP.

O projeto gera um PDF por tarefa. Cada relatório contém capa, resultados,
figuras tridimensionais e a listagem do código de cálculo e configuração.

## Tarefas

### Tarefa 1

A [Tarefa 1](tarefa_1.md) visualiza o campo de momentos de uma força
`F = (Fx, Fy, Fz)` aplicada em um ponto `P = (Px, Py, Pz)`. Para cada ponto
`O`, o momento é:

```
M(O) = (P - O) x F
```

As figuras mostram a força e sua linha de ação em vermelho, os momentos em
preto, os segmentos de `O` ao pé da perpendicular em verde tracejado e os
segmentos entre esse pé e a ponta de cada momento em azul tracejado.

### Tarefa 2

A [Tarefa 2](tarefa_2.md) reduz sistemas de `n` forças aplicadas a um corpo
rígido. Para cada caso, o programa calcula a resultante `R`, os momentos nos
polos `Q` e `A`, o torque no eixo `Au`, o invariante escalar `I`, a
caracterização do sistema, o eixo central e o momento mínimo quando existem.

As quatro categorias do enunciado são classificadas por tolerância numérica:

| Resultante | Invariante | Sistema |
| --- | --- | --- |
| nula | momento nulo | nulo |
| nula | momento não nulo | redutível a um binário |
| não nula | nulo | redutível a uma única força |
| não nula | não nulo | redutível a força mais binário |

O relatório padrão traz oito exemplos. Eles cobrem as quatro categorias e,
entre os sistemas redutíveis a uma única força, os casos de uma força, linhas
concorrentes, forças coplanares, forças paralelas e o caso geral. As forças e
os pontos de aplicação são mostrados em um paralelepípedo configurável.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `momentum/comum/vetores.py` | álgebra vetorial e geometria de retas |
| `momentum/comum/cena.py` | primitivas para as cenas 3D |
| `momentum/comum/documento.py` | elementos compartilhados dos PDFs |
| `momentum/tarefa_1/` | campo de momentos de uma força |
| `momentum/tarefa_2/` | redução de sistemas de forças |
| `config_tarefa_1.toml` | parâmetros e vistas da Tarefa 1 |
| `config_tarefa_2.toml` | casos, sólido, escalas e vistas da Tarefa 2 |

## Instalação

As dependências são gerenciadas com [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

Alternativamente, com `pip` e o `requirements.txt` gerado por `uv export`:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```sh
uv run momentum
uv run momentum tarefa1
uv run momentum tarefa2
uv run momentum tarefa1 --config outro.toml --saida relatorio.pdf
uv run momentum tarefa2 -c outro.toml -s relatorio.pdf
```

Sem subcomando, são gerados `saida/tarefa_1.pdf` e `saida/tarefa_2.pdf`.
Com apenas um subcomando, é gerado o PDF da tarefa escolhida. Sem o `uv`, com
o ambiente virtual ativado, use `python -m momentum` da mesma forma.

## Configuração

Todos os parâmetros que alteram cálculos ou visualizações estão nos arquivos
TOML. Um caminho fornecido com `--config` deve existir. Se o arquivo padrão não
existir, o programa usa os valores embutidos nos módulos de configuração.

Na Tarefa 2, cada bloco `[[casos]]` contém as forças `forcas`, seus pontos de
aplicação `pontos`, os polos `polo_q` e `polo_a` e o versor `versor_u`. O
programa normaliza `versor_u`, verifica as dimensões de todos os vetores e
confere as identidades de transporte do momento, invariância escalar e momento
mínimo antes de gerar o PDF.

## Automação

O fluxo em [.github/workflows/momentum.yml](.github/workflows/momentum.yml)
executa o programa a cada push na branch `main` e também sob demanda. Os dois
PDFs são guardados como artefatos. Quando a versão declarada no
`pyproject.toml` ainda não tem uma release, o fluxo publica uma release com o
código-fonte e os dois relatórios.

## Licença

Distribuído sob a GNU General Public License v3.0 ou posterior. O texto
completo está em [LICENSE](LICENSE).

## Créditos

Eduardo Lima Moraes, ID USP 16802140.

Desenvolvido com auxílio do Claude (Anthropic).
