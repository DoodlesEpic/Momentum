# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Figuras e animação da hipociclóide e da curva (λ, λ², λ³)."""

import io
from fractions import Fraction
from pathlib import Path

import imageio_ffmpeg
import matplotlib
import numpy as np
from matplotlib.animation import FFMpegWriter
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from ..comum import cena
from . import cubica, hipocicloide
from .config import Config

# O pacote imageio-ffmpeg traz o programa ffmpeg, que o matplotlib usa para gravar o MP4.
matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()


# Pontos de uma circunferência de centro e raio dados. Servem para o aro, o disco e os
# círculos osculadores.
def _circulo(centro: np.ndarray, raio: float) -> np.ndarray:
    angulos = np.linspace(0.0, 2 * np.pi, 181)
    return centro + raio * np.column_stack([np.cos(angulos), np.sin(angulos)])


# Valores de θ e pontos da hipociclóide de raios R e r, desde θ = 0 até a curva fechar.
def _curva(cfg: Config, R: float, r: float) -> tuple[np.ndarray, np.ndarray]:
    h = cfg.hipocicloide
    voltas = hipocicloide.voltas(R / r, h.voltas_maximas)
    thetas = np.linspace(0.0, 2 * np.pi * voltas, h.pontos_da_curva * voltas)
    return thetas, hipocicloide.posicao(R, r, thetas)


# Desenha o aro e ajusta os eixos com a mesma escala em x e y, para a curva não ficar
# achatada.
def _plano(eixos, cfg: Config, titulo: str, limite: float | None = None) -> None:
    R = cfg.hipocicloide.raio_aro
    limite = limite or 1.12 * R
    eixos.plot(*_circulo(np.zeros(2), R).T, color=cfg.cores["aro"], lw=1.4)
    eixos.set_aspect("equal")
    eixos.set_xlim(-limite, limite)
    eixos.set_ylim(-limite, limite)
    eixos.grid(True, lw=0.3, alpha=0.5)
    eixos.tick_params(labelsize=7)
    eixos.set_title(titulo, fontsize=10)


# Legenda com uma linha colorida para cada par (cor, rótulo).
def _legenda(eixos, itens: list[tuple[str, str]]) -> None:
    marcas = [Line2D([], [], color=cor, lw=2, label=rotulo) for cor, rotulo in itens]
    eixos.legend(handles=marcas, loc="upper right", fontsize=7, framealpha=0.9)


# Seta plana que sai de origem. Usa só as componentes x e y, porque na parte 1 z = 0.
def _seta(eixos, origem: np.ndarray, vetor: np.ndarray, cor: str) -> None:
    eixos.quiver(
        *origem, *vetor[:2], color=cor, angles="xy", scale_units="xy", scale=1, width=0.006
    )


# Um quadro da geração da curva no ângulo θ: o aro, o disco com centro C, o raio CP,
# o ponto de contato T e o traço deixado por P até θ.
def desenhar_rolamento(eixos, cfg: Config, theta: float) -> None:
    h = cfg.hipocicloide
    R, r = h.raio_aro, h.raio_disco
    cores = cfg.cores
    thetas, pontos = _curva(cfg, R, r)
    P = hipocicloide.posicao(R, r, theta)
    C = hipocicloide.centro_do_disco(R, r, theta)
    T = hipocicloide.ponto_de_contato(R, theta)
    tracado = np.vstack([pontos[thetas < theta], P])
    _plano(eixos, cfg, rf"$\theta = {np.degrees(theta):.0f}^\circ$")
    eixos.plot(*pontos.T, color=cores["curva"], lw=0.6, ls=":", alpha=0.5)
    eixos.plot(*tracado.T, color=cores["curva"], lw=1.8)
    eixos.plot(*_circulo(C, r).T, color=cores["disco"], lw=1.4)
    eixos.plot(*np.vstack([C, P]).T, color=cores["disco"], lw=1.0)
    eixos.plot(*C, "o", color=cores["disco"], ms=3)
    eixos.plot(*T, "o", color=cores["aro"], ms=4)
    eixos.plot(*P, "o", color=cores["ponto"], ms=5)
    eixos.text(*(P + 0.06 * R), "$P$", fontsize=9)


# Item 1.1: a hipociclóide completa dentro do aro, com as cúspides marcadas.
def figura_curva(cfg: Config) -> Figure:
    h = cfg.hipocicloide
    R, r = h.raio_aro, h.raio_disco
    figura = Figure(figsize=(6.4, 6.4))
    eixos = figura.subplots()
    _plano(eixos, cfg, f"Hipociclóide com $R = {R:g}$ e $r = {r:g}$")
    eixos.plot(*_curva(cfg, R, r)[1].T, color=cfg.cores["curva"], lw=1.8)
    cuspides = hipocicloide.cuspides(R, r, hipocicloide.voltas(R / r, h.voltas_maximas))
    eixos.plot(*cuspides.T, "o", color=cfg.cores["ponto"], ms=4)
    _legenda(
        eixos,
        [
            (cfg.cores["aro"], "aro de raio $R$"),
            (cfg.cores["curva"], "hipociclóide"),
            (cfg.cores["ponto"], "cúspides"),
        ],
    )
    figura.tight_layout()
    return figura


