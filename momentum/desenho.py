# Momentum - visualização do campo de momentos de uma força
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior; veja o arquivo LICENSE.

"""Desenho das figuras do campo de momentos com Matplotlib."""

import matplotlib

matplotlib.use("Agg")  # backend sem interface gráfica: só grava arquivos

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from . import campo
from .config import Config, Vista


def _angulos_axiais(n: np.ndarray) -> tuple[float, float]:
    """Elevação e azimute que colocam a câmera sobre a direção n."""
    return float(np.degrees(np.arcsin(np.clip(n[2], -1.0, 1.0)))), float(
        np.degrees(np.arctan2(n[1], n[0]))
    )


def _cubo_envolvente(pontos: np.ndarray, folga: float = 1.08):
    """Limites cúbicos que contêm todos os pontos, para não distorcer a figura."""
    minimo, maximo = pontos.min(axis=0), pontos.max(axis=0)
    centro = (minimo + maximo) / 2
    raio = max(float((maximo - minimo).max()) / 2, 1e-6) * folga
    return centro - raio, centro + raio


def _legenda(ax, cores: dict) -> None:
    marcas = [
        Line2D([], [], color=cores["forca"], lw=2, label="força F e linha de ação"),
        Line2D([], [], color=cores["momento"], lw=1.4, label="momento M(O)"),
        Line2D([], [], color=cores["raio"], lw=1, ls="--", label="O até Q"),
        Line2D([], [], color=cores["fecho"], lw=1, ls="--", label="M(O) até Q"),
    ]
    ax.legend(handles=marcas, loc="upper left", fontsize=7, framealpha=0.9)


def figura(cfg: Config, amostras: list[campo.Amostra], vista: Vista) -> Figure:
    """Monta a figura de uma vista do campo de momentos."""
    cores = cfg.cores
    inicio, fim = campo.extremos_da_linha_de_acao(cfg)
    pontas = [O + M * cfg.escala_momento for O, M in ((a.O, a.M) for a in amostras)]

    fig = plt.figure(figsize=(7.4, 5.6))
    ax = fig.add_subplot(projection="3d")
    ax.set_proj_type(vista.projecao)
    if vista.axial:
        elevacao, azimute = _angulos_axiais(campo.versor(cfg.forca))
    else:
        elevacao, azimute = vista.elevacao, vista.azimute
    ax.view_init(elev=elevacao, azim=azimute)

    # Linha de ação e a força aplicada em P, ambas em vermelho.
    ax.plot(*zip(inicio, fim), color=cores["forca"], lw=1.2, ls="-", alpha=0.8)
    ax.quiver(
        *cfg.ponto,
        *(cfg.forca * cfg.escala_forca),
        color=cores["forca"],
        lw=2.2,
        arrow_length_ratio=0.18,
    )
    ax.text(*(cfg.ponto + cfg.forca * cfg.escala_forca), "  F", color=cores["forca"], fontsize=10)
    ax.scatter(*cfg.ponto, color=cores["forca"], s=18)
    ax.text(*cfg.ponto, "  P", color=cores["forca"], fontsize=8)

    for amostra, ponta in zip(amostras, pontas):
        # Tracejado verde: do ponto O até o pé da perpendicular Q.
        ax.plot(*zip(amostra.O, amostra.Q), color=cores["raio"], lw=0.8, ls="--")
        # Tracejado azul: da extremidade do momento M(O) até o mesmo ponto Q.
        ax.plot(*zip(ponta, amostra.Q), color=cores["fecho"], lw=0.8, ls="--")
        # Vetor momento, desenhado a partir de O.
        ax.quiver(
            *amostra.O,
            *(amostra.M * cfg.escala_momento),
            color=cores["momento"],
            lw=1.1,
            arrow_length_ratio=0.16,
        )

    pontos = np.array([a.O for a in amostras] + [a.Q for a in amostras])
    ax.scatter(pontos[:, 0], pontos[:, 1], pontos[:, 2], color=cores["ponto"], s=6)

    inferior, superior = _cubo_envolvente(
        np.vstack([pontos, np.array(pontas), inicio, fim, cfg.ponto + cfg.forca * cfg.escala_forca])
    )
    ax.set_xlim(inferior[0], superior[0])
    ax.set_ylim(inferior[1], superior[1])
    ax.set_zlim(inferior[2], superior[2])
    ax.set_box_aspect((1, 1, 1), zoom=vista.zoom)  # escalas iguais nos três eixos

    ax.set_xlabel("x", fontsize=9)
    ax.set_ylabel("y", fontsize=9)
    ax.set_zlabel("z", fontsize=9)
    ax.tick_params(labelsize=7)
    ax.set_title(vista.nome, fontsize=12, pad=0)
    _legenda(ax, cores)
    fig.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.94)
    return fig


def gerar_figuras(cfg: Config, amostras: list[campo.Amostra]) -> list[Figure]:
    """Uma figura para cada vista configurada."""
    return [figura(cfg, amostras, vista) for vista in cfg.vistas]
