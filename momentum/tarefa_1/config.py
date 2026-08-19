# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Configuração da Tarefa 1, lida de um arquivo TOML."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from ..comum import cena

CORES_PADRAO = {
    "forca": "#d62728",
    "momento": "#000000",
    "raio": "#2ca02c",
    "fecho": "#1f77b4",
    "ponto": "#7f7f7f",
}


@dataclass
class Vista(cena.Vista):
    """Vista da Tarefa 1, que também pode ser axial."""

    axial: bool = False


@dataclass
class Config:
    """Parâmetros da simulação e da visualização."""

    forca: tuple = (3.0, -1.0, 2.0)
    ponto: tuple = (1.0, 1.0, 0.5)
    planos: int = 3
    espacamento_planos: float = 4.5
    raios: tuple = (1.4, 2.8)
    passo_angular: float = 60.0
    escala_forca: float = 1.0
    escala_momento: float = 0.22
    comprimento_linha_acao: float = 14.0
    cores: dict = field(default_factory=dict)
    vistas: list = field(
        default_factory=lambda: [
            {
                "nome": "Perspectiva isométrica",
                "descricao": "Câmera em perspectiva sobre a diagonal do primeiro octante.",
                "projecao": "persp",
                "elevacao": 35.264,
                "azimute": -45.0,
            },
            {
                "nome": "Projeção ortográfica",
                "descricao": "Projeção paralela: segmentos paralelos permanecem paralelos.",
                "projecao": "ortho",
                "elevacao": 25.0,
                "azimute": -85.0,
            },
            {
                "nome": "Vista axial",
                "descricao": "Câmera alinhada com a linha de ação de F, que aparece como um ponto.",
                "projecao": "ortho",
                "axial": True,
                "zoom": 1.32,
            },
        ]
    )
    saida_pdf: str = "saida/tarefa_1.pdf"
    dpi: int = 200

    def __post_init__(self) -> None:
        self.forca = np.asarray(self.forca, dtype=float)
        self.ponto = np.asarray(self.ponto, dtype=float)
        self.raios = tuple(float(r) for r in self.raios)
        self.cores = CORES_PADRAO | self.cores
        self.vistas = [v if isinstance(v, Vista) else Vista(**v) for v in self.vistas]
        self.validar()

    def validar(self) -> None:
        """Rejeita configurações que não produzem uma figura válida."""
        if self.forca.shape != (3,) or self.ponto.shape != (3,):
            raise ValueError("a força e o ponto devem ter três componentes")
        if np.allclose(self.forca, 0.0):
            raise ValueError("a força não pode ser nula: ela define a linha de ação")
        if self.planos < 1:
            raise ValueError("é preciso pelo menos um plano de amostragem")
        if not self.raios or any(r <= 0.0 for r in self.raios):
            raise ValueError("os raios devem ser positivos")
        if not 0.0 < self.passo_angular <= 360.0:
            raise ValueError("o passo angular deve estar em (0, 360] graus")


def carregar(caminho: str | Path | None = None) -> Config:
    """Lê o TOML, completando os campos omitidos com os padrões."""
    dados: dict = {}
    if caminho is not None:
        arquivo = Path(caminho)
        if not arquivo.exists():
            raise FileNotFoundError(f"configuração não encontrada: {arquivo}")
        dados = tomllib.loads(arquivo.read_text(encoding="utf-8"))
    return Config(**dados)