# Item 1.3: seis quadros da geração, desenhados pela mesma função usada na animação.
def figura_instantaneos(cfg: Config) -> Figure:
    figura = Figure(figsize=(9.6, 6.6))
    for eixos, theta in zip(figura.subplots(2, 3).flat, cfg.hipocicloide.instantaneos):
        desenhar_rolamento(eixos, cfg, theta)
    figura.tight_layout()
    return figura


# Item 1.4: uma hipociclóide para cada razão R/r, mantendo R e calculando r = R / (R/r).
def figura_razoes(cfg: Config) -> Figure:
    h = cfg.hipocicloide
    figura = Figure(figsize=(8.0, 8.0))
    for eixos, razao in zip(figura.subplots(2, 2).flat, h.razoes):
        r = h.raio_aro / razao
        fracao = Fraction(razao).limit_denominator(h.voltas_maximas)
        voltas = "1 volta" if fracao.denominator == 1 else f"{fracao.denominator} voltas"
        razao_tex = (
            rf"\frac{{{fracao.numerator}}}{{{fracao.denominator}}}"
            if fracao.denominator > 1
            else f"{fracao}"
        )
        _plano(eixos, cfg, rf"$\frac{{R}}{{r}} = {razao_tex}$, fecha após {voltas}")
        eixos.plot(*_curva(cfg, h.raio_aro, r)[1].T, color=cfg.cores["curva"], lw=1.4)
    figura.tight_layout()
    return figura


# Item 1.5: em cada ponto escolhido, o círculo osculador, de raio ρ e centro no centro de
# curvatura. É o círculo que melhor acompanha a curva naquele ponto.
def figura_curvatura(cfg: Config, curvaturas: list[hipocicloide.Curvatura]) -> Figure:
    h = cfg.hipocicloide
    cor = cfg.cores["curvatura"]
    figura = Figure(figsize=(6.4, 6.4))
    eixos = figura.subplots()
    limite = 1.08 * max(h.raio_aro, *(np.abs(item.centro).max() for item in curvaturas))
    _plano(eixos, cfg, "Raio de curvatura em diferentes posições", limite)
    eixos.plot(*_curva(cfg, h.raio_aro, h.raio_disco)[1].T, color=cfg.cores["curva"], lw=1.6)
    for indice, item in enumerate(curvaturas, start=1):
        eixos.plot(*_circulo(item.centro, item.raio).T, color=cor, lw=0.7, ls="--")
        eixos.plot(*np.vstack([item.ponto, item.centro]).T, color=cor, lw=0.7)
        eixos.plot(*item.ponto, "o", color=cfg.cores["ponto"], ms=4)
        eixos.plot(*item.centro, "x", color=cor, ms=5)
        eixos.text(*(item.ponto + 0.05 * h.raio_aro), str(indice), fontsize=8)
    _legenda(eixos, [(cfg.cores["curva"], "hipociclóide"), (cor, "círculos osculadores")])
    figura.tight_layout()
    return figura


# Item 1.6: setas dos versores τ e n nos pontos escolhidos, todas com o mesmo comprimento.
def figura_versores(cfg: Config, curvaturas: list[hipocicloide.Curvatura]) -> Figure:
    h = cfg.hipocicloide
    cores = cfg.cores
    comprimento = 0.25 * h.raio_aro
    figura = Figure(figsize=(6.4, 6.4))
    eixos = figura.subplots()
    _plano(eixos, cfg, "Versores tangente e normal principal")
    eixos.plot(*_curva(cfg, h.raio_aro, h.raio_disco)[1].T, color=cores["curva"], lw=1.6)
    for item in curvaturas:
        eixos.plot(*item.ponto, "o", color=cores["ponto"], ms=3)
        _seta(eixos, item.ponto, comprimento * item.tangente, cores["tangente"])
        _seta(eixos, item.ponto, comprimento * item.normal, cores["normal"])
    _legenda(
        eixos,
        [
            (cores["tangente"], r"tangente $\vec{\tau}$"),
            (cores["normal"], r"normal principal $\vec{n}$"),
        ],
    )
    figura.tight_layout()
    return figura


# Fatores de escala das setas de v e a. Fazem o maior vetor de cada tipo ocupar a fração
# de R pedida no TOML, já que v e a não são distâncias e não caberiam na figura.
def escalas_cinematica(
    cfg: Config, cinematicas: list[hipocicloide.Cinematica]
) -> tuple[float, float]:
    h = cfg.hipocicloide
    maior_v = max(np.linalg.norm(item.velocidade) for item in cinematicas)
    maior_a = max(np.linalg.norm(item.aceleracao) for item in cinematicas)
    return h.escala_velocidade * h.raio_aro / maior_v, h.escala_aceleracao * h.raio_aro / maior_a


