# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Geometria e cinemática da hipociclóide gerada por um disco que rola dentro de um aro."""

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from ..comum import vetores


@dataclass
class Curvatura:
    """Raio de curvatura e versores de Frenet em uma posição θ."""

    theta: float
    ponto: np.ndarray
    raio: float
    centro: np.ndarray
    tangente: np.ndarray
    normal: np.ndarray


@dataclass
class Cinematica:
    """Velocidade e aceleração de P em um instante t."""

    t: float
    curvatura: Curvatura
    velocidade: np.ndarray
    aceleracao: np.ndarray
    a_tangencial: float
    a_normal: float


def voltas(razao: float, maximo: int) -> int:
    """Voltas do centro do disco até a curva fechar, q para R/r = p/q irredutível."""
    return Fraction(razao).limit_denominator(maximo).denominator


def posicao(R: float, r: float, theta) -> np.ndarray:
    """Pontos P(θ) da hipociclóide, um por linha."""
    k = (R - r) / r
    x = (R - r) * np.cos(theta) + r * np.cos(k * theta)
    y = (R - r) * np.sin(theta) - r * np.sin(k * theta)
    return np.stack([x, y], axis=-1)


def derivadas(R: float, r: float, theta: float) -> tuple[np.ndarray, np.ndarray]:
    """Derivadas primeira e segunda de P em relação a θ."""
    k = (R - r) / r
    primeira = (R - r) * np.array(
        [-np.sin(theta) - np.sin(k * theta), np.cos(theta) - np.cos(k * theta)]
    )
    segunda = (R - r) * np.array(
        [-np.cos(theta) - k * np.cos(k * theta), -np.sin(theta) + k * np.sin(k * theta)]
    )
    return primeira, segunda


def centro_do_disco(R: float, r: float, theta: float) -> np.ndarray:
    return (R - r) * np.array([np.cos(theta), np.sin(theta)])


def ponto_de_contato(R: float, theta: float) -> np.ndarray:
    return R * np.array([np.cos(theta), np.sin(theta)])


def cuspides(R: float, r: float, voltas_da_curva: int) -> np.ndarray:
    """Pontos em que P toca o aro, a cada 2πr/R de θ."""
    quantidade = round(voltas_da_curva * R / r)
    return posicao(R, r, 2 * np.pi * r / R * np.arange(quantidade))


def curvatura(R: float, r: float, theta: float) -> Curvatura:
    """Raio de curvatura e versores τ e n em θ, como no capítulo 3 das notas de aula."""
    seno = np.sin(R * theta / (2 * r))
    if abs(seno) < 1e-9:
        raise ValueError(f"θ = {np.degrees(theta):g}° é uma cúspide, onde τ e n não existem")
    primeira, segunda = derivadas(R, r, theta)
    # Componente z de P' ∧ P'', o único termo não nulo no plano.
    produto = primeira[0] * segunda[1] - primeira[1] * segunda[0]
    raio = np.linalg.norm(primeira) ** 3 / abs(produto)
    if not np.isclose(raio, 4 * r * (R - r) * abs(seno) / abs(R - 2 * r)):
        raise ValueError("o raio de curvatura não confere com a forma fechada")
    tangente = vetores.versor(primeira)
    # b = ±k, e n = b ∧ τ.
    normal = np.sign(produto) * np.array([-tangente[1], tangente[0]])
    ponto = posicao(R, r, theta)
    return Curvatura(theta, ponto, raio, ponto + raio * normal, tangente, normal)


def cinematica(R: float, r: float, omega: float, t: float) -> Cinematica:
    """Velocidade e aceleração de P com a lei horária θ(t) = ω t."""
    theta = omega * t
    intrinseca = curvatura(R, r, theta)
    primeira, segunda = derivadas(R, r, theta)
    velocidade = omega * primeira
    aceleracao = omega**2 * segunda
    return Cinematica(
        t=t,
        curvatura=intrinseca,
        velocidade=velocidade,
        aceleracao=aceleracao,
        a_tangencial=float(np.dot(aceleracao, intrinseca.tangente)),
        a_normal=float(np.dot(aceleracao, intrinseca.normal)),
    )
