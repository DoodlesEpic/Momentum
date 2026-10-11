# Plano: implementação da Tarefa 5

## Contexto

A Tarefa Optativa 5, cujo enunciado está em [tarefa_5.md](tarefa_5.md), pede
dois programas de cinemática do ponto e geometria de curvas:

1. A hipociclóide traçada por um ponto `P` de um disco de raio `r` que rola sem
   escorregar dentro de um aro de raio `R > r`, com animação, instantâneos,
   exemplos para quatro razões `R/r`, raio de curvatura, versores tangente e
   normal principal, e velocidade e aceleração de `P` para a lei horária
   `θ(t) = ω t`, com `ω = π/60 rad/s`.
2. A cúbica reversa `x = λ`, `y = λ²`, `z = λ³`, com o raio de curvatura e o
   triedro de Frenet em três pontos.

O projeto já separa o tronco comum em `momentum/comum/` e cada tarefa em um
subpacote. A Tarefa 5 entra como `momentum/tarefa_5/`, reaproveitando
`comum/vetores.py`, `comum/cena.py` e `comum/documento.py`.

Decisões:

| Assunto | Decisão |
| --- | --- |
| Estrutura | subpacote `tarefa_5/` com um módulo de cálculo para cada programa |
| Configuração | `config_tarefa_5.toml`, com as seções `[hipocicloide]` e `[cubica]` |
| Linha de comando | subcomando `tarefa5`, e sem subcomando o programa gera as três tarefas |
| Saídas | um PDF com as duas partes e um GIF com a animação do item 1.2 |
| Animação | `matplotlib.animation` com o `PillowWriter`, sem dependência nova, já que o Pillow vem com o matplotlib |
| Ângulos na configuração | em graus, convertidos para radianos na leitura |
| Exemplo padrão | `R = 3r`, o mesmo do exemplo 17 do capítulo 3 das notas de aula |
| Notação | a das notas de aula: `v = v τ`, `a = a_τ τ + a_n n`, `b = τ ∧ n` |
| Fontes do PDF | DejaVu, que vem com o matplotlib e tem as letras gregas |

## Parte 1: hipociclóide

### `tarefa_5/hipocicloide.py`

Com `k = (R - r) / r`, a posição e as derivadas em relação a `θ` são:

| Grandeza | Expressão |
| --- | --- |
| `P(θ)` | `((R - r) cos θ + r cos kθ, (R - r) sin θ - r sin kθ)` |
| `P'(θ)` | `(R - r) (-sin θ - sin kθ, cos θ - cos kθ)` |
| `P''(θ)` | `(R - r) (-cos θ - k cos kθ, -sin θ + k sin kθ)` |
| centro do disco | `C(θ) = (R - r) (cos θ, sin θ)` |
| ponto de contato | `T(θ) = R (cos θ, sin θ)` |

Raio de curvatura e versores, calculados numericamente a partir das derivadas:

- `ρ = |P'|³ / |P' x P''|`, com o produto vetorial no plano tomado como escalar.
- `τ = P' / |P'|`.
- `b = (P' ∧ P'') / |P' ∧ P''| = ±k` e `n = b ∧ τ`, como no capítulo 3 das notas
  de aula. O resultado aponta para o centro de curvatura.
- centro de curvatura `P + ρ n`.

O programa confere o resultado numérico com a forma fechada
`ρ = 4 r (R - r) |sin(Rθ / 2r)| / |R - 2r|`, levantando `ValueError` se as duas
divergirem.

Singularidades:

- Nas cúspides, `sin(Rθ / 2r) = 0`, a velocidade se anula e `τ` não existe. As
  posições escolhidas para os itens 1.5, 1.6 e 1.7 não podem cair sobre uma
  cúspide, e a configuração é rejeitada com uma mensagem clara.
- Com `R = 2r` a curva degenera em um segmento de reta e o raio de curvatura é
  infinito. Esse caso só é aceito nos exemplos do item 1.4.

Fechamento da curva: se `R/r = p/q` em fração irredutível, a curva fecha depois
de `q` voltas do centro do disco. O número de voltas vem de
`Fraction(R/r).limit_denominator(voltas_maximas)`, de modo que razões
irracionais desenham no máximo `voltas_maximas` voltas.

Cinemática do item 1.7, com `θ = ω t` e `θ'' = 0`:

| Forma | Velocidade | Aceleração |
| --- | --- | --- |
| cartesiana | `v = ω P'(θ)` | `a = ω² P''(θ)` |
| intrínseca | `v = v τ`, com `v = |v|` | `a = a_τ τ + a_n n` |

