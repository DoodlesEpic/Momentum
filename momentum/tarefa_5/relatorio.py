# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Montagem do relatório PDF da Tarefa 5."""

from pathlib import Path

import numpy as np
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, Spacer

from ..comum import documento
from . import desenho
from .config import Config
from .cubica import Triedro
from .hipocicloide import Cinematica, Curvatura

TAREFA = "Tarefa Optativa 5"
ESTILOS = documento.estilos()


# Página de uma figura, com os trechos entre $ do título e da legenda desenhados como fórmulas.
def _pagina_de_figura(cfg: Config, figura, titulo: str, legenda: str) -> list:
    titulo = documento.com_formulas(titulo, 13)
    legenda = documento.com_formulas(legenda, 9)
    return documento.pagina_de_figura(figura, titulo, legenda, cfg.dpi, ESTILOS)


# Parágrafo de texto em que os trechos entre $ são desenhados como fórmulas.
def _texto(texto: str) -> Paragraph:
    return Paragraph(documento.com_formulas(texto), ESTILOS["texto"])


# Escreve um número com no máximo três casas decimais, sem zeros sobrando à direita.
# Somar 0.0 troca o -0 por 0 quando um valor muito pequeno e negativo é arredondado.
def _numero(valor: float) -> str:
    return f"{round(float(valor), 3) + 0.0:g}"


# Escreve um vetor como (x, y, z) com cada componente arredondada por _numero.
def _vetor(vetor: np.ndarray) -> str:
    return "(" + ", ".join(_numero(componente) for componente in vetor) + ")"


# Escreve um ângulo θ, guardado em radianos, em graus.
def _graus(theta: float) -> str:
    return _numero(np.degrees(theta)) + "°"


# Tabela com o cabeçalho em notação matemática e larguras de coluna em centímetros.
def _tabela(cabecalho: list[str], linhas: list[list[str]], larguras: list[float]):
    titulos = [
        Paragraph(documento.com_formulas(titulo, 8), ESTILOS["cabecalho"]) for titulo in cabecalho
    ]
    return documento.tabela(titulos, linhas, [largura * cm for largura in larguras])


# Linhas da capa que resumem os dados de entrada das duas partes.
def _parametros(cfg: Config) -> list[str]:
    h = cfg.hipocicloide
    c = cfg.cubica
    linhas = [
        f"<b>Aro e disco</b>: $R = {_numero(h.raio_aro)}$ e $r = {_numero(h.raio_disco)}$",
        f"<b>Razões $R/r$ dos exemplos</b>: {', '.join(_numero(razao) for razao in h.razoes)}",
        rf"<b>Lei horária</b>: $\theta(t) = \omega t$, com "
        rf"$\omega = \pi/60 \approx {_numero(h.omega)}$ rad/s",
        f"<b>Instantes</b>: {', '.join(f'$t = {_numero(t)}$ s' for t in h.instantes)}",
        rf"<b>Curva $\mathcal{{C}}$</b>: $\lambda$ de {_numero(c.lambda_minimo)} a "
        rf"{_numero(c.lambda_maximo)}, triedros em $\lambda$ = "
        + ", ".join(_numero(valor) for valor in c.parametros),
    ]
    return [documento.com_formulas(linha) for linha in linhas]


