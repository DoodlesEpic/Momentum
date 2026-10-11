# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Montagem do relatório PDF da Tarefa 5."""

from pathlib import Path

import numpy as np
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer

from ..comum import documento
from . import desenho
from .config import Config
from .cubica import Triedro
from .hipocicloide import Cinematica, Curvatura

TAREFA = "Tarefa Optativa 5"


# Escreve um número com no máximo três casas decimais, sem zeros sobrando à direita.
# Somar 0.0 troca o -0 por 0 quando um valor muito pequeno e negativo é arredondado.
def _numero(valor: float) -> str:
    return f"{round(float(valor), 3) + 0.0:g}"


# Escreve um vetor como (x, y, z) com cada componente arredondada por _numero.
def _vetor(vetor: np.ndarray) -> str:
    return "(" + ", ".join(_numero(componente) for componente in vetor) + ")"


# Escreve um ângulo θ, guardado em radianos, em graus.
def _graus(theta: float) -> str:
    return _numero(np.degrees(theta)) + "°"


# Monta uma tabela com larguras de coluna dadas em centímetros.
def _tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[float]):
    return documento.tabela(cabecalho, linhas, [largura * cm for largura in larguras])


# Linhas da capa que resumem os dados de entrada das duas partes.
def _parametros(cfg: Config) -> list[str]:
    h = cfg.hipocicloide
    c = cfg.cubica
    return [
        f"<b>Aro e disco</b>: R = {_numero(h.raio_aro)}, r = {_numero(h.raio_disco)}",
        f"<b>Razões R/r dos exemplos</b>: {', '.join(_numero(razao) for razao in h.razoes)}",
        f"<b>Lei horária</b>: θ(t) = ω t, com ω = π/60 ≈ {_numero(h.omega)} rad/s",
        f"<b>Instantes</b>: {', '.join(f'{_numero(t)} s' for t in h.instantes)}",
        (
            f"<b>Curva C</b>: λ de {_numero(c.lambda_minimo)} a {_numero(c.lambda_maximo)}, "
            f"triedros em λ = {', '.join(_numero(valor) for valor in c.parametros)}"
        ),
    ]


