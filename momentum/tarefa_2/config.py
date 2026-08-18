# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Configuração dos sistemas de forças da Tarefa 2."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..comum import cena, vetores

CORES_PADRAO = {
    "forca": "#d62728",
    "resultante": "#9467bd",
    "momento": "#000000",
    "eixo_au": "#1f77b4",
    "eixo_central": "#2ca02c",
    "polo": "#ff7f0e",
    "solido": "#bdbdbd",
}


@dataclass
class Solido:
    """Paralelepípedo que contextualiza os pontos de aplicação."""

    canto: tuple = (0.0, 0.0, 0.0)
    dimensoes: tuple = (4.0, 3.0, 2.0)

    def __post_init__(self) -> None:
        self.canto = np.asarray(self.canto, dtype=float)
        self.dimensoes = np.asarray(self.dimensoes, dtype=float)
        if self.canto.shape != (3,) or self.dimensoes.shape != (3,):
            raise ValueError("o canto e as dimensões do sólido devem ter três componentes")
        if np.any(self.dimensoes <= 0.0):
            raise ValueError("as dimensões do sólido devem ser positivas")


@dataclass
class Caso:
    """Um sistema de forças e os elementos usados na sua redução."""

    nome: str
    descricao: str
    forcas: tuple
    pontos: tuple
    polo_q: tuple
    polo_a: tuple
    versor_u: tuple
    vistas: list | None = None

    def __post_init__(self) -> None:
        self.forcas = np.atleast_2d(np.asarray(self.forcas, dtype=float))
        self.pontos = np.atleast_2d(np.asarray(self.pontos, dtype=float))
        self.polo_q = np.asarray(self.polo_q, dtype=float)
        self.polo_a = np.asarray(self.polo_a, dtype=float)
        self.versor_u = vetores.versor(np.asarray(self.versor_u, dtype=float))
        if self.forcas.ndim != 2 or self.forcas.shape[1:] != (3,):
            raise ValueError("cada força deve ter três componentes")
        if self.pontos.shape != self.forcas.shape:
            raise ValueError("forças e pontos devem ter a mesma quantidade de vetores")
        if self.polo_q.shape != (3,) or self.polo_a.shape != (3,):
            raise ValueError("os polos Q e A devem ter três componentes")
        if len(self.forcas) < 1:
            raise ValueError("cada caso deve ter pelo menos uma força")
        if self.vistas is not None:
            self.vistas = [v if isinstance(v, cena.Vista) else cena.Vista(**v) for v in self.vistas]


@dataclass
class Config:
    """Configuração completa do relatório da Tarefa 2."""

    tolerancia: float = 1e-9
    saida_pdf: str = "saida/tarefa_2.pdf"
    dpi: int = 200
    escala_forca: float = 0.36
    escala_momento: float = 0.28
    comprimento_eixo: float = 1.5
    opacidade_solido: float = 0.14
    solido: Solido | dict = field(default_factory=Solido)
    cores: dict = field(default_factory=dict)
    vistas: list = field(
        default_factory=lambda: [
            {
                "nome": "Perspectiva geral",
                "descricao": "Perspectiva escolhida para identificar forças, polos e momentos.",
                "projecao": "persp",
                "elevacao": 26.0,
                "azimute": -48.0,
            },
            {
                "nome": "Perspectiva do eixo central",
                "descricao": "Perspectiva escolhida para evidenciar a resultante e o momento mínimo.",
                "projecao": "persp",
                "elevacao": 22.0,
                "azimute": -58.0,
            },
        ]
    )
    casos: list = field(default_factory=list)

    def __post_init__(self) -> None:
        self.solido = self.solido if isinstance(self.solido, Solido) else Solido(**self.solido)
        self.cores = CORES_PADRAO | self.cores
        self.vistas = [v if isinstance(v, cena.Vista) else cena.Vista(**v) for v in self.vistas]
        self.casos = [c if isinstance(c, Caso) else Caso(**c) for c in self.casos]
        if not np.isfinite(self.tolerancia) or self.tolerancia <= 0.0:
            raise ValueError("a tolerância deve ser positiva")
        if self.dpi < 1:
            raise ValueError("o dpi deve ser positivo")
        if self.escala_forca <= 0.0 or self.escala_momento <= 0.0:
            raise ValueError("as escalas de desenho devem ser positivas")
        if self.comprimento_eixo <= 0.0:
            raise ValueError("o comprimento do eixo deve ser positivo")
        if not 0.0 < self.opacidade_solido <= 1.0:
            raise ValueError("a opacidade do sólido deve estar em (0, 1]")
        if len(self.vistas) < 2:
            raise ValueError("são necessárias duas vistas, uma para cada tipo de figura")
        if not self.casos:
            raise ValueError("é preciso configurar pelo menos um sistema de forças")


def carregar(caminho: str | Path | None = None) -> Config:
    """Lê o TOML, completando os campos omitidos com os padrões."""
    dados: dict = {}
    if caminho is not None:
        arquivo = Path(caminho)
        if not arquivo.exists():
            raise FileNotFoundError(f"configuração não encontrada: {arquivo}")
        dados = tomllib.loads(arquivo.read_text(encoding="utf-8"))
    return Config(**dados)
