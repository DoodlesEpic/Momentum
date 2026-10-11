# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Montagem do relatório PDF da Tarefa 5."""

from pathlib import Path

import numpy as np
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer, TableStyle

from ..comum import documento
from . import desenho
from .config import Config
from .cubica import Triedro
from .hipocicloide import Cinematica, Curvatura

TAREFA = "Tarefa Optativa 5"
FONTE = documento.FONTE_UNICODE


def _estilos() -> dict:
    """Estilos comuns com uma fonte que tem as letras gregas."""
    estilos = documento.estilos()
    for nome in ("titulo", "subtitulo", "secao", "texto", "legenda"):
        negrito = estilos[nome].fontName.endswith("Bold")
        estilos[nome].fontName = FONTE + "-Bold" if negrito else FONTE
    return estilos


def _tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[float]):
    tabela = documento.tabela(cabecalho, linhas, [largura * cm for largura in larguras])
    tabela.setStyle(
        TableStyle(
            [("FONTNAME", (0, 0), (-1, -1), FONTE), ("FONTNAME", (0, 0), (-1, 0), FONTE + "-Bold")]
        )
    )
    return tabela


def _numero(valor: float) -> str:
    """Escreve zeros numéricos, como 1e-18, simplesmente como 0."""
    return f"{valor:.5g}" if abs(valor) > 1e-12 else "0"


def _vetor(vetor: np.ndarray) -> str:
    return documento.vetor(np.where(np.abs(vetor) > 1e-12, vetor, 0.0))


def _graus(theta: float) -> str:
    return f"{np.degrees(theta):.6g}°"


def _parametros(cfg: Config) -> list[str]:
    h = cfg.hipocicloide
    c = cfg.cubica
    return [
        f"<b>Aro e disco</b>: R = {h.raio_aro:g}, r = {h.raio_disco:g}",
        f"<b>Razões R/r dos exemplos</b>: {', '.join(f'{razao:g}' for razao in h.razoes)}",
        f"<b>Lei horária</b>: θ(t) = ω t, com ω = π/60 = {h.omega:.6g} rad/s",
        f"<b>Instantes</b>: {', '.join(f'{t:g} s' for t in h.instantes)}",
        (
            f"<b>Curva C</b>: λ de {c.lambda_minimo:g} a {c.lambda_maximo:g}, "
            f"triedros em λ = {', '.join(f'{valor:g}' for valor in c.parametros)}"
        ),
    ]


def _parte_1(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
    estilos: dict,
) -> list:
    """Texto e tabelas da hipociclóide."""
    h = cfg.hipocicloide
    escala_v, escala_a = desenho.escalas_cinematica(cfg, cinematicas)
    texto = estilos["texto"]
    return [
        Paragraph("Parte 1: hipociclóide", estilos["secao"]),
        Paragraph(
            f"Um disco de raio r = {h.raio_disco:g} rola sem escorregar dentro de um aro de raio "
            f"R = {h.raio_aro:g}. O ponto P do disco descreve x = (R - r) cos θ + r cos(kθ) e "
            "y = (R - r) sin θ - r sin(kθ), com k = (R - r) / r. A animação do item 1.2 está no "
            f"arquivo {Path(cfg.saida_animacao).name}, entregue junto com este relatório, e a "
            "Figura 2 mostra quadros dessa animação. Os versores seguem o capítulo 3 das notas de "
            "aula: τ = P' / |P'|, b = (P' ∧ P'') / |P' ∧ P''| = ±k e n = b ∧ τ. Nas cúspides P' "
            "se anula e τ e n não são definidos.",
            texto,
        ),
        Paragraph("Item 1.5: raio de curvatura", estilos["secao"]),
        Paragraph(
            "ρ = |P'|³ / |P' ∧ P''|, conferido com a forma fechada "
            "ρ = 4 r (R - r) |sin(Rθ / 2r)| / |R - 2r|.",
            texto,
        ),
        _tabela(
            ["Ponto", "θ", "P", "ρ", "Centro de curvatura"],
            [
                [
                    str(i),
                    _graus(c.theta),
                    _vetor(c.ponto),
                    f"{c.raio:.6g}",
                    _vetor(c.centro),
                ]
                for i, c in enumerate(curvaturas, start=1)
            ],
            [1.3, 1.8, 5.0, 2.0, 5.9],
        ),
        Paragraph("Item 1.6: versores tangente e normal principal", estilos["secao"]),
        _tabela(
            ["θ", "P", "τ", "n"],
            [
                [
                    _graus(c.theta),
                    _vetor(c.ponto),
                    _vetor(c.tangente),
                    _vetor(c.normal),
                ]
                for c in versores
            ],
            [1.8, 4.6, 4.8, 4.8],
        ),
        PageBreak(),
        Paragraph("Item 1.7: velocidade e aceleração", estilos["secao"]),
        Paragraph(
            "Com θ(t) = ω t, vale v = ω P'(θ) e a = ω² P''(θ). Na forma intrínseca, v = v τ e "
            "a = a_τ τ + a_n n, com v = |v|, a_τ = dv/dt = a · τ e a_n = v² / ρ = a · n. "
            "Comprimentos na mesma unidade de R e r, tempos em segundos.",
            texto,
        ),
        Paragraph("Forma cartesiana", texto),
        _tabela(
            ["t", "θ", "P", "v", "a"],
            [
                [
                    f"{k.t:g} s",
                    _graus(k.curvatura.theta),
                    _vetor(k.curvatura.ponto),
                    _vetor(k.velocidade),
                    _vetor(k.aceleracao),
                ]
                for k in cinematicas
            ],
            [1.3, 1.5, 4.2, 4.4, 4.6],
        ),
        Spacer(1, 0.3 * cm),
        Paragraph("Coordenadas intrínsecas", texto),
        _tabela(
            ["t", "v", "a_τ", "a_n", "ρ", "τ", "n"],
            [
                [
                    f"{k.t:g} s",
                    _numero(np.linalg.norm(k.velocidade)),
                    _numero(k.a_tangencial),
                    _numero(k.a_normal),
                    _numero(k.curvatura.raio),
                    _vetor(k.curvatura.tangente),
                    _vetor(k.curvatura.normal),
                ]
                for k in cinematicas
            ],
            [1.2, 1.7, 1.8, 1.7, 1.6, 4.5, 4.5],
        ),
        Spacer(1, 0.2 * cm),
        Paragraph(
            f"Na Figura 6, v aparece multiplicada por {escala_v:.4g} e a por {escala_a:.4g}.", texto
        ),
        PageBreak(),
    ]


