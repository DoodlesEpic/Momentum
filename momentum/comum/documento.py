# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Elementos compartilhados dos relatórios em PDF."""

import io
import textwrap
from pathlib import Path
from xml.sax.saxutils import escape

import matplotlib
import numpy as np
from matplotlib.figure import Figure
from pygments import lex
from pygments.lexers import get_lexer_for_filename
from pygments.styles import get_style_by_name
from pypdf import PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
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
FONTE_UNICODE = "DejaVuSans"
FONTE_CODIGO = "DejaVuSansMono"


# Registra a fonte DejaVu, que vem com o matplotlib, porque as fontes padrão do PDF não têm
# letras gregas. As quatro variantes permitem usar <b> e <i> nos textos.
def _registrar_fontes() -> None:
    pasta = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    for variante, negrito, italico in (
        ("", 0, 0),
        ("-Bold", 1, 0),
        ("-Oblique", 0, 1),
        ("-BoldOblique", 1, 1),
    ):
        nome = FONTE_UNICODE + variante
        pdfmetrics.registerFont(TTFont(nome, pasta / f"{nome}.ttf"))
        addMapping(FONTE_UNICODE, negrito, italico, nome)
    pdfmetrics.registerFont(TTFont(FONTE_CODIGO, pasta / f"{FONTE_CODIGO}.ttf"))


_registrar_fontes()


# Estilos de texto comuns aos relatórios. Todos usam a DejaVu, menos o código, que usa
# a versão monoespaçada dela.
def estilos() -> dict:
    base = getSampleStyleSheet()
    negrito = FONTE_UNICODE + "-Bold"
    return {
        "titulo": ParagraphStyle(
            "titulo", parent=base["Title"], fontName=negrito, fontSize=26, leading=30, spaceAfter=6
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo",
            parent=base["Normal"],
            fontName=FONTE_UNICODE,
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
        ),
        "secao": ParagraphStyle(
            "secao",
            parent=base["Heading2"],
            fontName=negrito,
            fontSize=13,
            leading=16,
            spaceBefore=10,
            spaceAfter=6,
        ),
        "texto": ParagraphStyle(
            "texto",
            parent=base["Normal"],
            fontName=FONTE_UNICODE,
            fontSize=10,
            leading=14,
            spaceAfter=3,
        ),
        "arquivo": ParagraphStyle(
            "arquivo",
            parent=base["Normal"],
            fontName=FONTE_UNICODE,
            fontSize=10,
            leading=14,
            spaceAfter=6,
        ),
        "legenda": ParagraphStyle(
            "legenda",
            parent=base["Normal"],
            fontName=FONTE_UNICODE,
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
        ),
        "codigo": ParagraphStyle(
            "codigo", parent=base["Code"], fontName=FONTE_CODIGO, fontSize=7.2, leading=8.6
        ),
    }


# Escreve um vetor como (x, y, z) com até seis algarismos significativos.
def vetor(v: np.ndarray) -> str:
    return "(" + ", ".join(f"{c:.6g}" for c in np.asarray(v)) + ")"


# Página de rosto com título, autor, parâmetros, explicação e créditos. A partir da
# Tarefa 5 o professor dispensou o crédito ao Claude, que então pode ser omitido.
def capa(
    subtitulo: str,
    tarefa: str,
    parametros: list[str],
    explicacao: str,
    estilos_do_documento: dict,
    credito_ao_claude: bool = True,
) -> list:
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
            f"Programa e figuras por {AUTOR} (ID USP {ID_USP})"
            + (
                ", com auxílio do <b>Claude</b> (Anthropic) na escrita do código"
                if credito_ao_claude
                else ""
            )
            + f". Momentum {__version__}, distribuído sob a licença GNU GPL v3 ou posterior.",
            estilos_do_documento["texto"],
        ),
        PageBreak(),
    ]
    return conteudo


# Página com o título, a figura do matplotlib convertida em imagem PNG e a legenda.
def pagina_de_figura(
    figura: Figure, titulo: str, texto_da_legenda: str, dpi: int, estilos_do_documento: dict
) -> list:
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


# Tabela com cabeçalho cinza e grade fina. A primeira coluna fica à esquerda e as demais,
# numéricas, à direita.
def tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[float]) -> Table:
    dados = [cabecalho] + linhas
    resultado = Table(dados, colWidths=larguras, repeatRows=1, hAlign="LEFT")
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6e6e6")),
        ("FONTNAME", (0, 0), (-1, -1), FONTE_UNICODE),
        ("FONTNAME", (0, 0), (-1, 0), FONTE_UNICODE + "-Bold"),
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


# Colore o código-fonte com o pygments e quebra as linhas longas para caberem na página.
def codigo_colorido(fonte: str, nome: str) -> str:
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


# Páginas finais com a listagem colorida de cada arquivo que gerou o documento.
def paginas_do_codigo(arquivos: list[Path], estilos_do_documento: dict) -> list:
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


# Cria a função que o ReportLab chama em cada página para escrever o rodapé com a tarefa,
# o autor e o número da página.
def rodape_de(tarefa: str):
    def rodape(canvas, documento) -> None:
        canvas.saveState()
        canvas.setFont(FONTE_UNICODE, 8)
        canvas.setFillGray(0.4)
        canvas.drawString(2 * cm, 1.2 * cm, f"Momentum, {tarefa}, {AUTOR} ({ID_USP})")
        canvas.drawRightString(A4[0] - 2 * cm, 1.2 * cm, str(documento.page))
        canvas.restoreState()

    return rodape


# Grava o PDF em A4 com o conteúdo da tarefa, seguido da listagem do código-fonte.
def gerar_pdf(tarefa: str, conteudo: list, arquivos: list[Path], caminho: str | Path) -> Path:
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


# Anexa um arquivo, como o vídeo da Tarefa 5, a um PDF já gravado. O anexo aparece no
# painel de anexos, o ícone de clipe, de leitores como o Acrobat e o Firefox.
def anexar(caminho_pdf: str | Path, arquivo: str | Path) -> None:
    arquivo = Path(arquivo)
    escritor = PdfWriter(clone_from=caminho_pdf)
    escritor.add_attachment(arquivo.name, arquivo.read_bytes())
    escritor.write(caminho_pdf)
