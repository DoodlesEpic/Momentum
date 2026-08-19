# AGENTS.md

Instruções para agentes de IA que trabalham neste repositório. Elas resumem o
que foi pedido nos prompts que originaram o projeto.

## O projeto

O Momentum é um programa pequeno em Python para as tarefas optativas de PME0100
Mecânica I (2026), da Engenharia de Computação da Escola Politécnica da USP.
Cada tarefa é um módulo dentro do pacote `momentum`, com o seu próprio enunciado
na raiz do repositório.

### Tarefa 1

Visualiza o campo de momentos de uma força. O enunciado está em
[tarefa_1.md](tarefa_1.md) e manda desenhar, para uma força `F` aplicada em um
ponto `P`, a força e sua linha de ação em vermelho, os vetores `M(O)` em preto,
as retas tracejadas verdes de cada ponto `O` até o ponto `Q` (pé da perpendicular
sobre a linha de ação) e as retas tracejadas azuis da extremidade de `M(O)` até
o mesmo `Q`. Os pontos `O` ficam em planos normais à linha de ação, espaçados
igualmente, e em cada plano as direções são separadas por 60 graus.

### Tarefa 2

Reduz sistemas de `n` forças aplicadas a um corpo rígido. O enunciado está em
[tarefa_2.md](tarefa_2.md) e calcula a resultante, os momentos em dois polos, o
torque em um eixo, o invariante escalar, a caracterização do sistema e, quando
existirem, o eixo central e o momento mínimo, além das figuras e da tabela de
resultados.

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

- Cada tarefa gera um PDF com a capa, as figuras e o código-fonte.
- Na tarefa 1 são três visualizações, uma perspectiva isométrica, uma projeção
  ortográfica e uma terceira de outra maneira, hoje a vista axial alinhada com a
  linha de ação da força.
- O PDF credita Eduardo Lima Moraes, ID USP 16802140, e também o Claude.
- Tudo que muda a visualização fica em `config_tarefa_1.toml` ou
  `config_tarefa_2.toml`, sem precisar editar código.

## Automação

O fluxo do GitHub Actions em
[.github/workflows/momentum.yml](.github/workflows/momentum.yml) executa o
programa a cada push na `main`, guarda o PDF como artefato e publica uma release
com o código e o PDF sempre que a versão do `pyproject.toml` muda.

## Releases

Sempre que uma nova release for publicada no GitHub, use a CLI `gh` para editar
as notas de lançamento da tag correspondente, resumindo em português do Brasil as
principais novidades, melhorias ou correções da versão.

