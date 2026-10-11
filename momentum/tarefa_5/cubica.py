# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Raio de curvatura e triedro de Frenet da curva (λ, λ², λ³)."""

from dataclasses import dataclass

import numpy as np

from ..comum import vetores


@dataclass
class Triedro:
    """Ponto da curva com o raio de curvatura e os versores τ, n e b."""

    parametro: float
    ponto: np.ndarray
    raio: float
    tangente: np.ndarray
    normal: np.ndarray
    binormal: np.ndarray


def posicao(parametro) -> np.ndarray:
    """Pontos (λ, λ², λ³), um por linha."""
    return np.stack([parametro, parametro**2, parametro**3], axis=-1)


def triedro(parametro: float) -> Triedro:
    """Triedro de Frenet pelo procedimento do capítulo 3 das notas de aula."""
    primeira = np.array([1.0, 2 * parametro, 3 * parametro**2])
    segunda = np.array([0.0, 2.0, 6 * parametro])
    produto = np.cross(primeira, segunda)
    raio = np.linalg.norm(primeira) ** 3 / np.linalg.norm(produto)
    tangente = vetores.versor(primeira)
    binormal = vetores.versor(produto)
    normal = np.cross(binormal, tangente)
    return Triedro(parametro, posicao(parametro), raio, tangente, normal, binormal)
