# AGENTS.md

Instruções para agentes de IA que trabalham neste repositório. Elas resumem o
que foi pedido nos prompts que originaram o projeto.

## O projeto

O Momentum é um programa pequeno em Python para as tarefas optativas de PME0100
Mecânica I (2026), da Engenharia de Computação da Escola Politécnica da USP.
Cada tarefa é um subpacote dentro de `momentum`, com o enunciado em
`enunciados/`, a configuração em `config/` e o plano de implementação em
`planos/`. O código compartilhado fica em `momentum/comum/`. A numeração segue a
da disciplina, por isso não existem tarefas 3 e 4 no repositório.

### Tarefa 1

Visualiza o campo de momentos de uma força. O enunciado está em
[enunciados/tarefa_1.md](enunciados/tarefa_1.md) e manda desenhar, para uma força `F` aplicada em um
ponto `P`, a força e sua linha de ação em vermelho, os vetores `M(O)` em preto,
as retas tracejadas verdes de cada ponto `O` até o ponto `Q` (pé da perpendicular
sobre a linha de ação) e as retas tracejadas azuis da extremidade de `M(O)` até
o mesmo `Q`. Os pontos `O` ficam em planos normais à linha de ação, espaçados
igualmente, e em cada plano as direções são separadas por 60 graus.

### Tarefa 2

Reduz sistemas de `n` forças aplicadas a um corpo rígido. O enunciado está em
[enunciados/tarefa_2.md](enunciados/tarefa_2.md) e calcula a resultante, os momentos em dois polos, o
torque em um eixo, o invariante escalar, a caracterização do sistema e, quando
existirem, o eixo central e o momento mínimo, além das figuras e da tabela de
resultados.

### Tarefa 5

Estuda a geometria e a cinemática de curvas. O enunciado está em
[enunciados/tarefa_5.md](enunciados/tarefa_5.md) e tem duas partes. A primeira
traça a hipociclóide, grava um vídeo da sua geração de um disco que rola dentro de um aro, mostra
instantâneos e quatro razões `R/r`, e calcula o raio de curvatura, os versores
tangente e normal principal e a velocidade e a aceleração de `P` nas formas
cartesiana e intrínseca. A segunda calcula o raio de curvatura e o triedro de
Frenet da curva `(λ, λ², λ³)` em três pontos. O exemplo padrão, `R = 3r`, e a
notação seguem o capítulo 3 das notas de aula.

## Idioma e escrita

- Código, comentários, documentação e mensagens de commit em português do Brasil.
- Nada de travessões nem de pontos e vírgulas em textos e comentários. Use
  vírgulas, pontos ou frases separadas.
- Nada de negrito no texto do README.
- Cada função e cada classe tem, logo acima, um comentário de uma ou duas linhas
  dizendo o que faz e como faz, escrito para quem tem dificuldade em Mecânica I
  ou ainda sabe pouco de programação. Esses comentários substituem as docstrings.
  Fora isso, comentários só onde explicam uma decisão que o código não mostra.

## Commits

- Um commit para cada arquivo criado ou alteração realizada, feitos ao longo do
  trabalho e não todos no final.
- Conventional commits sem escopo entre parênteses, por exemplo
  `feat: adiciona leitura da configuração em TOML`.
- Nada de `Co-authored-by`, `Signed-off-by`, `Generated with` ou qualquer outra
  linha de créditos ou atribuição a ferramentas nas mensagens de commit. Os
  créditos ficam no README e, nas tarefas 1 e 2, no PDF.
- O autor e o committer são sempre a identidade git indicada pelo dono do
  repositório, e não a configuração global da máquina nem a de uma ferramenta.

## Código

- Python simples e sucinto, condizente com um calouro de Engenharia de
  Computação da Poli USP, sem abstrações que a tarefa não peça.
- Dependências gerenciadas com o uv, mantendo o `uv.lock` versionado e o
  `requirements.txt` gerado por `uv export`.
- Prefira as bibliotecas mais aptas e populares para cada finalidade, sempre nas
  versões mais recentes. Hoje o projeto usa numpy, matplotlib, reportlab e
  pygments.
- Quando houver material de aula do professor, siga a sua notação e os seus
  procedimentos de cálculo e confira os resultados com os exemplos resolvidos.
- Licença GNU GPL v3 ou posterior, com cabeçalho curto em cada módulo.

## Comportamento do programa

- Cada tarefa gera um PDF com a capa, as figuras e o código-fonte. A tarefa 5
  também grava o vídeo da hipociclóide em MP4 e o anexa ao PDF.
- Na tarefa 1 são três visualizações, uma perspectiva isométrica, uma projeção
  ortográfica e uma terceira de outra maneira, hoje a vista axial alinhada com a
  linha de ação da força.
- O PDF credita Eduardo Lima Moraes, ID USP 16802140. Os PDFs das tarefas 1 e 2
  também creditam o Claude, mas a partir da tarefa 5 o professor dispensou esse
  crédito, e ele não deve aparecer nas entregas novas.
- Os números no PDF têm no máximo três casas decimais, para ficarem legíveis.
- Tudo que muda a visualização fica no TOML da tarefa, em `config/`, sem
  precisar editar código.
- Os relatórios usam a fonte DejaVu, que vem com o matplotlib, porque as fontes
  padrão do PDF não têm letras gregas.

## Automação

O fluxo do GitHub Actions em
[.github/workflows/momentum.yml](.github/workflows/momentum.yml) executa o
programa a cada push na `main`, guarda os PDFs e o vídeo como artefatos e
publica uma release com o código, os PDFs e o vídeo sempre que a versão do
`pyproject.toml` muda.

## Releases

Sempre que uma nova release for publicada no GitHub, use a CLI `gh` para editar
as notas de lançamento da tag correspondente, resumindo em português do Brasil as
principais novidades, melhorias ou correções da versão.

