# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Montagem do relatório PDF da Tarefa 2."""

from pathlib import Path

from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer

from ..comum import documento
from .config import Config
from .desenho import FigurasDoCaso
from .sistema import Reducao

TAREFA = "Tarefa Optativa 2"


def _parametros(cfg: Config) -> list[str]:
    """Linhas da capa que resumem a configuração comum aos exemplos."""
    return [
        f"<b>Casos analisados</b>: {len(cfg.casos)}",
        f"<b>Tolerância numérica</b>: {cfg.tolerancia:.3g}",
        f"<b>Paralelepípedo de referência</b>: canto {documento.vetor(cfg.solido.canto)}, "
        f"dimensões {documento.vetor(cfg.solido.dimensoes)}",
    ]


def _tabela_resumo(reducoes: list[Reducao]):
    """Tabela que evidencia a cobertura das categorias pedidas."""
    linhas = [
        [reducao.caso.nome, reducao.tipo]
        for reducao in reducoes
    ]
    return documento.tabela(
        ["Caso", "Caracterização"],
        linhas,
        [7.0 * cm, 9.0 * cm],
    )


def _tabelas_de_entrada(reducao: Reducao) -> list:
    """Tabela de forças e pontos, seguida dos polos e do versor do eixo."""
    caso = reducao.caso
    linhas = [
        [str(indice), documento.vetor(forca), documento.vetor(ponto)]
        for indice, (forca, ponto) in enumerate(zip(caso.forcas, caso.pontos), start=1)
    ]
    tabela_forcas = documento.tabela(
        ["i", "F_i", "P_i"], linhas, [1.0 * cm, 7.5 * cm, 7.5 * cm]
    )
    tabela_elementos = documento.tabela(
        ["Elemento", "Valor"],
        [
            ["Polo Q", documento.vetor(caso.polo_q)],
            ["Polo A", documento.vetor(caso.polo_a)],
            ["Versor u", documento.vetor(caso.versor_u)],
        ],
        [4.0 * cm, 12.0 * cm],
    )
    return [tabela_forcas, Spacer(1, 0.25 * cm), tabela_elementos]


def _tabela_de_resultados(reducao: Reducao):
    """Tabela com as saídas numéricas e geométricas do enunciado."""
    linhas = [
        ["Resultante R", documento.vetor(reducao.resultante)],
        ["Momento M_Q", documento.vetor(reducao.momento_q)],
        ["Momento M_A", documento.vetor(reducao.momento_a)],
        ["Torque no eixo Au", f"{reducao.torque:.6g}"],
        ["Invariante escalar I", f"{reducao.invariante:.6g}"],
        ["Caracterização", reducao.tipo],
    ]
    if reducao.eixo_central is not None and reducao.momento_minimo is not None:
        linhas += [
            [
                "Eixo central",
                f"E = {documento.vetor(reducao.eixo_central.ponto)}, direção = "
                f"{documento.vetor(reducao.eixo_central.direcao)}",
            ],
            ["Momento mínimo M_E", documento.vetor(reducao.momento_minimo)],
        ]
    else:
        linhas += [
            ["Eixo central", "não existe"],
            ["Momento mínimo M_E", "não existe"],
        ]
    return documento.tabela(["Resultado", "Valor"], linhas, [5.0 * cm, 11.0 * cm])


def _pagina_do_caso(reducao: Reducao, estilos: dict) -> list:
    """Conteúdo tabular que antecede as figuras de um caso."""
    return [
        Paragraph(reducao.caso.nome, estilos["secao"]),
        Paragraph(reducao.caso.descricao, estilos["texto"]),
        Spacer(1, 0.25 * cm),
        Paragraph("Dados de entrada", estilos["secao"]),
        *_tabelas_de_entrada(reducao),
        Spacer(1, 0.3 * cm),
        Paragraph("Resultados", estilos["secao"]),
        _tabela_de_resultados(reducao),
        PageBreak(),
    ]


def gerar_pdf(
    cfg: Config,
    reducoes: list[Reducao],
    figuras: list[FigurasDoCaso],
    arquivos: list[Path],
    caminho: str | Path,
) -> Path:
    """Grava o relatório completo da Tarefa 2."""
    if len(reducoes) != len(figuras):
        raise ValueError("cada redução precisa das suas figuras")
    estilos = documento.estilos()
    explicacao = (
        "Para cada sistema de forças, o programa calcula a resultante R, os momentos M_Q e M_A, "
        "o torque no eixo Au e o invariante escalar I. Em seguida caracteriza o sistema "
        "e determina o eixo central e o momento mínimo quando a resultante não é nula."
    )
    conteudo = documento.capa(
        "Redução de sistemas de forças no espaço",
        TAREFA,
        _parametros(cfg),
        explicacao,
        estilos,
    )
    conteudo += [
        Paragraph("Cobertura dos casos", estilos["secao"]),
        Paragraph(
            "Os exemplos abaixo abrangem as quatro categorias do enunciado e os casos particulares "
            "de uma única força, forças concorrentes, forças coplanares e forças paralelas.",
            estilos["texto"],
        ),
        Spacer(1, 0.25 * cm),
        _tabela_resumo(reducoes),
        PageBreak(),
    ]
    numero_da_figura = 1
    for reducao, figuras_do_caso in zip(reducoes, figuras):
        conteudo += _pagina_do_caso(reducao, estilos)
        conteudo += documento.pagina_de_figura(
            figuras_do_caso.reducao,
            f"Figura {numero_da_figura}: {reducao.caso.nome}, redução do sistema",
            "Forças e pontos de aplicação, polos Q e A, eixo Au, resultante e momentos nos polos.",
            cfg.dpi,
            estilos,
        )
        numero_da_figura += 1
        if figuras_do_caso.eixo_central is not None:
            conteudo += documento.pagina_de_figura(
                figuras_do_caso.eixo_central,
                f"Figura {numero_da_figura}: {reducao.caso.nome}, eixo central",
                "Forças, polo Q, momento M_Q, eixo central, resultante e momento mínimo.",
                cfg.dpi,
                estilos,
            )
            numero_da_figura += 1
    return documento.gerar_pdf(TAREFA, conteudo, arquivos, caminho)
