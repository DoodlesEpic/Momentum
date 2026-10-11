# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Configuração da hipociclóide e da curva (λ, λ², λ³) da Tarefa 5."""

import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..comum import cena

CORES_PADRAO = {
    "aro": "#7f7f7f",
    "disco": "#1f77b4",
    "curva": "#d62728",
    "ponto": "#000000",
    "tangente": "#2ca02c",
    "normal": "#9467bd",
    "binormal": "#ff7f0e",
    "velocidade": "#2ca02c",
    "aceleracao": "#9467bd",
    "curvatura": "#17becf",
}


# Parte 1: disco de raio r rolando dentro de um aro de raio R. Os ângulos θ vêm em graus
# no TOML e são convertidos para radianos, a unidade que o numpy usa.
@dataclass
class Hipocicloide:
    raio_aro: float = 3.0
    raio_disco: float = 1.0
    razoes: tuple = (3.0, 4.0, 6.0, 2.5)
    voltas_maximas: int = 12
    instantaneos: tuple = (0.0, 50.0, 110.0, 180.0, 260.0, 330.0)
    posicoes_curvatura: tuple = (15.0, 60.0, 100.0, 230.0)
    posicoes_versores: tuple = (20.0, 60.0, 100.0, 140.0, 180.0, 220.0, 260.0, 300.0, 340.0)
    omega: float = math.pi / 60
    instantes: tuple = (10.0, 20.0, 35.0)
    pontos_da_curva: int = 2000
    quadros: int = 180
    quadros_por_segundo: int = 30
    quadros_pdf: int = 90
    quadros_por_segundo_pdf: int = 15
    dpi_animacao: int = 100
    escala_velocidade: float = 0.4
    escala_aceleracao: float = 0.4

    # Converte os ângulos e recusa raios que não formam uma hipociclóide com curvatura finita.
    def __post_init__(self) -> None:
        self.instantaneos = np.radians(self.instantaneos)
        self.posicoes_curvatura = np.radians(self.posicoes_curvatura)
        self.posicoes_versores = np.radians(self.posicoes_versores)
        if not 0.0 < self.raio_disco < self.raio_aro:
            raise ValueError("os raios devem satisfazer 0 < r < R")
        if math.isclose(self.raio_aro, 2 * self.raio_disco):
            raise ValueError(
                "com R = 2r a hipociclóide é um segmento e o raio de curvatura é infinito"
            )
        if min(self.razoes) <= 1.0:
            raise ValueError("as razões R/r devem ser maiores que 1")


# Parte 2: trecho desenhado da curva (λ, λ², λ³) e os três valores de λ analisados.
@dataclass
class Cubica:
    lambda_minimo: float = -1.3
    lambda_maximo: float = 1.3
    parametros: tuple = (-1.0, 0.5, 1.2)
    comprimento_versores: float = 0.75
    pontos_da_curva: int = 400

    # Recusa λ = 0, que o enunciado exclui.
    def __post_init__(self) -> None:
        if 0.0 in self.parametros:
            raise ValueError("o enunciado pede λ diferente de zero")


# Configuração completa: arquivos de saída, as duas partes, as cores e a vista 3D da parte 2.
@dataclass
class Config:
    saida_pdf: str = "saida/tarefa_5.pdf"
    saida_animacao: str = "saida/tarefa_5_hipocicloide.mp4"
    dpi: int = 200
    hipocicloide: Hipocicloide | dict = field(default_factory=Hipocicloide)
    cubica: Cubica | dict = field(default_factory=Cubica)
    cores: dict = field(default_factory=dict)
    vista: cena.Vista | dict = field(
        default_factory=lambda: {
            "nome": "Perspectiva da curva",
            "descricao": "Perspectiva escolhida para separar os três versores de cada triedro.",
            "elevacao": 24.0,
            "azimute": -62.0,
        }
    )

    # Transforma as tabelas lidas do TOML nas classes acima e completa as cores que faltarem.
    def __post_init__(self) -> None:
        if isinstance(self.hipocicloide, dict):
            self.hipocicloide = Hipocicloide(**self.hipocicloide)
        if isinstance(self.cubica, dict):
            self.cubica = Cubica(**self.cubica)
        if isinstance(self.vista, dict):
            self.vista = cena.Vista(**self.vista)
        self.cores = CORES_PADRAO | self.cores


# Lê o arquivo TOML. Os campos que não estiverem nele ficam com os valores padrão acima.
def carregar(caminho: str | Path | None = None) -> Config:
    dados: dict = {}
    if caminho is not None:
        arquivo = Path(caminho)
        if not arquivo.exists():
            raise FileNotFoundError(f"configuração não encontrada: {arquivo}")
        dados = tomllib.loads(arquivo.read_text(encoding="utf-8"))
    return Config(**dados)