# Texto e tabelas da parte 1: equações da curva, raio de curvatura (1.5), versores (1.6)
# e velocidade e aceleração nas formas cartesiana e intrínseca (1.7).
def _parte_1(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
    estilos: dict,
) -> list:
    h = cfg.hipocicloide
    escala_v, escala_a = desenho.escalas_cinematica(cfg, cinematicas)
    texto = estilos["texto"]
    return [
        Paragraph("Parte 1: hipociclóide", estilos["secao"]),
        Paragraph(
            f"Um disco de raio r = {_numero(h.raio_disco)} rola sem escorregar dentro de um aro "
            f"de raio R = {_numero(h.raio_aro)}. O ponto P do disco descreve "
            "x = (R - r) cos θ + r cos(kθ) e y = (R - r) sin θ - r sin(kθ), com k = (R - r) / r. "
            f"O vídeo do item 1.2, {Path(cfg.saida_animacao).name}, está anexado a este PDF, "
            "no painel de anexos do leitor, e é entregue também como arquivo separado. A Figura 2 "
            "mostra quadros desse vídeo.",
            texto,
        ),
        Paragraph(
            "Como no capítulo 3 das notas de aula, com r' = dP/dθ e r'' = d²P/dθ²: "
            "ρ = |r'|³ / |r' ∧ r''|, τ = r' / |r'|, b = (r' ∧ r'') / |r' ∧ r''| = ±k e n = b ∧ τ. "
            "Nas cúspides r' = 0, e τ e n não são definidos.",
            texto,
        ),
        Paragraph("Item 1.5: raio de curvatura", estilos["secao"]),
        _tabela(
            ["Ponto", "θ", "P", "ρ", "Centro de curvatura"],
            [
                [str(i), _graus(c.theta), _vetor(c.ponto), _numero(c.raio), _vetor(c.centro)]
                for i, c in enumerate(curvaturas, start=1)
            ],
            [1.5, 2.0, 4.8, 2.0, 5.7],
        ),
        Paragraph("Item 1.6: versores tangente e normal principal", estilos["secao"]),
        _tabela(
            ["θ", "P", "τ", "n"],
            [
                [_graus(c.theta), _vetor(c.ponto), _vetor(c.tangente), _vetor(c.normal)]
                for c in versores
            ],
            [2.0, 4.4, 4.8, 4.8],
        ),
        PageBreak(),
        Paragraph("Item 1.7: velocidade e aceleração", estilos["secao"]),
        Paragraph(
            "Com θ(t) = ω t, a regra da cadeia dá v = ω dP/dθ e, como ω é constante, "
            "a = ω² d²P/dθ². Na forma intrínseca, v = v τ e a = a_τ τ + a_n n, com v = |v|, "
            "a_τ = dv/dt = a · τ e a_n = v² / ρ = a · n. Comprimentos na mesma unidade de R e r, "
            "tempos em segundos.",
            texto,
        ),
        Paragraph("Forma cartesiana", texto),
        _tabela(
            ["t", "θ", "P", "v", "a"],
            [
                [
                    f"{_numero(k.t)} s",
                    _graus(k.curvatura.theta),
                    _vetor(k.curvatura.ponto),
                    _vetor(k.velocidade),
                    _vetor(k.aceleracao),
                ]
                for k in cinematicas
            ],
            [1.4, 1.6, 3.6, 4.7, 4.7],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Coordenadas intrínsecas", texto),
        _tabela(
            ["t", "v", "a_τ", "a_n", "ρ", "τ", "n"],
            [
                [
                    f"{_numero(k.t)} s",
                    _numero(np.linalg.norm(k.velocidade)),
                    _numero(k.a_tangencial),
                    _numero(k.a_normal),
                    _numero(k.curvatura.raio),
                    _vetor(k.curvatura.tangente),
                    _vetor(k.curvatura.normal),
                ]
                for k in cinematicas
            ],
            [1.4, 1.6, 1.6, 1.6, 1.6, 4.1, 4.1],
        ),
        Spacer(1, 0.2 * cm),
        Paragraph(
            f"Na Figura 6, v aparece multiplicada por {_numero(escala_v)} "
            f"e a por {_numero(escala_a)}.",
            texto,
        ),
        PageBreak(),
    ]


# Texto e tabelas da parte 2: o raio de curvatura (2.2) e o triedro de Frenet (2.3) nos
# três pontos escolhidos da curva C.
def _parte_2(triedros: list[Triedro], estilos: dict) -> list:
    return [
        Paragraph("Parte 2: curva C", estilos["secao"]),
        Paragraph(
            "Para r(λ) = (λ, λ², λ³), vale r' = (1, 2λ, 3λ²) e r'' = (0, 2, 6λ). Pelo mesmo "
            "procedimento do capítulo 3, ρ = |r'|³ / |r' ∧ r''|, τ = r' / |r'|, "
            "b = (r' ∧ r'') / |r' ∧ r''| e n = b ∧ τ.",
            estilos["texto"],
        ),
        Paragraph("Item 2.2: raio de curvatura", estilos["secao"]),
        _tabela(
            ["λ", "P", "ρ"],
            [[_numero(t.parametro), _vetor(t.ponto), _numero(t.raio)] for t in triedros],
            [2.0, 9.0, 5.0],
        ),
        Paragraph("Item 2.3: triedro de Frenet", estilos["secao"]),
        _tabela(
            ["λ", "τ", "n", "b"],
            [
                [_numero(t.parametro), _vetor(t.tangente), _vetor(t.normal), _vetor(t.binormal)]
                for t in triedros
            ],
            [1.6, 4.8, 4.8, 4.8],
        ),
        PageBreak(),
    ]


# Monta o PDF completo: capa, parte 1 com as figuras 1 a 6, parte 2 com a figura 7 e o
# código-fonte. Por fim anexa o vídeo do item 1.2 ao PDF.
def gerar_pdf(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
    triedros: list[Triedro],
    arquivos: list[Path],
    caminho: str | Path,
) -> Path:
    estilos = documento.estilos()
    explicacao = (
        "Na primeira parte, o programa traça a hipociclóide gerada por um disco que rola dentro "
        "de um aro, grava um vídeo do processo, mostra instantâneos e exemplos para quatro "
        "razões R/r, e calcula o raio de curvatura, os versores tangente e normal principal e a "
        "velocidade e a aceleração de P nas formas cartesiana e intrínseca. Na segunda parte, "
        "calcula o raio de curvatura e o triedro de Frenet da curva (λ, λ², λ³) em três pontos."
    )
    conteudo = documento.capa(
        "Hipociclóide e triedro de Frenet",
        TAREFA,
        _parametros(cfg),
        explicacao,
        estilos,
        credito_ao_claude=False,
    )
    conteudo += _parte_1(cfg, curvaturas, versores, cinematicas, estilos)
    figuras = [
        (desenho.figura_curva(cfg), "Item 1.1: hipociclóide", "O aro, a curva e as cúspides."),
        (
            desenho.figura_instantaneos(cfg),
            "Item 1.3: instantâneos da geração",
            "O disco, o raio CP, o ponto de contato com o aro e o traço de P até cada θ.",
        ),
        (
            desenho.figura_razoes(cfg),
            "Item 1.4: quatro razões R/r",
            "Com R/r = p/q irredutível, a curva tem p cúspides e fecha após q voltas.",
        ),
        (
            desenho.figura_curvatura(cfg, curvaturas),
            "Item 1.5: raio de curvatura",
            "Círculos osculadores nos pontos da tabela, numerados na mesma ordem.",
        ),
        (
            desenho.figura_versores(cfg, versores),
            "Item 1.6: versores tangente e normal principal",
            "A normal principal aponta sempre para o centro de curvatura.",
        ),
        (
            desenho.figura_cinematica(cfg, cinematicas),
            "Item 1.7: velocidade e aceleração",
            "Vetores v e a de P nos três instantes, nas escalas indicadas no texto.",
        ),
    ]
    for numero, (figura, titulo, legenda) in enumerate(figuras, start=1):
        conteudo += documento.pagina_de_figura(
            figura, f"Figura {numero}: {titulo}", legenda, cfg.dpi, estilos
        )
    conteudo += _parte_2(triedros, estilos)
    conteudo += documento.pagina_de_figura(
        desenho.figura_cubica(cfg, triedros),
        "Figura 7: itens 2.1 e 2.3, curva C",
        cfg.vista.descricao,
        cfg.dpi,
        estilos,
    )
    documento.gerar_pdf(TAREFA, conteudo, arquivos, caminho)
    documento.anexar(caminho, cfg.saida_animacao)
    return Path(caminho)
