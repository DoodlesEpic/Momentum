# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Figuras tridimensionais dos sistemas de forças da Tarefa 2."""

from dataclasses import dataclass

import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from ..comum import cena, vetores
from .config import Config
from .sistema import Reducao


@dataclass
class FigurasDoCaso:
    """Figuras do item h e, quando aplicável, do item i do enunciado."""

    reducao: Figure
    eixo_central: Figure | None


def _vistas(cfg: Config, reducao: Reducao) -> list[cena.Vista]:
    """Usa vistas próprias do caso quando elas forem informadas."""
    vistas = reducao.caso.vistas or cfg.vistas
    if len(vistas) < 2:
        raise ValueError("cada caso precisa de duas vistas para as figuras")
    return vistas


def _fator_de_escala(vetores_a_desenhar: list[np.ndarray], tamanho: float, fracao: float) -> float:
    """Escala vetores visualmente sem alterar os resultados calculados."""
    maior_modulo = max((np.linalg.norm(vetor) for vetor in vetores_a_desenhar), default=0.0)
    return 0.0 if maior_modulo == 0.0 else fracao * tamanho / maior_modulo


def _nao_nulo(vetor: np.ndarray | None, tolerancia: float) -> bool:
    """Evita desenhar setas sem comprimento visível."""
    return vetor is not None and np.linalg.norm(vetor) > tolerancia


def _marcas_reducao(cfg: Config, reducao: Reducao) -> list[Line2D]:
    """Marcas da legenda da primeira figura."""
    cores = cfg.cores
    marcas = [
        Line2D([], [], color=cores["forca"], lw=2, label="forças Fᵢ"),
        Line2D([], [], color=cores["polo"], marker="o", lw=0, label="polos Q e A"),
        Line2D([], [], color=cores["eixo_au"], lw=1.2, ls="--", label="eixo Au"),
    ]
    if _nao_nulo(reducao.resultante, cfg.tolerancia):
        marcas.append(Line2D([], [], color=cores["resultante"], lw=2, label="resultante R"))
    if _nao_nulo(reducao.momento_q, cfg.tolerancia) or _nao_nulo(
        reducao.momento_a, cfg.tolerancia
    ):
        marcas.append(Line2D([], [], color=cores["momento"], lw=1.5, label="momentos"))
    return marcas


def _marcas_eixo_central(cfg: Config, reducao: Reducao) -> list[Line2D]:
    """Marcas da legenda da segunda figura."""
    cores = cfg.cores
    marcas = [
        Line2D([], [], color=cores["forca"], lw=2, label="forças Fᵢ"),
        Line2D([], [], color=cores["momento"], lw=1.5, label="momento M_Q"),
        Line2D([], [], color=cores["eixo_central"], lw=1.8, ls="--", label="eixo central"),
        Line2D([], [], color=cores["resultante"], lw=2, label="resultante R"),
    ]
    if _nao_nulo(reducao.momento_minimo, cfg.tolerancia):
        marcas.append(Line2D([], [], color=cores["momento"], lw=1.5, label="momento mínimo M_E"))
    return marcas


def _desenhar_forcas(eixos, cfg: Config, reducao: Reducao, fator: float) -> list[np.ndarray]:
    """Desenha todas as forças e seus pontos de aplicação."""
    pontas = []
    for indice, (ponto, forca) in enumerate(zip(reducao.caso.pontos, reducao.caso.forcas), start=1):
        cena.marcar_ponto(eixos, ponto, cfg.cores["forca"], f"P{indice}")
        pontas.append(
            cena.seta(
                eixos,
                ponto,
                forca * fator,
                cfg.cores["forca"],
                f"F{indice}",
                largura=1.8,
            )
        )
    return pontas