# Item 1.7: setas de v e a de P em cada instante, multiplicadas pelos fatores de escala.
def figura_cinematica(cfg: Config, cinematicas: list[hipocicloide.Cinematica]) -> Figure:
    h = cfg.hipocicloide
    cores = cfg.cores
    escala_v, escala_a = escalas_cinematica(cfg, cinematicas)
    figura = Figure(figsize=(6.4, 6.4))
    eixos = figura.subplots()
    _plano(eixos, cfg, r"Velocidade e aceleração com $\omega = \pi/60$ rad/s")
    eixos.plot(*_curva(cfg, h.raio_aro, h.raio_disco)[1].T, color=cores["curva"], lw=1.6)
    for item in cinematicas:
        ponto = item.curvatura.ponto
        eixos.plot(*ponto, "o", color=cores["ponto"], ms=4)
        _seta(eixos, ponto, escala_v * item.velocidade, cores["velocidade"])
        _seta(eixos, ponto, escala_a * item.aceleracao, cores["aceleracao"])
        eixos.text(*(ponto + 0.05 * h.raio_aro), f"$t = {item.t:g}$ s", fontsize=8)
    _legenda(
        eixos,
        [
            (cores["velocidade"], r"velocidade $\vec{v}$"),
            (cores["aceleracao"], r"aceleração $\vec{a}$"),
        ],
    )
    figura.tight_layout()
    return figura


# Itens 2.1 e 2.3: a curva C em 3D e, em cada ponto escolhido, as setas de τ, n e b.
def figura_cubica(cfg: Config, triedros: list[cubica.Triedro]) -> Figure:
    c = cfg.cubica
    cores = cfg.cores
    figura, eixos = cena.criar_eixos(cfg.vista)
    pontos = cubica.posicao(np.linspace(c.lambda_minimo, c.lambda_maximo, c.pontos_da_curva))
    eixos.plot(*pontos.T, color=cores["curva"], lw=1.6)
    pontas = []
    for item in triedros:
        cena.marcar_ponto(eixos, item.ponto, cores["ponto"], rf"$\lambda = {item.parametro:g}$")
        for versor, cor, rotulo in (
            (item.tangente, cores["tangente"], r"$\vec{\tau}$"),
            (item.normal, cores["normal"], r"$\vec{n}$"),
            (item.binormal, cores["binormal"], r"$\vec{b}$"),
        ):
            vetor = c.comprimento_versores * versor
            pontas.append(cena.seta(eixos, item.ponto, vetor, cor, rotulo, largura=1.6))
    cena.finalizar(
        eixos, np.vstack([pontos, *pontas]), cfg.vista, r"Curva $\mathcal{C}$ e triedros de Frenet"
    )
    _legenda(
        eixos,
        [
            (cores["curva"], r"curva $\mathcal{C}$"),
            (cores["tangente"], r"tangente $\vec{\tau}$"),
            (cores["normal"], r"normal principal $\vec{n}$"),
            (cores["binormal"], r"binormal $\vec{b}$"),
        ],
    )
    return figura


# Ângulos θ dos quadros de uma animação, igualmente espaçados entre 0 e o ângulo em que a
# curva fecha.
def _angulos_da_animacao(cfg: Config, quantidade: int) -> np.ndarray:
    h = cfg.hipocicloide
    final = 2 * np.pi * hipocicloide.voltas(h.raio_aro / h.raio_disco, h.voltas_maximas)
    return np.linspace(0.0, final, quantidade)


# Item 1.2: grava o vídeo MP4 da geração. Desenha um quadro para cada θ e entrega cada
# quadro ao ffmpeg.
def gravar_animacao(cfg: Config) -> Path:
    h = cfg.hipocicloide
    caminho = Path(cfg.saida_animacao)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    figura = Figure(figsize=(5.0, 5.0))
    eixos = figura.subplots()
    escritor = FFMpegWriter(fps=h.quadros_por_segundo)
    with escritor.saving(figura, str(caminho), dpi=h.dpi_animacao):
        for theta in _angulos_da_animacao(cfg, h.quadros):
            eixos.clear()
            desenhar_rolamento(eixos, cfg, theta)
            escritor.grab_frame()
    return caminho


# Item 1.2 dentro do PDF: os quadros da animação como imagens JPEG, com o mesmo desenho do
# vídeo e menos quadros, para o PDF não ficar pesado.
def quadros_jpeg(cfg: Config) -> list[bytes]:
    h = cfg.hipocicloide
    figura = Figure(figsize=(5.0, 5.0))
    eixos = figura.subplots()
    quadros = []
    for theta in _angulos_da_animacao(cfg, h.quadros_pdf):
        eixos.clear()
        desenhar_rolamento(eixos, cfg, theta)
        arquivo = io.BytesIO()
        figura.savefig(arquivo, format="jpg", dpi=h.dpi_animacao, pil_kwargs={"quality": 85})
        quadros.append(arquivo.getvalue())
    return quadros
