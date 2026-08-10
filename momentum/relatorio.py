# Momentum - visualização do campo de momentos de uma força
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior; veja o arquivo LICENSE.

"""Montagem do PDF com as figuras, o código-fonte e os créditos."""

import io
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from matplotlib.figure import Figure
from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    CondPageBreak,
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    XPreformatted,
)

from . import __version__
from .config import Config

AUTOR = "Eduardo Lima Moraes"
ID_USP = "16802140"
DISCIPLINA = "PME0100 - Mecânica I (2026)"
TAREFA = "Tarefa Optativa 1"

LARGURA_CODIGO = 110  # colunas por linha na listagem do código
ESTILO_CODIGO = "friendly"


def _estilos() -> dict:
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "titulo", parent=base["Title"], fontSize=26, leading=30, spaceAfter=6
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base["Normal"], fontSize=13, leading=18, alignment=TA_CENTER
        ),
        "secao": ParagraphStyle(
            "secao", parent=base["Heading2"], fontSize=13, leading=16, spaceBefore=10, spaceAfter=6
        ),
        "texto": ParagraphStyle(
            "texto", parent=base["Normal"], fontSize=10, leading=14, spaceAfter=3
        ),
        "arquivo": ParagraphStyle(  # nome do arquivo na listagem, colado ao seu código
            "arquivo",
            parent=base["Normal"],
            fontSize=10,
            leading=14,
            spaceAfter=6,
        ),
        "legenda": ParagraphStyle(
            "legenda", parent=base["Normal"], fontSize=9, leading=12, alignment=TA_CENTER
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=8.6
        ),
    }


def _vetor(v: np.ndarray) -> str:
    return "(" + ", ".join(f"{c:g}" for c in v) + ")"


def _capa(cfg: Config, estilos: dict) -> list:
    """Página de rosto: identificação, parâmetros usados e créditos."""
    F, P = cfg.forca, cfg.ponto
    parametros = [
        f"<b>Força F</b> = {_vetor(F)} &nbsp;&nbsp; (módulo {np.linalg.norm(F):.4g})",
        f"<b>Ponto de aplicação P</b> = {_vetor(P)}",
        f"<b>Planos normais à linha de ação</b>: {cfg.planos}, "
        f"espaçados de {cfg.espacamento_planos:g}",
        f"<b>Raios dos pontos O em cada plano</b>: {_vetor(np.array(cfg.raios))}",
        f"<b>Passo angular entre as direções</b>: {cfg.passo_angular:g}°",
        f"<b>Escalas de desenho</b>: força {cfg.escala_forca:g}, "
        f"momento {cfg.escala_momento:g}",
    ]

    conteudo = [
        Spacer(1, 3 * cm),
        Paragraph("Momentum", estilos["titulo"]),
        Paragraph("Campo de momentos de uma força no espaço", estilos["subtitulo"]),
        Spacer(1, 1.4 * cm),
        Paragraph(f"{TAREFA} — {DISCIPLINA}", estilos["subtitulo"]),
        Paragraph("Escola Politécnica da USP — Engenharia de Computação", estilos["subtitulo"]),
        Spacer(1, 1.4 * cm),
        Paragraph(f"<b>{AUTOR}</b> — ID USP {ID_USP}", estilos["subtitulo"]),
        Spacer(1, 1.6 * cm),
        Paragraph("Parâmetros da figura", estilos["secao"]),
    ]
    conteudo += [Paragraph(linha, estilos["texto"]) for linha in parametros]
    conteudo += [
        Paragraph("O que cada figura mostra", estilos["secao"]),
        Paragraph(
            "Em <b>vermelho</b>, a força F e sua linha de ação. Em <b>preto</b>, os vetores "
            "momento M(O) = (P − O) × F, desenhados a partir de cada ponto O. Em "
            "<b>verde tracejado</b>, o segmento que liga O ao ponto Q, pé da perpendicular "
            "baixada de O sobre a linha de ação. Em <b>azul tracejado</b>, o segmento que liga "
            "a extremidade de M(O) ao mesmo ponto Q. Os pontos O pertencem a planos normais à "
            "linha de ação, equiespaçados entre si, e em cada plano as direções de O são "
            f"separadas por ângulos de {cfg.passo_angular:g}°.",
            estilos["texto"],
        ),
        Paragraph("Créditos", estilos["secao"]),
        Paragraph(
            f"Programa e figuras por {AUTOR} (ID USP {ID_USP}), com auxílio do "
            "<b>Claude</b> (Anthropic) na escrita do código. "
            f"Momentum {__version__}, distribuído sob a licença GNU GPL v3 ou posterior.",
            estilos["texto"],
        ),
        PageBreak(),
    ]
    return conteudo