# Texto e tabelas da parte 1: equações da curva, procedimento das notas de aula, raio de
# curvatura (1.5), versores (1.6) e velocidade e aceleração (1.7).
def _parte_1(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
) -> list:
    h = cfg.hipocicloide
    escala_v, escala_a = desenho.escalas_cinematica(cfg, cinematicas)
    return [
        Paragraph("Parte 1: hipociclóide", ESTILOS["secao"]),
        _texto(
            f"Um disco de raio $r = {_numero(h.raio_disco)}$ rola sem escorregar dentro de um aro "
            f"de raio $R = {_numero(h.raio_aro)}$. O ponto $P$ da periferia do disco descreve a "
            "hipociclóide"
        ),
        documento.formula(
            r"x = (R - r)\cos\theta + r\cos\left(\dfrac{R - r}{r}\,\theta\right)"
            r"\qquad y = (R - r)\sin\theta - r\sin\left(\dfrac{R - r}{r}\,\theta\right)"
        ),
        _texto(
            "A Figura 2 mostra a animação do item 1.2. O mesmo processo está no vídeo "
            f"{Path(cfg.saida_animacao).name}, entregue junto com este PDF e também anexado a ele. "
            "Como na seção 16 do capítulo 3 das notas de aula, o raio de curvatura e os versores "
            r"saem das derivadas $\vec{r}\,' = d\vec{P}/d\theta$ e "
            r"$\vec{r}\,'' = d^2\vec{P}/d\theta^2$, com componente $z = 0$:"
        ),
        documento.formula(
            r"\rho = \dfrac{|\vec{r}\,'|^3}{|\vec{r}\,' \wedge \vec{r}\,''|}"
            r"\qquad \vec{\tau} = \dfrac{\vec{r}\,'}{|\vec{r}\,'|}"
            r"\qquad \vec{b} = "
            r"\dfrac{\vec{r}\,' \wedge \vec{r}\,''}{|\vec{r}\,' \wedge \vec{r}\,''|}"
            r"\qquad \vec{n} = \vec{b} \wedge \vec{\tau}"
        ),
        _texto(
            r"No plano, $\vec{b} = \pm\vec{k}$. Nas cúspides $\vec{r}\,' = \vec{0}$, e "
            r"$\vec{\tau}$ e $\vec{n}$ não são definidos."
        ),
        Paragraph("Item 1.5: raio de curvatura", ESTILOS["secao"]),
        _tabela(
            ["Ponto", r"$\theta$", "$P$", r"$\rho$", "Centro de curvatura"],
            [
                [str(i), _graus(c.theta), _vetor(c.ponto), _numero(c.raio), _vetor(c.centro)]
                for i, c in enumerate(curvaturas, start=1)
            ],
            [1.5, 2.0, 4.8, 2.0, 5.7],
        ),
        Paragraph("Item 1.6: versores tangente e normal principal", ESTILOS["secao"]),
        _tabela(
            [r"$\theta$", "$P$", r"$\vec{\tau}$", r"$\vec{n}$"],
            [
                [_graus(c.theta), _vetor(c.ponto), _vetor(c.tangente), _vetor(c.normal)]
                for c in versores
            ],
            [2.0, 4.4, 4.8, 4.8],
        ),
        PageBreak(),
        Paragraph("Item 1.7: velocidade e aceleração", ESTILOS["secao"]),
        _texto(
            r"Com a lei horária $\theta(t) = \omega t$ e $\omega$ constante, a regra da cadeia dá"
        ),
        documento.formula(
            r"\vec{v} = \omega\,\dfrac{d\vec{P}}{d\theta}"
            r"\qquad \vec{a} = \omega^2\,\dfrac{d^2\vec{P}}{d\theta^2}"
            r"\qquad \omega = \dfrac{\pi}{60}\ \mathrm{rad/s}"
        ),
        _texto("e, na forma intrínseca,"),
        documento.formula(
            r"\vec{v} = v\,\vec{\tau}"
            r"\qquad \vec{a} = a_\tau\,\vec{\tau} + a_n\,\vec{n}"
            r"\qquad a_\tau = \dfrac{dv}{dt} = \vec{a} \cdot \vec{\tau}"
            r"\qquad a_n = \dfrac{v^2}{\rho} = \vec{a} \cdot \vec{n}"
        ),
        _texto(
            "Comprimentos na mesma unidade de $R$ e $r$, tempos em segundos. "
            rf"Na Figura 7, $\vec{{v}}$ aparece multiplicada por {_numero(escala_v)} e "
            rf"$\vec{{a}}$ por {_numero(escala_a)}."
        ),
        _texto("Forma cartesiana"),
        _tabela(
            ["$t$ (s)", r"$\theta$", "$P$", r"$\vec{v}$", r"$\vec{a}$"],
            [
                [
                    _numero(k.t),
                    _graus(k.curvatura.theta),
                    _vetor(k.curvatura.ponto),
                    _vetor(k.velocidade),
                    _vetor(k.aceleracao),
                ]
                for k in cinematicas
            ],
            [1.4, 1.6, 3.6, 4.7, 4.7],
        ),
        Spacer(1, 0.3 * cm),
        _texto("Coordenadas intrínsecas"),
        _tabela(
            ["$t$ (s)", "$v$", r"$a_\tau$", "$a_n$", r"$\rho$", r"$\vec{\tau}$", r"$\vec{n}$"],
            [
                [
                    _numero(k.t),
                    _numero(np.linalg.norm(k.velocidade)),
                    _numero(k.a_tangencial),
                    _numero(k.a_normal),
                    _numero(k.curvatura.raio),
                    _vetor(k.curvatura.tangente),
                    _vetor(k.curvatura.normal),
                ]
                for k in cinematicas
            ],
            [1.4, 1.6, 1.6, 1.6, 1.6, 4.1, 4.1],
        ),
        PageBreak(),
    ]


