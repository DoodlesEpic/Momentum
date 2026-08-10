# AGENTS.md

Instruções para agentes de IA que trabalham neste repositório. Elas resumem o
que foi pedido nos prompts que originaram o projeto.

## O projeto

O Momentum é um programa pequeno em Python que visualiza o campo de momentos de
uma força. Ele foi feito para a Tarefa Optativa 1 de PME0100 Mecânica I (2026),
da Engenharia de Computação da Escola Politécnica da USP. O enunciado está em
[tarefa.md](tarefa.md) e manda desenhar, para uma força `F` aplicada em um ponto
`P`, a força e sua linha de ação em vermelho, os vetores `M(O)` em preto, as
retas tracejadas verdes de cada ponto `O` até o ponto `Q` (pé da perpendicular
sobre a linha de ação) e as retas tracejadas azuis da extremidade de `M(O)` até
o mesmo `Q`. Os pontos `O` ficam em planos normais à linha de ação, espaçados
igualmente, e em cada plano as direções são separadas por 60 graus.

## Idioma e escrita

- Código, comentários, documentação e mensagens de commit em português do Brasil.
- Nada de travessões nem de pontos e vírgulas em textos e comentários. Use
  vírgulas, pontos ou frases separadas.
- Nada de negrito no texto do README.
- Comentários pontuais, apenas onde explicam uma decisão que o código não mostra.

## Commits

- Um commit para cada arquivo criado ou alteração realizada.
- Conventional commits sem escopo entre parênteses, por exemplo
  `feat: adiciona leitura da configuração em TOML`.
- Sem linha de `Co-authored-by`. Os créditos ficam no README e no PDF.

## Código

- Python, simples e sucinto, sem abstrações que a tarefa não peça.
- Dependências gerenciadas com o uv, mantendo o `uv.lock` versionado e o
  `requirements.txt` gerado por `uv export`.
- Prefira as bibliotecas mais aptas e populares para cada finalidade. Hoje o
  projeto usa numpy, matplotlib, reportlab e pygments.
- Licença GNU GPL v3 ou posterior, com cabeçalho curto em cada módulo.

## Comportamento do programa

- Rodar o programa gera um PDF com a capa, três visualizações e o código-fonte.
- As três visualizações são uma perspectiva isométrica, uma projeção ortográfica
  e uma terceira de outra maneira, hoje a vista axial alinhada com a linha de
  ação da força.
- O PDF credita Eduardo Lima Moraes, ID USP 16802140, e também o Claude.
- Tudo que muda a visualização fica no `config.toml`, sem precisar editar código.

## Automação

O fluxo do GitHub Actions em
[.github/workflows/momentum.yml](.github/workflows/momentum.yml) executa o
programa a cada push na `main`, guarda o PDF como artefato e publica uma release
com o código e o PDF sempre que a versão do `pyproject.toml` muda.
