# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Raio de curvatura e triedro de Frenet da curva (λ, λ², λ³)."""

from dataclasses import dataclass

import numpy as np

from ..comum import vetores


# Ponto da curva com o raio de curvatura e os versores τ, n e b do triedro de Frenet.
@dataclass
class Triedro:
    parametro: float
    ponto: np.ndarray
    raio: float
    tangente: np.ndarray
    normal: np.ndarray
    binormal: np.ndarray


# Pontos r(λ) = (λ, λ², λ³) da curva C, um ponto por linha.
def posicao(parametro) -> np.ndarray:
    return np.stack([parametro, parametro**2, parametro**3], axis=-1)


# Triedro de Frenet no ponto de parâmetro λ. Deriva r(λ) à mão, r' = (1, 2λ, 3λ²) e
# r'' = (0, 2, 6λ), e aplica o procedimento da seção 16 do capítulo 3.
def triedro(parametro: float) -> Triedro:
    primeira = np.array([1.0, 2 * parametro, 3 * parametro**2])
    segunda = np.array([0.0, 2.0, 6 * parametro])
    raio, tangente, normal, binormal = vetores.frenet(primeira, segunda)
    return Triedro(parametro, posicao(parametro), raio, tangente, normal, binormal)
