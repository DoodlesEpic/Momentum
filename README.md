# Momentum

Programas das tarefas optativas de PME0100 Mecânica I (2026), da Engenharia de
Computação da Escola Politécnica da USP.

O projeto gera um PDF por tarefa. Cada relatório contém capa, resultados,
figuras e a listagem do código de cálculo e configuração. A Tarefa 5 também
gera uma animação em GIF.

## Tarefas

### Tarefa 1

A [Tarefa 1](enunciados/tarefa_1.md) visualiza o campo de momentos de uma força
`F = (Fx, Fy, Fz)` aplicada em um ponto `P = (Px, Py, Pz)`. Para cada ponto
`O`, o momento é:

```
M(O) = (P - O) x F
```

As figuras mostram a força e sua linha de ação em vermelho, os momentos em
preto, os segmentos de `O` ao pé da perpendicular em verde tracejado e os
segmentos entre esse pé e a ponta de cada momento em azul tracejado.

### Tarefa 2

A [Tarefa 2](enunciados/tarefa_2.md) reduz sistemas de `n` forças aplicadas a um corpo
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

### Tarefa 5

A [Tarefa 5](enunciados/tarefa_5.md) tem duas partes. A primeira traça a
hipociclóide gerada por um ponto `P` de um disco de raio `r` que rola sem
escorregar dentro de um aro de raio `R`:

```
x = (R - r) cos θ + r cos(((R - r) / r) θ)
y = (R - r) sin θ - r sin(((R - r) / r) θ)
```

O programa anima a geração da curva, mostra instantâneos, desenha exemplos
para quatro razões `R/r` e calcula o raio de curvatura, os versores tangente e
normal principal e, com a lei horária `θ(t) = ω t` e `ω = π/60 rad/s`, a
velocidade e a aceleração de `P` nas formas cartesiana e intrínseca. O exemplo
padrão usa `R = 3r`, o mesmo do capítulo 3 das notas de aula.

A segunda parte calcula o raio de curvatura e o triedro de Frenet `τ`, `n`, `b`
da curva `(λ, λ², λ³)` em três pontos, com `b = (r' ∧ r'') / |r' ∧ r''|` e
`n = b ∧ τ`.

## Estrutura

| Caminho | Conteúdo |
| --- | --- |
| `momentum/comum/vetores.py` | álgebra vetorial e geometria de retas |
| `momentum/comum/cena.py` | primitivas para as cenas 3D |
| `momentum/comum/documento.py` | elementos compartilhados dos PDFs |
| `momentum/tarefa_1/` | campo de momentos de uma força |
| `momentum/tarefa_2/` | redução de sistemas de forças |
| `momentum/tarefa_5/` | hipociclóide e triedro de Frenet |
| `config/` | um arquivo TOML de configuração por tarefa |
| `enunciados/` | enunciados das tarefas |
| `planos/` | planos de implementação das tarefas |

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
uv run momentum tarefa5
uv run momentum tarefa1 --config outro.toml --saida relatorio.pdf
uv run momentum tarefa2 -c outro.toml -s relatorio.pdf
```

Sem subcomando, são gerados `saida/tarefa_1.pdf`, `saida/tarefa_2.pdf`,
`saida/tarefa_5.pdf` e a animação `saida/tarefa_5_hipocicloide.gif`.
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

Na Tarefa 5, a seção `[hipocicloide]` define `R`, `r`, as razões dos exemplos,
os ângulos dos instantâneos e dos pontos analisados, em graus, `ω`, os instantes
e a animação. A seção `[cubica]` define o trecho desenhado da curva e os três
valores de `λ`, que devem ser diferentes de zero. Posições sobre uma cúspide da
hipociclóide são rejeitadas, porque nelas a velocidade se anula e os versores
tangente e normal não existem.

## Automação

O fluxo em [.github/workflows/momentum.yml](.github/workflows/momentum.yml)
executa o programa a cada push na branch `main` e também sob demanda. Os PDFs
e a animação são guardados como artefatos. Quando a versão declarada no
`pyproject.toml` ainda não tem uma release, o fluxo publica uma release com o
código-fonte, os relatórios e a animação.

## Licença

Distribuído sob a GNU General Public License v3.0 ou posterior. O texto
completo está em [LICENSE](LICENSE).

## Créditos

Eduardo Lima Moraes, ID USP 16802140.

Desenvolvido com auxílio do Claude (Anthropic).
