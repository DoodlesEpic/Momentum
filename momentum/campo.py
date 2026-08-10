# Momentum - visualização do campo de momentos de uma força
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Geometria do campo de momentos de uma força F aplicada em um ponto P."""

from dataclasses import dataclass

import numpy as np

from .config import Config


@dataclass
class Amostra:
    """Um ponto O do espaço, com o pé da perpendicular Q e o momento M(O)."""

    O: np.ndarray  # ponto onde o momento é calculado
    Q: np.ndarray  # ponto da linha de ação mais próximo de O
    M: np.ndarray  # momento de F em relação a O


def versor(v: np.ndarray) -> np.ndarray:
    """Vetor unitário com a direção e o sentido de v."""
    return np.asarray(v, dtype=float) / np.linalg.norm(v)


def base_do_plano(n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Dois versores ortonormais que geram o plano normal a n."""
    # Um eixo qualquer serve de referência, desde que não seja paralelo a n.
    referencia = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(referencia, n)) > 0.9:
        referencia = np.array([0.0, 1.0, 0.0])
    u = versor(np.cross(n, referencia))
    return u, np.cross(n, u)


def momento(O: np.ndarray, P: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Momento de F, aplicada em P, em relação ao ponto O: M(O) = (P - O) x F."""
    return np.cross(P - O, F)


def pe_da_perpendicular(O: np.ndarray, P: np.ndarray, n: np.ndarray) -> np.ndarray:
    """Ponto Q da linha de ação (P, n) mais próximo de O, isto é, o pé da
    perpendicular baixada de O sobre a reta."""
    return P + np.dot(O - P, n) * n


def gerar_amostras(cfg: Config) -> list[Amostra]:
    """Amostra o campo de momentos em pontos O distribuídos em planos normais
    à linha de ação de F, equiespaçados e centrados no ponto de aplicação.

    Em cada plano, as direções de O em relação à linha de ação são separadas
    por ângulos iguais (60 graus por padrão) e repetidas para cada raio.
    """
    n = versor(cfg.forca)
    u, v = base_do_plano(n)
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
                        Q=pe_da_perpendicular(O, cfg.ponto, n),
                        M=momento(O, cfg.ponto, cfg.forca),
                    )
                )
    return amostras


def extremos_da_linha_de_acao(cfg: Config) -> tuple[np.ndarray, np.ndarray]:
    """Pontos inicial e final do trecho desenhado da linha de ação de F."""
    n = versor(cfg.forca)
    meio = cfg.comprimento_linha_acao / 2
    return cfg.ponto - meio * n, cfg.ponto + meio * n
