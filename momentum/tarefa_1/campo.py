# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Geometria do campo de momentos de uma força F aplicada em um ponto P."""

from dataclasses import dataclass

import numpy as np

from ..comum import vetores
from .config import Config


@dataclass
class Amostra:
    """Um ponto O do espaço, com o pé da perpendicular Q e o momento M(O)."""

    O: np.ndarray  # ponto onde o momento é calculado
    Q: np.ndarray  # ponto da linha de ação mais próximo de O
    M: np.ndarray  # momento de F em relação a O


def gerar_amostras(cfg: Config) -> list[Amostra]:
    """Amostra o campo de momentos em pontos O distribuídos em planos normais
    à linha de ação de F, equiespaçados e centrados no ponto de aplicação.

    Em cada plano, as direções de O em relação à linha de ação são separadas
    por ângulos iguais (60 graus por padrão) e repetidas para cada raio.
    """
    n = vetores.versor(cfg.forca)
    u, v = vetores.base_do_plano(n)
    angulos = np.deg2rad(np.arange(0.0, 360.0, cfg.passo_angular))
    # Posições dos planos ao longo da linha de ação, centradas em P.
    posicoes = (np.arange(cfg.planos) - (cfg.planos - 1) / 2) * cfg.espacamento_planos

    amostras = []
    for posicao in posicoes:
        centro = cfg.ponto + posicao * n  # onde o plano corta a linha de ação
        for angulo in angulos:
            direcao = np.cos(angulo) * u + np.sin(angulo) * v
            for raio in cfg.raios:
                O = centro + raio * direcao
                amostras.append(
                    Amostra(
                        O=O,
                        Q=vetores.pe_da_perpendicular(O, cfg.ponto, n),
                        M=vetores.momento(O, cfg.ponto, cfg.forca),
                    )
                )
    return amostras


def extremos_da_linha_de_acao(cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    """Pontos inicial e final do trecho desenhado da linha de ação de F."""
    return vetores.segmento_da_reta(cfg.ponto, cfg.forca, cfg.comprimento_linha_acao)
