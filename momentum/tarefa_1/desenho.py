# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Desenho das figuras do campo de momentos com Matplotlib."""

from dataclasses import replace

import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from ..comum import cena, vetores
from . import campo
from .config import Config, Vista


def _legenda(eixos, cores: dict) -> None:
    marcas = [
        Line2D([], [], color=cores["forca"], lw=2, label="força F e linha de ação"),
        Line2D([], [], color=cores["momento"], lw=1.4, label="momento M(O)"),
        Line2D([], [], color=cores["raio"], lw=1, ls="--", label="O até Q"),
        Line2D([], [], color=cores["fecho"], lw=1, ls="--", label="M(O) até Q"),
    ]
    cena.legenda(eixos, marcas)


def figura(cfg: Config, amostras: list[campo.Amostra], vista: Vista) -> Figure:
    """Monta a figura de uma vista do campo de momentos."""
    cores = cfg.cores
    inicio, fim = campo.extremos_da_linha_de_acao(cfg)
    pontas = [a.O + a.M * cfg.escala_momento for a in amostras]  # extremidades de M(O)

    if vista.axial:
        elevacao, azimute = cena.angulos_axiais(vetores.versor(cfg.forca))
        vista = replace(vista, elevacao=elevacao, azimute=azimute)
    fig, ax = cena.criar_eixos(vista)

    cena.segmento(ax, inicio, fim, cores["forca"], lw=1.2)
    cena.seta(
        ax,
        cfg.ponto,
        cfg.forca * cfg.escala_forca,
        cores["forca"],
        "F",
        largura=2.2,
        tamanho_da_ponta=0.18,
    )
    cena.marcar_ponto(ax, cfg.ponto, cores["forca"], "P")

    for amostra, ponta in zip(amostras, pontas):
        cena.segmento(ax, amostra.O, amostra.Q, cores["raio"], ls="--", lw=0.8)
        cena.segmento(ax, ponta, amostra.Q, cores["fecho"], ls="--", lw=0.8)
        cena.seta(
            ax,
            amostra.O,
            amostra.M * cfg.escala_momento,
            cores["momento"],
            largura=1.1,
        )

    pontos = np.array([a.O for a in amostras] + [a.Q for a in amostras])
    ax.scatter(pontos[:, 0], pontos[:, 1], pontos[:, 2], color=cores["ponto"], s=6)

    ponta_da_forca = cfg.ponto + cfg.forca * cfg.escala_forca
    cena.finalizar(
        ax, np.vstack([pontos, np.array(pontas), inicio, fim, ponta_da_forca]), vista, vista.nome
    )
    _legenda(ax, cores)
    return fig


def gerar_figuras(cfg: Config, amostras: list[campo.Amostra]) -> list[Figure]:
    """Uma figura para cada vista configurada."""
    return [figura(cfg, amostras, vista) for vista in cfg.vistas]
