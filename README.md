# Momentum

Visualização do campo de momentos de uma força no espaço.

## Introdução

O Momentum é um pequeno programa em Python que desenha o campo de momentos
de uma força `F = (Fx, Fy, Fz)` aplicada em um ponto `P = (Px, Py, Pz)`.

Para cada ponto `O` do espaço, o momento da força em relação a `O` é

```
M(O) = (P - O) x F
```

Como o momento não se altera ao deslocar o ponto de aplicação ao longo da linha
de ação de `F`, o campo depende apenas da distância de `O` até essa linha. O
programa explora essa propriedade amostrando os pontos `O` em planos normais à
linha de ação e igualmente espaçados, e desenhando, em cada plano, direções
separadas por ângulos iguais (60° por padrão).

Este é o trabalho da Tarefa Optativa 1 da disciplina PME0100 Mecânica I
(2026), da Engenharia de Computação da Escola Politécnica da USP.

## Visão Geral

Cada figura gerada mostra:

| Elemento | Cor / traço |
| --- | --- |
| Força `F` e sua linha de ação | vermelho |
| Vetores momento `M(O)` | preto |
| Segmentos de `O` até `Q` (pé da perpendicular à linha de ação) | verde tracejado |
| Segmentos da extremidade de `M(O)` até `Q` | azul tracejado |

O programa produz um único arquivo PDF contendo:

1. a capa com os parâmetros usados e os créditos
2. três visualizações do campo, em perspectiva isométrica, em projeção
   ortográfica e em vista axial (câmera alinhada com a linha de ação de `F`)
3. o código-fonte completo do programa

### Estrutura

| Arquivo | Conteúdo |
| --- | --- |
| `momentum/config.py` | leitura e validação da configuração |
| `momentum/campo.py` | geometria e cálculo do campo de momentos |
| `momentum/desenho.py` | construção das figuras com Matplotlib |
| `momentum/relatorio.py` | montagem do PDF com ReportLab |
| `momentum/__main__.py` | linha de comando |
| `config.toml` | parâmetros da simulação e da visualização |

### Instalação

As dependências são gerenciadas com [uv](https://docs.astral.sh/uv/):

```sh
uv sync
```

Alternativamente, com `pip` e o `requirements.txt` (gerado a partir do `uv`):

```sh
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
```

### Uso

```sh
uv run momentum                       # gera saida/momentum.pdf
uv run momentum --config outro.toml   # usa outra configuração
uv run momentum --saida relatorio.pdf # escolhe o arquivo de saída
```

Sem o `uv`, com o ambiente virtual ativado, use `python -m momentum` com as
mesmas opções.

### Configuração

Todos os parâmetros ficam em `config.toml`: a força, o ponto de aplicação, a
quantidade e o espaçamento dos planos, os raios e o passo angular das direções,
as escalas de desenho, as cores e a lista de vistas. Editar esse arquivo é
suficiente para alterar a visualização, sem nenhuma mudança no código.

## Licença

Distribuído sob a GNU General Public License v3.0 ou posterior. O texto
completo está em [LICENSE](LICENSE).

## Créditos

Eduardo Lima Moraes, ID USP 16802140.

Desenvolvido com auxílio do Claude (Anthropic).
