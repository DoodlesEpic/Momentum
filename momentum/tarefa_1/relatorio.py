# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Montagem do relatório PDF da Tarefa 1."""

from pathlib import Path

import numpy as np
from matplotlib.figure import Figure

from ..comum import documento
from .config import Config

TAREFA = "Tarefa Optativa 1"


def _parametros(cfg: Config) -> list[str]:
    """Linhas da capa que descrevem a configuração usada."""
    return [
        f"<b>Força F</b> = {documento.vetor(cfg.forca)} de módulo {np.linalg.norm(cfg.forca):.4g}",
        f"<b>Ponto de aplicação P</b> = {documento.vetor(cfg.ponto)}",
        f"<b>Planos normais à linha de ação</b>: {cfg.planos}, espaçados de "
        f"{cfg.espacamento_planos:g}",
        f"<b>Raios dos pontos O em cada plano</b>: {documento.vetor(np.array(cfg.raios))}",
        f"<b>Passo angular entre as direções</b>: {cfg.passo_angular:g}°",
        f"<b>Escalas de desenho</b>: força {cfg.escala_forca:g}, momento "
        f"{cfg.escala_momento:g}",
    ]


def gerar_pdf(
    cfg: Config, figuras: list[Figure], arquivos: list[Path], caminho: str | Path
) -> Path:
    """Grava a capa, as figuras e o código-fonte da Tarefa 1."""
    estilos = documento.estilos()
    explicacao = (
        "Em <b>vermelho</b>, a força F e sua linha de ação. Em <b>preto</b>, os vetores "
        "momento M(O) = (P - O) × F, desenhados a partir de cada ponto O. Em "
        "<b>verde tracejado</b>, o segmento que liga O ao ponto Q, pé da perpendicular "
        "baixada de O sobre a linha de ação. Em <b>azul tracejado</b>, o segmento que liga "
        "a extremidade de M(O) ao mesmo ponto Q. Os pontos O pertencem a planos normais à "
        "linha de ação, equiespaçados entre si, e em cada plano as direções de O são "
        f"separadas por ângulos de {cfg.passo_angular:g}°."
    )
    conteudo = documento.capa(
        "Campo de momentos de uma força no espaço",
        TAREFA,
        _parametros(cfg),
        explicacao,
        estilos,
    )
    for indice, (vista, figura) in enumerate(zip(cfg.vistas, figuras), start=1):
        conteudo += documento.pagina_de_figura(
            figura,
            f"Figura {indice}: {vista.nome}",
            vista.descricao,
            cfg.dpi,
            estilos,
        )
    return documento.gerar_pdf(TAREFA, conteudo, arquivos, caminho)
