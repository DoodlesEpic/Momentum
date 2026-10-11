# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Operações geométricas e vetoriais usadas nas tarefas."""

import numpy as np


# Versor (vetor de módulo 1) com a direção e o sentido de v.
# Divide v pelo seu módulo e recusa o vetor nulo, que não tem direção.
def versor(v: np.ndarray) -> np.ndarray:
    vetor = np.asarray(v, dtype=float)
    norma = np.linalg.norm(vetor)
    if norma == 0.0:
        raise ValueError("não existe versor de um vetor nulo")
    return vetor / norma


# Dois versores perpendiculares entre si e a n, que formam uma base do plano normal a n.
# Faz o produto vetorial de n com um eixo que não seja quase paralelo a ele.
def base_do_plano(n: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    normal = versor(n)
    referencia = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(referencia, normal)) > 0.9:
        referencia = np.array([0.0, 1.0, 0.0])
    u = versor(np.cross(normal, referencia))
    return u, np.cross(normal, u)


# Momento em relação ao polo O da força F aplicada em P, M(O) = (P - O) ∧ F.
def momento(O: np.ndarray, P: np.ndarray, F: np.ndarray) -> np.ndarray:
    return np.cross(np.asarray(P) - np.asarray(O), np.asarray(F))


# Ponto da reta que passa por P com direção n mais próximo de O.
# Projeta o vetor O - P sobre a direção da reta.
def pe_da_perpendicular(O: np.ndarray, P: np.ndarray, n: np.ndarray) -> np.ndarray:
    direcao = versor(n)
    return np.asarray(P) + np.dot(np.asarray(O) - np.asarray(P), direcao) * direcao


# Extremos de um segmento de reta centrado em ponto, com o comprimento e a direção dados.
def segmento_da_reta(
    ponto: np.ndarray, direcao: np.ndarray, comprimento: float
) -> tuple[np.ndarray, np.ndarray]:
    meio = comprimento / 2
    unitario = versor(direcao)
    return np.asarray(ponto) - meio * unitario, np.asarray(ponto) + meio * unitario


# Raio de curvatura e triedro de Frenet a partir de v e a, ou de r' e r'', como na seção 16
# do capítulo 3: ρ = |v|³ / |v ∧ a|, τ = v / |v|, b = (v ∧ a) / |v ∧ a| e n = b ∧ τ.
def frenet(v: np.ndarray, a: np.ndarray) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    produto = np.cross(v, a)
    raio = float(np.linalg.norm(v) ** 3 / np.linalg.norm(produto))
    tangente = versor(v)
    binormal = versor(produto)
    return raio, tangente, np.cross(binormal, tangente), binormal