# Página da Figura 2 com o lugar reservado para a animação, que é colocada depois que o PDF
# fica pronto, e a nota ao professor sobre o vídeo entregue junto.
def _pagina_da_animacao(reserva: documento.Reserva, video: str) -> list:
    return [
        Spacer(1, 1.6 * cm),
        Paragraph("Figura 2: Item 1.2: animação da geração", ESTILOS["secao"]),
        reserva,
        Spacer(1, 0.2 * cm),
        Paragraph(
            "A animação roda sozinha em leitores de PDF que executam JavaScript, como o Google "
            "Chrome, o Microsoft Edge e o Adobe Acrobat Reader. Nos demais aparece só o primeiro "
            "quadro.",
            ESTILOS["legenda"],
        ),
        Spacer(1, 0.6 * cm),
        Paragraph(
            "<b>Nota ao professor</b>: se a animação não rodar no seu leitor de PDF, o mesmo "
            f"processo pode ser visto no vídeo {Path(video).name}, entregue junto com este PDF. "
            "O vídeo também vai anexado ao próprio PDF.",
            ESTILOS["texto"],
        ),
        PageBreak(),
    ]


# Texto e tabelas da parte 2: o raio de curvatura (2.2) e o triedro de Frenet (2.3) nos
# três pontos escolhidos da curva C.
def _parte_2(triedros: list[Triedro]) -> list:
    return [
        Paragraph(documento.com_formulas(r"Parte 2: curva $\mathcal{C}$", 13), ESTILOS["secao"]),
        _texto(r"A curva $\mathcal{C}$ e as suas derivadas são"),
        documento.formula(
            r"\vec{r}(\lambda) = (\lambda,\ \lambda^2,\ \lambda^3)"
            r"\qquad \vec{r}\,' = (1,\ 2\lambda,\ 3\lambda^2)"
            r"\qquad \vec{r}\,'' = (0,\ 2,\ 6\lambda)"
        ),
        _texto(
            r"e $\rho$, $\vec{\tau}$, $\vec{n}$ e $\vec{b}$ saem do mesmo procedimento da parte 1."
        ),
        Paragraph("Item 2.2: raio de curvatura", ESTILOS["secao"]),
        _tabela(
            [r"$\lambda$", "$P$", r"$\rho$"],
            [[_numero(t.parametro), _vetor(t.ponto), _numero(t.raio)] for t in triedros],
            [2.0, 9.0, 5.0],
        ),
        Paragraph("Item 2.3: triedro de Frenet", ESTILOS["secao"]),
        _tabela(
            [r"$\lambda$", r"$\vec{\tau}$", r"$\vec{n}$", r"$\vec{b}$"],
            [
                [_numero(t.parametro), _vetor(t.tangente), _vetor(t.normal), _vetor(t.binormal)]
                for t in triedros
            ],
            [1.6, 4.8, 4.8, 4.8],
        ),
        PageBreak(),
    ]


