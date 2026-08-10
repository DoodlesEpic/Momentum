# Momentum - visualização do campo de momentos de uma força
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior; veja o arquivo LICENSE.

"""Configuração do programa, lida de um arquivo TOML."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

CORES_PADRAO = {
    "forca": "#d62728",  # força e linha de ação (vermelho)
    "momento": "#000000",  # vetores M(O) (preto)
    "raio": "#2ca02c",  # tracejado de O até Q (verde)
    "fecho": "#1f77b4",  # tracejado da ponta de M(O) até Q (azul)
    "ponto": "#7f7f7f",  # marcadores dos pontos O e Q
}


@dataclass
class Vista:
    """Uma das visualizações geradas."""

    nome: str
    descricao: str = ""
    projecao: str = "persp"  # "persp" (perspectiva) ou "ortho" (ortográfica)
    elevacao: float = 30.0
    azimute: float = -60.0
    axial: bool = False  # se verdadeiro, alinha a câmera com a linha de ação de F


@dataclass
class Config:
    """Parâmetros da simulação e da visualização."""

    # Força e ponto de aplicação
    forca: tuple = (3.0, 1.0, 2.0)
    ponto: tuple = (1.0, 2.0, 0.5)

    # Amostragem dos pontos O
    planos: int = 3  # quantidade de planos normais à linha de ação
    espacamento_planos: float = 2.0  # distância entre planos consecutivos
    raios: tuple = (1.5, 3.0)  # distâncias de O até a linha de ação
    passo_angular: float = 60.0  # ângulo entre direções vizinhas, em graus

    # Escalas de desenho (apenas visuais, não alteram o cálculo)
    escala_forca: float = 1.0
    escala_momento: float = 0.25
    comprimento_linha_acao: float = 9.0

    cores: dict = field(default_factory=dict)

    vistas: list = field(
        default_factory=lambda: [
            {
                "nome": "Perspectiva isométrica",
                "descricao": "Câmera em perspectiva sobre a diagonal do primeiro octante.",
                "projecao": "persp",
                "elevacao": 35.264,
                "azimute": 45.0,
            },
            {
                "nome": "Projeção ortográfica",
                "descricao": "Projeção paralela: segmentos paralelos permanecem paralelos.",
                "projecao": "ortho",
                "elevacao": 22.0,
                "azimute": -55.0,
            },
            {
                "nome": "Vista axial",
                "descricao": "Câmera alinhada com a linha de ação de F, que aparece como um ponto.",
                "projecao": "ortho",
                "axial": True,
            },
        ]
    )

    # Saída
    saida_pdf: str = "saida/momentum.pdf"
    dpi: int = 200

    def __post_init__(self) -> None:
        self.forca = np.asarray(self.forca, dtype=float)
        self.ponto = np.asarray(self.ponto, dtype=float)
        self.raios = tuple(float(r) for r in self.raios)
        self.cores = CORES_PADRAO | self.cores  # cores omitidas mantêm o padrão
        self.vistas = [v if isinstance(v, Vista) else Vista(**v) for v in self.vistas]
        self.validar()

    def validar(self) -> None:
        """Rejeita configurações que não produzem uma figura válida."""
        if np.allclose(self.forca, 0.0):
            raise ValueError("a força não pode ser nula: ela define a linha de ação")
        if self.planos < 1:
            raise ValueError("é preciso pelo menos um plano de amostragem")
        if not self.raios or any(r <= 0.0 for r in self.raios):
            raise ValueError("os raios devem ser positivos")
        if not 0.0 < self.passo_angular <= 360.0:
            raise ValueError("o passo angular deve estar em (0, 360] graus")


def carregar(caminho: str | Path | None = None) -> Config:
    """Lê a configuração do arquivo TOML, completando o que faltar com os padrões."""
    dados: dict = {}
    if caminho is not None:
        arquivo = Path(caminho)
        if not arquivo.exists():
            raise FileNotFoundError(f"configuração não encontrada: {arquivo}")
        dados = tomllib.loads(arquivo.read_text(encoding="utf-8"))
    return Config(**dados)
