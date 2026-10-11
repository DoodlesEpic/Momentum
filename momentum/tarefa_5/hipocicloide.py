# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Geometria e cinemática da hipociclóide gerada por um disco que rola dentro de um aro."""

from dataclasses import dataclass
from fractions import Fraction

import numpy as np

from ..comum import vetores


# Raio de curvatura, centro de curvatura e versores τ e n em uma posição θ da curva.
@dataclass
class Curvatura:
    theta: float
    ponto: np.ndarray
    raio: float
    centro: np.ndarray
    tangente: np.ndarray
    normal: np.ndarray


# Velocidade, aceleração e componentes intrínsecas de P em um instante t.
@dataclass
class Cinematica:
    t: float
    curvatura: Curvatura
    velocidade: np.ndarray
    aceleracao: np.ndarray
    a_tangencial: float
    a_normal: float


# Voltas do centro do disco até P voltar ao ponto de partida. Se R/r = p/q em fração
# irredutível, são q voltas. Razões irracionais são aproximadas com no máximo "maximo" voltas.
def voltas(razao: float, maximo: int) -> int:
    return Fraction(razao).limit_denominator(maximo).denominator


# Pontos P(θ) da hipociclóide pelas equações do enunciado, um ponto (x, y) por linha.
def posicao(R: float, r: float, theta) -> np.ndarray:
    k = (R - r) / r
    x = (R - r) * np.cos(theta) + r * np.cos(k * theta)
    y = (R - r) * np.sin(theta) - r * np.sin(k * theta)
    return np.stack([x, y], axis=-1)


# Derivadas dP/dθ e d²P/dθ², obtidas derivando à mão as equações do enunciado.
# Têm componente z = 0 para que se possa usar o produto vetorial ∧ das notas de aula.
def derivadas(R: float, r: float, theta: float) -> tuple[np.ndarray, np.ndarray]:
    k = (R - r) / r
    primeira = (R - r) * np.array(
        [-np.sin(theta) - np.sin(k * theta), np.cos(theta) - np.cos(k * theta), 0.0]
    )
    segunda = (R - r) * np.array(
        [-np.cos(theta) - k * np.cos(k * theta), -np.sin(theta) + k * np.sin(k * theta), 0.0]
    )
    return primeira, segunda


# Centro C do disco, que gira em torno do centro O do aro à distância R - r.
def centro_do_disco(R: float, r: float, theta: float) -> np.ndarray:
    return (R - r) * np.array([np.cos(theta), np.sin(theta)])


# Ponto T em que o disco toca o aro. Sem escorregamento, é o ponto do disco com velocidade nula.
def ponto_de_contato(R: float, theta: float) -> np.ndarray:
    return R * np.array([np.cos(theta), np.sin(theta)])


# Cúspides, os pontos em que P encosta no aro. Elas se repetem a cada 2πr/R de θ.
def cuspides(R: float, r: float, voltas_da_curva: int) -> np.ndarray:
    quantidade = round(voltas_da_curva * R / r)
    return posicao(R, r, 2 * np.pi * r / R * np.arange(quantidade))


# Raio de curvatura e versores τ e n em θ, pela seção 16 do capítulo 3 com r' = dP/dθ e
# r'' = d²P/dθ². Nas cúspides dP/dθ = 0, e τ e n não existem, como dizem as notas.
def curvatura(R: float, r: float, theta: float) -> Curvatura:
    primeira, segunda = derivadas(R, r, theta)
    if np.linalg.norm(primeira) < 1e-9 * R:
        raise ValueError(f"θ = {np.degrees(theta):g}° é uma cúspide, onde τ e n não existem")
    raio, tangente, normal, _ = vetores.frenet(primeira, segunda)
    ponto = posicao(R, r, theta)
    return Curvatura(theta, ponto, raio, ponto + raio * normal[:2], tangente, normal)


# Velocidade e aceleração de P com θ(t) = ω t. Pela regra da cadeia v = ω dP/dθ e, como ω
# é constante, a = ω² d²P/dθ². Na forma intrínseca a = a_τ τ + a_n n, com a_τ = a · τ e a_n = a · n.
def cinematica(R: float, r: float, omega: float, t: float) -> Cinematica:
    geometria = curvatura(R, r, omega * t)
    primeira, segunda = derivadas(R, r, omega * t)
    velocidade = omega * primeira
    aceleracao = omega**2 * segunda
    return Cinematica(
        t=t,
        curvatura=geometria,
        velocidade=velocidade,
        aceleracao=aceleracao,
        a_tangencial=float(np.dot(aceleracao, geometria.tangente)),
        a_normal=float(np.dot(aceleracao, geometria.normal)),
    )