def _paginas_das_figuras(cfg: Config, figuras: list[Figure], estilos: dict) -> list:
    """Uma figura por página, com o nome e a descrição da vista."""
    conteudo = []
    for indice, (vista, figura) in enumerate(zip(cfg.vistas, figuras), start=1):
        buffer = io.BytesIO()
        figura.savefig(buffer, format="png", dpi=cfg.dpi)
        buffer.seek(0)
        largura = 17 * cm
        altura = largura * figura.get_figheight() / figura.get_figwidth()
        conteudo += [
            Spacer(1, 1.6 * cm),  # aproxima a figura do centro vertical da página
            Paragraph(f"Figura {indice} — {vista.nome}", estilos["secao"]),
            Image(buffer, width=largura, height=altura),
            Spacer(1, 0.2 * cm),
            Paragraph(vista.descricao, estilos["legenda"]),
            PageBreak(),
        ]
    return conteudo


def _codigo_colorido(fonte: str, nome: str) -> str:
    """Converte o código em marcação colorida para o ReportLab, usando o Pygments."""
    estilo = get_style_by_name(ESTILO_CODIGO)
    # Quebra as linhas longas para que nada extrapole a largura da página.
    linhas = []
    for linha in fonte.expandtabs(4).splitlines():
        linhas += textwrap.wrap(
            linha, LARGURA_CODIGO, subsequent_indent="    ", drop_whitespace=False
        ) or [""]

    partes = []
    for tipo, valor in lex("\n".join(linhas), get_lexer_for_filename(nome)):
        cor = estilo.style_for_token(tipo)["color"]
        # Um trecho pode conter quebras de linha; a marcação é aplicada linha a linha.
        for indice, pedaco in enumerate(valor.split("\n")):
            if indice:
                partes.append("\n")
            if pedaco:
                texto = escape(pedaco)
                partes.append(f'<font color="#{cor}">{texto}</font>' if cor else texto)
    return "".join(partes)


def _paginas_do_codigo(arquivos: list[Path], estilos: dict) -> list:
    conteudo = [
        Paragraph("Código-fonte", estilos["secao"]),
        Paragraph(
            "Listagem completa do programa que gerou as figuras deste documento.",
            estilos["texto"],
        ),
        Spacer(1, 0.3 * cm),
    ]
    for arquivo in arquivos:
        fonte = arquivo.read_text(encoding="utf-8")
        conteudo += [
            # Evita que o nome do arquivo fique sozinho no pé da página.
            CondPageBreak(3 * cm),
            Paragraph(f"<b>{escape(arquivo.name)}</b>", estilos["arquivo"]),
            XPreformatted(_codigo_colorido(fonte, arquivo.name), estilos["codigo"]),
            Spacer(1, 0.5 * cm),
        ]
    return conteudo


def _rodape(canvas, documento) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillGray(0.4)
    canvas.drawString(2 * cm, 1.2 * cm, f"Momentum — {TAREFA} — {AUTOR} ({ID_USP})")
    canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(documento.page))
    canvas.restoreState()


def gerar_pdf(
    cfg: Config, figuras: list[Figure], arquivos: list[Path], caminho: str | Path
) -> Path:
    """Grava o PDF com a capa, as figuras e o código-fonte."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    estilos = _estilos()
    documento = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        title=f"Momentum — {TAREFA}",
        author=AUTOR,
        subject=DISCIPLINA,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    conteudo = (
        _capa(cfg, estilos)
        + _paginas_das_figuras(cfg, figuras, estilos)
        + _paginas_do_codigo(arquivos, estilos)
    )
    documento.build(conteudo, onFirstPage=_rodape, onLaterPages=_rodape)
    return caminho
