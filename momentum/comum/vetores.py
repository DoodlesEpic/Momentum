# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Operações geométricas e vetoriais usadas nas tarefas."""

import numpy as np


def versor(v: np.ndarray) -> np.ndarray:
    """Vetor unitário com a direção e o sentido de v."""
    vetor = np.asarray(v, dtype=float)
    norma = np.linalg.norm(vetor)
    if norma == 0.0:
        raise ValueError("não existe versor de um vetor nulo")
    return vetor / norma


def base_do_plano(n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Dois versores ortonormais que geram o plano normal a n."""
    normal = versor(n)
    referencia = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(referencia, normal)) > 0.9:
        referencia = np.array([0.0, 1.0, 0.0])
    u = versor(np.cross(normal, referencia))
    return u, np.cross(normal, u)


def momento(O: np.ndarray, P: np.ndarray, F: np.ndarray) -> np.ndarray:
    """Momento de F, aplicada em P, em relação a O: M(O) = (P - O) x F."""
    return np.cross(np.asarray(P) - np.asarray(O), np.asarray(F))


def pe_da_perpendicular(O: np.ndarray, P: np.ndarray, n: np.ndarray) -> np.ndarray:
    """Ponto da reta (P, n) mais próximo de O."""
    direcao = versor(n)
    return np.asarray(P) + np.dot(np.asarray(O) - np.asarray(P), direcao) * direcao


def segmento_da_reta(
    ponto: np.ndarray, direcao: np.ndarray, comprimento: float
) -> tuple[np.ndarray, np.ndarray]:
    """Extremos de um segmento centrado em ponto, na direção indicada."""
    meio = comprimento / 2
    unitario = versor(direcao)
    return np.asarray(ponto) - meio * unitario, np.asarray(ponto) + meio * unitario