def _parte_2(triedros: list[Triedro], estilos: dict) -> list:
    """Texto e tabelas da curva (λ, λ², λ³)."""
    return [
        Paragraph("Parte 2: curva C", estilos["secao"]),
        Paragraph(
            "Para r(λ) = (λ, λ², λ³), vale r' = (1, 2λ, 3λ²) e r'' = (0, 2, 6λ). O raio de "
            "curvatura é ρ = |r'|³ / |r' ∧ r''|, e o triedro de Frenet é τ = r' / |r'|, "
            "b = (r' ∧ r'') / |r' ∧ r''| e n = b ∧ τ.",
            estilos["texto"],
        ),
        Spacer(1, 0.25 * cm),
        _tabela(
            ["λ", "P", "ρ"],
            [[f"{t.parametro:g}", _vetor(t.ponto), f"{t.raio:.6g}"] for t in triedros],
            [2.0, 9.0, 5.0],
        ),
        Spacer(1, 0.25 * cm),
        _tabela(
            ["λ", "τ", "n", "b"],
            [
                [
                    f"{t.parametro:g}",
                    _vetor(t.tangente),
                    _vetor(t.normal),
                    _vetor(t.binormal),
                ]
                for t in triedros
            ],
            [1.4, 5.2, 5.2, 5.2],
        ),
        PageBreak(),
    ]


def gerar_pdf(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
    triedros: list[Triedro],
    arquivos: list[Path],
    caminho: str | Path,
) -> Path:
    """Grava o relatório completo da Tarefa 5."""
    estilos = _estilos()
    explicacao = (
        "Na primeira parte, o programa traça a hipociclóide gerada por um disco que rola dentro "
        "de um aro, anima o processo, mostra instantâneos e exemplos para quatro razões R/r, e "
        "calcula o raio de curvatura, os versores tangente e normal principal e a velocidade e a "
        "aceleração de P nas formas cartesiana e intrínseca. Na segunda parte, calcula o raio de "
        "curvatura e o triedro de Frenet da curva (λ, λ², λ³) em três pontos."
    )
    conteudo = documento.capa(
        "Hipociclóide e triedro de Frenet", TAREFA, _parametros(cfg), explicacao, estilos
    )
    conteudo += _parte_1(cfg, curvaturas, versores, cinematicas, estilos)
    figuras = [
        (
            desenho.figura_curva(cfg),
            "Item 1.1: hipociclóide",
            "O aro, a curva completa e as cúspides.",
        ),
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
    return documento.gerar_pdf(TAREFA, conteudo, arquivos, caminho)