def figura_reducao(cfg: Config, reducao: Reducao) -> Figure:
    """Monta a figura com forças, polos, eixo Au e momentos nos polos."""
    vista = _vistas(cfg, reducao)[0]
    caso = reducao.caso
    cores = cfg.cores
    tamanho = float(np.max(cfg.solido.dimensoes))
    vetores_de_forca = [*caso.forcas, reducao.resultante]
    fator_forca = _fator_de_escala(vetores_de_forca, tamanho, cfg.escala_forca)
    vetores_de_momento = [reducao.momento_q, reducao.momento_a]
    fator_momento = _fator_de_escala(vetores_de_momento, tamanho, cfg.escala_momento)
    figura, eixos = cena.criar_eixos(vista)
    vertices = cena.paralelepipedo(
        eixos, cfg.solido.canto, cfg.solido.dimensoes, cores["solido"], cfg.opacidade_solido
    )
    pontas = _desenhar_forcas(eixos, cfg, reducao, fator_forca)
    cena.marcar_ponto(eixos, caso.polo_q, cores["polo"], "Q")
    cena.marcar_ponto(eixos, caso.polo_a, cores["polo"], "A")
    inicio_au, fim_au = vetores.segmento_da_reta(
        caso.polo_a, caso.versor_u, cfg.comprimento_eixo * tamanho
    )
    cena.segmento(eixos, inicio_au, fim_au, cores["eixo_au"], ls="--", lw=1.2)
    pontas += [inicio_au, fim_au]
    if _nao_nulo(reducao.resultante, cfg.tolerancia):
        pontas.append(
            cena.seta(
                eixos,
                caso.polo_q,
                reducao.resultante * fator_forca,
                cores["resultante"],
                "R",
                largura=2.2,
            )
        )
    if _nao_nulo(reducao.momento_q, cfg.tolerancia):
        pontas.append(
            cena.seta(
                eixos,
                caso.polo_q,
                reducao.momento_q * fator_momento,
                cores["momento"],
                "M_Q",
                largura=1.4,
            )
        )
    if _nao_nulo(reducao.momento_a, cfg.tolerancia):
        pontas.append(
            cena.seta(
                eixos,
                caso.polo_a,
                reducao.momento_a * fator_momento,
                cores["momento"],
                "M_A",
                largura=1.4,
            )
        )
    pontos = np.vstack([vertices, caso.pontos, caso.polo_q, caso.polo_a, *pontas])
    cena.finalizar(eixos, pontos, vista, f"{caso.nome}: redução do sistema")
    cena.legenda(eixos, _marcas_reducao(cfg, reducao))
    return figura


def figura_eixo_central(cfg: Config, reducao: Reducao) -> Figure:
    """Monta a figura que localiza R e M_E sobre o eixo central."""
    if reducao.eixo_central is None or reducao.momento_minimo is None:
        raise ValueError("não existe eixo central para este sistema")
    vista = _vistas(cfg, reducao)[1]
    caso = reducao.caso
    eixo = reducao.eixo_central
    cores = cfg.cores
    tamanho = float(np.max(cfg.solido.dimensoes))
    fator_forca = _fator_de_escala([*caso.forcas, reducao.resultante], tamanho, cfg.escala_forca)
    fator_momento = _fator_de_escala(
        [reducao.momento_q, reducao.momento_minimo], tamanho, cfg.escala_momento
    )
    figura, eixos = cena.criar_eixos(vista)
    vertices = cena.paralelepipedo(
        eixos, cfg.solido.canto, cfg.solido.dimensoes, cores["solido"], cfg.opacidade_solido
    )
    pontas = _desenhar_forcas(eixos, cfg, reducao, fator_forca)
    cena.marcar_ponto(eixos, caso.polo_q, cores["polo"], "Q")
    inicio, fim = vetores.segmento_da_reta(
        eixo.ponto, eixo.direcao, cfg.comprimento_eixo * tamanho
    )
    cena.segmento(eixos, inicio, fim, cores["eixo_central"], ls="--", lw=1.8)
    pontas += [inicio, fim]
    if _nao_nulo(reducao.momento_q, cfg.tolerancia):
        pontas.append(
            cena.seta(
                eixos,
                caso.polo_q,
                reducao.momento_q * fator_momento,
                cores["momento"],
                "M_Q",
                largura=1.4,
            )
        )
    pontas.append(
        cena.seta(
            eixos,
            eixo.ponto,
            reducao.resultante * fator_forca,
            cores["resultante"],
            "R",
            largura=2.2,
        )
    )
    if _nao_nulo(reducao.momento_minimo, cfg.tolerancia):
        pontas.append(
            cena.seta(
                eixos,
                eixo.ponto,
                reducao.momento_minimo * fator_momento,
                cores["momento"],
                "M_E",
                largura=1.4,
            )
        )
    pontos = np.vstack([vertices, caso.pontos, caso.polo_q, eixo.ponto, *pontas])
    cena.finalizar(eixos, pontos, vista, f"{caso.nome}: eixo central")
    cena.legenda(eixos, _marcas_eixo_central(cfg, reducao))
    return figura


def gerar_figuras(cfg: Config, reducoes: list[Reducao]) -> list[FigurasDoCaso]:
    """Gera as figuras pedidas para todos os sistemas configurados."""
    figuras = []
    for reducao in reducoes:
        figuras.append(
            FigurasDoCaso(
                reducao=figura_reducao(cfg, reducao),
                eixo_central=(
                    figura_eixo_central(cfg, reducao)
                    if reducao.eixo_central is not None
                    else None
                ),
            )
        )
    return figuras
