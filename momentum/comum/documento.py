# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Elementos compartilhados dos relatórios em PDF."""

import io
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from matplotlib.figure import Figure
from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name
from reportlab.lib import colors
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
    Table,
    TableStyle,
    XPreformatted,
)

from .. import __version__

AUTOR = "Eduardo Lima Moraes"
ID_USP = "16802140"
DISCIPLINA = "PME0100 - Mecânica I (2026)"
LARGURA_CODIGO = 110
ESTILO_CODIGO = "friendly"


def estilos() -> dict:
    """Estilos tipográficos comuns aos relatórios."""
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
        "arquivo": ParagraphStyle(
            "arquivo", parent=base["Normal"], fontSize=10, leading=14, spaceAfter=6
        ),
        "legenda": ParagraphStyle(
            "legenda", parent=base["Normal"], fontSize=9, leading=12, alignment=TA_CENTER
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName="Courier", fontSize=7.2, leading=8.6
        ),
    }


def vetor(v: np.ndarray) -> str:
    """Representação compacta de um vetor para o relatório."""
    return "(" + ", ".join(f"{c:.6g}" for c in np.asarray(v)) + ")"


def capa(
    subtitulo: str,
    tarefa: str,
    parametros: list[str],
    explicacao: str,
    estilos_do_documento: dict,
) -> list:
    """Página de rosto com parâmetros, explicação e créditos."""
    conteudo = [
        Spacer(1, 3 * cm),
        Paragraph("Momentum", estilos_do_documento["titulo"]),
        Paragraph(subtitulo, estilos_do_documento["subtitulo"]),
        Spacer(1, 1.4 * cm),
        Paragraph(f"{tarefa} de {DISCIPLINA}", estilos_do_documento["subtitulo"]),
        Paragraph(
            "Escola Politécnica da USP, Engenharia de Computação",
            estilos_do_documento["subtitulo"],
        ),
        Spacer(1, 1.4 * cm),
        Paragraph(f"<b>{AUTOR}</b>, ID USP {ID_USP}", estilos_do_documento["subtitulo"]),
        Spacer(1, 1.6 * cm),
        Paragraph("Parâmetros", estilos_do_documento["secao"]),
    ]
    conteudo += [Paragraph(linha, estilos_do_documento["texto"]) for linha in parametros]
    conteudo += [
        Paragraph("O que o programa calcula", estilos_do_documento["secao"]),
        Paragraph(explicacao, estilos_do_documento["texto"]),
        Paragraph("Créditos", estilos_do_documento["secao"]),
        Paragraph(
            f"Programa e figuras por {AUTOR} (ID USP {ID_USP}), com auxílio do "
            "<b>Claude</b> (Anthropic) na escrita do código. "
            f"Momentum {__version__}, distribuído sob a licença GNU GPL v3 ou posterior.",
            estilos_do_documento["texto"],
        ),
        PageBreak(),
    ]
    return conteudo


def pagina_de_figura(
    figura: Figure, titulo: str, texto_da_legenda: str, dpi: int, estilos_do_documento: dict
) -> list:
    """Cria uma página do documento para uma figura e sua legenda."""
    buffer = io.BytesIO()
    figura.savefig(buffer, format="png", dpi=dpi)
    buffer.seek(0)
    largura = 17 * cm
    altura = largura * figura.get_figheight() / figura.get_figwidth()
    return [
        Spacer(1, 1.6 * cm),
        Paragraph(titulo, estilos_do_documento["secao"]),
        Image(buffer, width=largura, height=altura),
        Spacer(1, 0.2 * cm),
        Paragraph(texto_da_legenda, estilos_do_documento["legenda"]),
        PageBreak(),
    ]


def tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[float]) -> Table:
    """Monta uma tabela numérica legível em uma página A4."""
    dados = [cabecalho] + linhas
    resultado = Table(dados, colWidths=larguras, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEADING", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#b0b0b0")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if len(cabecalho) > 1:
        estilo.append(("ALIGN", (1, 0), (-1, -1), "RIGHT"))
    resultado.setStyle(TableStyle(estilo))
    return resultado


def codigo_colorido(fonte: str, nome: str) -> str:
    """Converte código em marcação colorida para o ReportLab."""
    estilo = get_style_by_name(ESTILO_CODIGO)
    linhas = []
    for linha in fonte.expandtabs(4).splitlines():
        linhas += textwrap.wrap(
            linha, LARGURA_CODIGO, subsequent_indent="    ", drop_whitespace=False
        ) or [""]

    partes = []
    for tipo, valor in lex("\n".join(linhas), get_lexer_for_filename(nome)):
        cor = estilo.style_for_token(tipo)["color"]
        for indice, pedaco in enumerate(valor.split("\n")):
            if indice:
                partes.append("\n")
            if pedaco:
                texto = escape(pedaco)
                partes.append(f'<font color="#{cor}">{texto}</font>' if cor else texto)
    return "".join(partes)


def paginas_do_codigo(arquivos: list[Path], estilos_do_documento: dict) -> list:
    """Anexa a listagem de todos os arquivos que geraram o documento."""
    conteudo = [
        Paragraph("Código-fonte", estilos_do_documento["secao"]),
        Paragraph(
            "Listagem completa do programa que gerou as figuras deste documento.",
            estilos_do_documento["texto"],
        ),
        Spacer(1, 0.3 * cm),
    ]
    for arquivo in arquivos:
        fonte = arquivo.read_text(encoding="utf-8")
        conteudo += [
            CondPageBreak(3 * cm),
            Paragraph(f"<b>{escape(arquivo.name)}</b>", estilos_do_documento["arquivo"]),
            XPreformatted(codigo_colorido(fonte, arquivo.name), estilos_do_documento["codigo"]),
            Spacer(1, 0.5 * cm),
        ]
    return conteudo


def rodape_de(tarefa: str):
    """Devolve o callback que desenha o rodapé do relatório."""

    def rodape(canvas, documento) -> None:
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillGray(0.4)
        canvas.drawString(2 * cm, 1.2 * cm, f"Momentum, {tarefa}, {AUTOR} ({ID_USP})")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(documento.page))
        canvas.restoreState()

    return rodape


def gerar_pdf(tarefa: str, conteudo: list, arquivos: list[Path], caminho: str | Path) -> Path:
    """Grava o conteúdo e o código-fonte em um relatório PDF."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    documento = SimpleDocTemplate(
        str(caminho),
        pagesize=A4,
        title=f"Momentum - {tarefa}",
        author=AUTOR,
        subject=DISCIPLINA,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )
    todo_o_conteudo = conteudo + paginas_do_codigo(arquivos, estilos())
    rodape = rodape_de(tarefa)
    documento.build(todo_o_conteudo, onFirstPage=rodape, onLaterPages=rodape)
    return caminho