As componentes intrínsecas saem de `a_τ = a . τ` e `a_n = v² / ρ = a . n`.

### Figuras da parte 1

| Item | Figura |
| --- | --- |
| 1.1 | aro, curva completa e cúspides |
| 1.2 | GIF com o disco rolando, o raio `CP`, o ponto de contato e o traço de `P` |
| 1.3 | grade com seis instantâneos do mesmo desenho da animação |
| 1.4 | grade 2 x 2 com as quatro razões `R/r` da configuração |
| 1.5 | curva, pontos escolhidos e círculos osculadores com seus centros |
| 1.6 | curva com os versores `τ` e `n` nos pontos escolhidos |
| 1.7 | curva com os vetores `v` e `a` nos três instantes |

Os desenhos são planos, com `matplotlib` e eixos de mesma escala. A animação e
os instantâneos usam a mesma função de desenho do estado do rolamento, para
que o PDF mostre exatamente quadros da animação.

## Parte 2: cúbica reversa

### `tarefa_5/cubica.py`

| Grandeza | Expressão |
| --- | --- |
| `r(λ)` | `(λ, λ², λ³)` |
| `r'(λ)` | `(1, 2λ, 3λ²)` |
| `r''(λ)` | `(0, 2, 6λ)` |
| `ρ` | `|r'|³ / |r' x r''|` |
| `τ` | `r' / |r'|` |
| `b` | `(r' x r'') / |r' x r''|` |
| `n` | `b x τ` |

Como `r' x r'' = (6λ², -6λ, 2)` nunca se anula, a curvatura existe em todo
ponto. O programa ainda exige `λ ≠ 0` nos pontos escolhidos, como pede o
enunciado, e confere que o triedro é ortonormal e dextrogiro.

A figura é uma cena 3D montada com `comum/cena.py`: a curva, os três pontos e
os três versores de cada triedro, com a vista definida na configuração.

## Configuração

```toml
saida_pdf = "saida/tarefa_5.pdf"
saida_animacao = "saida/tarefa_5_hipocicloide.gif"
dpi = 200

[hipocicloide]
raio_aro = 3.0
raio_disco = 1.0
razoes = [3.0, 4.0, 6.0, 2.5]
instantaneos = [...]          # θ em graus
posicoes_curvatura = [...]    # θ em graus
posicoes_versores = [...]     # θ em graus
omega = 0.05235987755982988   # π/60 rad/s
instantes = [10.0, 20.0, 35.0]

[cubica]
lambda_minimo = -1.3
lambda_maximo = 1.3
parametros = [-1.0, 0.5, 1.2]

[cores]

[vista]
```

Mesmo padrão das outras tarefas: dataclasses com validação no
`__post_init__` e `carregar` com `tomllib`.

## Relatório

1. Capa com os parâmetros das duas partes.
2. Parte 1: página com as tabelas de raio de curvatura, versores e cinemática
   cartesiana e intrínseca, seguida das figuras, uma por página. O texto indica
   o arquivo GIF da animação.
3. Parte 2: tabela com `λ`, `P`, `ρ`, `τ`, `n` e `b`, seguida da figura 3D.
4. O código-fonte de cálculo e a configuração.

## Infraestrutura

- `__main__.py`: subcomando `tarefa5` e listagem dos dois módulos de cálculo.
- Workflow: a release passa a anexar o PDF e o GIF da Tarefa 5.
- README e AGENTS.md: descrição da tarefa, estrutura, uso e configuração.
- Versão `3.0.0`, seguindo a Tarefa 2, que subiu a versão principal.

## Verificação

```sh
uv run momentum tarefa5
uv run momentum
```

- O PDF e o GIF são gerados sem erro.
- `ρ` numérico bate com a forma fechada da hipociclóide e da cúbica.
- Na cúbica, o triedro é ortonormal e dextrogiro.
- No item 1.7, `a_n = v² / ρ`.
- Com `R = 3r` e `ω = π/30`, o instante `t = 15 s` reproduz o exemplo 17 das
  notas de aula: `τ = (-√2/2, √2/2)`, `n = (√2/2, √2/2)`,
  `a_τ = -3√2 (π/30)² r` e `a_n = √2 (π/30)² r`.

## Commits

Um commit por arquivo criado ou alterado, conventional commits sem escopo e sem
`Co-authored-by`. Ordem: `docs:` do enunciado e do plano, `feat:` de cada módulo
de `tarefa_5/` e da configuração, `feat:` da linha de comando, `ci:` do
workflow, `docs:` do README e do AGENTS.md e `build:` da versão e do lockfile.