# Monta o PDF completo: capa, parte 1 com as figuras 1 a 7, parte 2 com a figura 8 e o
# código-fonte. Depois põe a animação no lugar reservado e anexa o vídeo.
def gerar_pdf(
    cfg: Config,
    curvaturas: list[Curvatura],
    versores: list[Curvatura],
    cinematicas: list[Cinematica],
    triedros: list[Triedro],
    arquivos: list[Path],
    caminho: str | Path,
) -> Path:
    explicacao = documento.com_formulas(
        "Na primeira parte, o programa traça a hipociclóide gerada por um disco que rola dentro "
        "de um aro, anima o processo, mostra instantâneos e exemplos para quatro razões $R/r$, e "
        "calcula o raio de curvatura, os versores tangente e normal principal e a velocidade e a "
        "aceleração de $P$ nas formas cartesiana e intrínseca. Na segunda parte, calcula o raio "
        r"de curvatura e o triedro de Frenet da curva $(\lambda,\ \lambda^2,\ \lambda^3)$ em três "
        "pontos."
    )
    conteudo = documento.capa(
        "Hipociclóide e triedro de Frenet",
        TAREFA,
        _parametros(cfg),
        explicacao,
        ESTILOS,
        mencionar_projeto=False,
    )
    conteudo += _parte_1(cfg, curvaturas, versores, cinematicas)
    conteudo += _pagina_de_figura(
        cfg,
        desenho.figura_curva(cfg),
        "Figura 1: Item 1.1: hipociclóide",
        "O aro, a curva e as cúspides.",
    )
    reserva = documento.Reserva(12 * cm, 12 * cm)
    conteudo += _pagina_da_animacao(reserva, cfg.saida_animacao)
    figuras = [
        (
            desenho.figura_instantaneos(cfg),
            "Item 1.3: instantâneos da geração",
            r"O disco, o raio $CP$, o ponto de contato com o aro e o traço de $P$ "
            r"até cada $\theta$.",
        ),
        (
            desenho.figura_razoes(cfg),
            "Item 1.4: quatro razões $R/r$",
            "Com $R/r = p/q$ irredutível, a curva tem $p$ cúspides e fecha após $q$ voltas.",
        ),
        (
            desenho.figura_curvatura(cfg, curvaturas),
            "Item 1.5: raio de curvatura",
            "Círculos osculadores nos pontos da tabela, numerados na mesma ordem.",
        ),
        (
            desenho.figura_versores(cfg, versores),
            "Item 1.6: versores tangente e normal principal",
            "A normal principal aponta sempre para o centro de curvatura.",
        ),
        (
            desenho.figura_cinematica(cfg, cinematicas),
            "Item 1.7: velocidade e aceleração",
            "Vetores velocidade e aceleração de $P$ nos três instantes, nas escalas do texto.",
        ),
    ]
    for numero, (figura, titulo, legenda) in enumerate(figuras, start=3):
        conteudo += _pagina_de_figura(cfg, figura, f"Figura {numero}: {titulo}", legenda)
    conteudo += _parte_2(triedros)
    conteudo += _pagina_de_figura(
        cfg,
        desenho.figura_cubica(cfg, triedros),
        r"Figura 8: itens 2.1 e 2.3, curva $\mathcal{C}$",
        cfg.vista.descricao,
    )
    documento.gerar_pdf(TAREFA, conteudo, arquivos, caminho, mencionar_projeto=False)
    documento.animar(
        caminho, desenho.quadros_jpeg(cfg), reserva, cfg.hipocicloide.quadros_por_segundo_pdf
    )
    documento.anexar(caminho, cfg.saida_animacao)
    return Path(caminho)
