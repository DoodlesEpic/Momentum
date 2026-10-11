# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Primitivas para a construção de cenas tridimensionais."""

from dataclasses import dataclass

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


# Câmera de uma figura 3D: projeção em perspectiva ou ortográfica, elevação e azimute
# em graus e zoom.
@dataclass
class Vista:
    nome: str
    descricao: str = ""
    projecao: str = "persp"
    elevacao: float = 30.0
    azimute: float = -60.0
    zoom: float = 1.05


# Elevação e azimute que põem a câmera olhando ao longo da direção n. Saem das
# coordenadas esféricas do versor de n.
def angulos_axiais(n: np.ndarray) -> tuple[float, float]:
    normal = np.asarray(n, dtype=float)
    normal /= np.linalg.norm(normal)
    return float(np.degrees(np.arcsin(np.clip(normal[2], -1.0, 1.0)))), float(
        np.degrees(np.arctan2(normal[1], normal[0]))
    )


# Cubo que contém todos os pontos, com uma pequena folga. Com limites iguais nos três
# eixos, a figura não fica distorcida.
def cubo_envolvente(
    pontos: np.ndarray, folga: float = 1.08
) -> tuple[np.ndarray, np.ndarray]:
    pontos = np.asarray(pontos, dtype=float)
    minimo, maximo = pontos.min(axis=0), pontos.max(axis=0)
    centro = (minimo + maximo) / 2
    raio = max(float((maximo - minimo).max()) / 2, 1e-6) * folga
    return centro - raio, centro + raio


# Cria a figura e os eixos 3D do matplotlib já com a câmera da vista escolhida.
def criar_eixos(vista: Vista):
    figura = plt.figure(figsize=(7.4, 5.6))
    eixos = figura.add_subplot(projection="3d")
    eixos.set_proj_type(vista.projecao)
    eixos.view_init(elev=vista.elevacao, azim=vista.azimute)
    return figura, eixos


# Acerta os limites cúbicos, os rótulos x, y e z, o título e as margens da figura 3D.
def finalizar(eixos, pontos: np.ndarray, vista: Vista, titulo: str) -> None:
    inferior, superior = cubo_envolvente(pontos)
    eixos.set_xlim(inferior[0], superior[0])
    eixos.set_ylim(inferior[1], superior[1])
    eixos.set_zlim(inferior[2], superior[2])
    eixos.set_box_aspect((1, 1, 1), zoom=vista.zoom)
    eixos.set_xlabel("x", fontsize=9)
    eixos.set_ylabel("y", fontsize=9)
    eixos.set_zlabel("z", fontsize=9)
    eixos.tick_params(labelsize=7)
    eixos.set_title(titulo, fontsize=12, pad=0)
    eixos.figure.subplots_adjust(left=0.02, right=0.98, bottom=0.04, top=0.94)


# Desenha a seta de um vetor a partir de origem e devolve a sua ponta. Opcionalmente
# escreve um rótulo junto da ponta.
def seta(
    eixos,
    origem: np.ndarray,
    vetor: np.ndarray,
    cor: str,
    rotulo: str | None = None,
    largura: float = 1.8,
    tamanho_da_ponta: float = 0.16,
) -> np.ndarray:
    origem = np.asarray(origem, dtype=float)
    vetor = np.asarray(vetor, dtype=float)
    eixos.quiver(
        *origem,
        *vetor,
        color=cor,
        lw=largura,
        arrow_length_ratio=tamanho_da_ponta,
    )
    ponta = origem + vetor
    if rotulo:
        eixos.text(*ponta, f"  {rotulo}", color=cor, fontsize=9)
    return ponta


# Desenha o segmento de reta entre os pontos a e b.
def segmento(eixos, a: np.ndarray, b: np.ndarray, cor: str, ls: str = "-", lw: float = 1.2) -> None:
    eixos.plot(*zip(a, b), color=cor, lw=lw, ls=ls)


# Marca um ponto com uma bolinha e escreve o seu nome ao lado.
def marcar_ponto(eixos, ponto: np.ndarray, cor: str, rotulo: str) -> None:
    eixos.scatter(*ponto, color=cor, s=18)
    eixos.text(*ponto, f"  {rotulo}", color=cor, fontsize=8)


# Mostra a legenda no canto superior esquerdo com as marcas dadas.
def legenda(eixos, marcas: list[Line2D]) -> None:
    eixos.legend(handles=marcas, loc="upper left", fontsize=7, framealpha=0.9)


# Desenha um paralelepípedo translúcido a partir de um canto e das dimensões, e devolve
# os seus oito vértices.
def paralelepipedo(
    eixos, canto: np.ndarray, dimensoes: np.ndarray, cor: str, alpha: float
) -> np.ndarray:
    canto = np.asarray(canto, dtype=float)
    dx, dy, dz = np.asarray(dimensoes, dtype=float)
    vertices = canto + np.array(
        [
            [0, 0, 0],
            [dx, 0, 0],
            [dx, dy, 0],
            [0, dy, 0],
            [0, 0, dz],
            [dx, 0, dz],
            [dx, dy, dz],
            [0, dy, dz],
        ]
    )
    faces = [
        vertices[[0, 1, 2, 3]],
        vertices[[4, 5, 6, 7]],
        vertices[[0, 1, 5, 4]],
        vertices[[1, 2, 6, 5]],
        vertices[[2, 3, 7, 6]],
        vertices[[3, 0, 4, 7]],
    ]
    eixos.add_collection3d(
        Poly3DCollection(faces, facecolors=cor, edgecolors=cor, alpha=alpha, linewidths=0.6)
    )
    return vertices
