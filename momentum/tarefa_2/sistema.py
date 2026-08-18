# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Redução e caracterização de sistemas de forças no espaço."""

from dataclasses import dataclass

import numpy as np

from ..comum import vetores
from .config import Caso


@dataclass
class EixoCentral:
    """Ponto e direção da reta central de um sistema de forças."""

    ponto: np.ndarray
    direcao: np.ndarray


@dataclass
class Disposicao:
    """Propriedades geométricas detectadas nas linhas de ação."""

    nomes: tuple[str, ...]
    ponto_de_concorrencia: np.ndarray | None = None

    @property
    def descricao(self) -> str:
        """Texto que pode ser incluído diretamente no relatório."""
        return ", ".join(self.nomes)


@dataclass
class Reducao:
    """Todas as grandezas resultantes da redução de um caso."""

    caso: Caso
    resultante: np.ndarray
    momento_q: np.ndarray
    momento_a: np.ndarray
    torque: float
    invariante: float
    tipo: str
    disposicao: Disposicao
    eixo_central: EixoCentral | None
    momento_minimo: np.ndarray | None


@dataclass(frozen=True)
class _Escalas:
    """Escalas naturais usadas nas comparações por tolerância."""

    forca: float
    comprimento: float
    momento: float
    invariante: float


def _matriz_antissimetrica(vetor: np.ndarray) -> np.ndarray:
    """Matriz que representa o produto vetorial vetor x x."""
    x, y, z = vetor
    return np.array([[0.0, -z, y], [z, 0.0, -x], [-y, x, 0.0]])


def _escalas(caso: Caso) -> _Escalas:
    """Obtém escalas das forças e distâncias do próprio caso."""
    modulos = np.linalg.norm(caso.forcas, axis=1)
    escala_forca = max(float(modulos.sum()), np.finfo(float).eps)
    referencias = np.vstack([caso.pontos, caso.polo_q, caso.polo_a])
    distancias = np.linalg.norm(referencias - referencias[0], axis=1)
    escala_comprimento = max(float(distancias.max()), np.finfo(float).eps)
    escala_momento = escala_forca * escala_comprimento
    return _Escalas(
        forca=escala_forca,
        comprimento=escala_comprimento,
        momento=escala_momento,
        invariante=escala_forca * escala_momento,
    )


def _nulo(valor: np.ndarray | float, escala: float, tolerancia: float) -> bool:
    """Informa se um escalar ou vetor é nulo na escala indicada."""
    return np.linalg.norm(valor) <= tolerancia * escala


def _momento_no_polo(caso: Caso, polo: np.ndarray) -> np.ndarray:
    """Soma os momentos das forças de um caso em relação a um polo."""
    return np.cross(caso.pontos - polo, caso.forcas).sum(axis=0)


def _ponto_de_concorrencia(
    forcas: np.ndarray, pontos: np.ndarray, escalas: _Escalas, tolerancia: float
) -> np.ndarray | None:
    """Encontra um ponto comum às linhas de ação, se ele existir."""
    referencia = pontos[0]
    direcoes = np.array([vetores.versor(forca) for forca in forcas])
    matriz = np.vstack([_matriz_antissimetrica(direcao) for direcao in direcoes])
    termos = np.concatenate(
        [np.cross(direcao, ponto - referencia) for direcao, ponto in zip(direcoes, pontos)]
    )
    deslocamento, _, _, _ = np.linalg.lstsq(matriz, termos, rcond=None)
    residuos = np.linalg.norm(
        np.cross(direcoes, deslocamento - (pontos - referencia)), axis=1
    )
    if np.all(residuos <= tolerancia * escalas.comprimento):
        return referencia + deslocamento
    return None


def _normal_do_plano(
    forcas: np.ndarray, pontos: np.ndarray, escalas: _Escalas, tolerancia: float
) -> np.ndarray | None:
    """Encontra a normal de um plano que contém todas as linhas de ação."""
    referencia = pontos[0]
    direcoes = np.array([vetores.versor(forca) for forca in forcas])
    distancias = (pontos - referencia) / escalas.comprimento
    matriz = np.vstack(
        [np.column_stack([direcoes, np.zeros(len(direcoes))]), np.column_stack([distancias, -np.ones(len(pontos))])]
    )
    candidato = np.linalg.svd(matriz)[2][-1]
    normal = candidato[:3]
    norma = np.linalg.norm(normal)
    if norma == 0.0:
        return None
    normal /= norma
    desvios_das_forcas = np.abs(direcoes @ normal)
    desvios_dos_pontos = np.abs((pontos - referencia) @ normal)
    if np.all(desvios_das_forcas <= tolerancia) and np.all(
        desvios_dos_pontos <= tolerancia * escalas.comprimento
    ):
        return normal
    return None


def _disposicao(caso: Caso, escalas: _Escalas, tolerancia: float) -> Disposicao:
    """Detecta paralelismo, concorrência e coplanaridade das forças não nulas."""
    modulos = np.linalg.norm(caso.forcas, axis=1)
    forcas = caso.forcas[modulos > tolerancia * escalas.forca]
    pontos = caso.pontos[modulos > tolerancia * escalas.forca]
    if len(forcas) == 0:
        return Disposicao(("sem forças não nulas",))
    if len(forcas) == 1:
        return Disposicao(("uma única força",))

    direcoes = np.array([vetores.versor(forca) for forca in forcas])
    paralelas = all(
        np.linalg.norm(np.cross(direcoes[0], direcao)) <= tolerancia
        for direcao in direcoes[1:]
    )
    ponto = _ponto_de_concorrencia(forcas, pontos, escalas, tolerancia)
    normal = _normal_do_plano(forcas, pontos, escalas, tolerancia)
    nomes = []
    if ponto is not None:
        nomes.append("forças concorrentes")
    if normal is not None:
        nomes.append("forças coplanares")
    if paralelas:
        nomes.append("forças paralelas")
    return Disposicao(tuple(nomes or ["sem disposição geométrica especial"]), ponto)


def _tipo(resultante: np.ndarray, momento_q: np.ndarray, invariante: float, escalas: _Escalas, tolerancia: float) -> str:
    """Classifica o sistema em uma das quatro categorias do enunciado."""
    if _nulo(resultante, escalas.forca, tolerancia):
        return "nulo" if _nulo(momento_q, escalas.momento, tolerancia) else "redutível a um binário"
    if _nulo(invariante, escalas.invariante, tolerancia):
        return "redutível a uma única força"
    return "redutível a força mais binário"


def _validar(reducao: Reducao, escalas: _Escalas, tolerancia: float) -> None:
    """Confere as identidades mecânicas que devem valer para toda redução."""
    caso = reducao.caso
    transporte = reducao.momento_q + np.cross(caso.polo_q - caso.polo_a, reducao.resultante)
    if not _nulo(reducao.momento_a - transporte, escalas.momento, tolerancia):
        raise ValueError("o transporte do momento entre os polos não confere")
    invariante_a = float(np.dot(reducao.resultante, reducao.momento_a))
    if not _nulo(invariante_a - reducao.invariante, escalas.invariante, tolerancia):
        raise ValueError("o invariante escalar dependeu do polo")
    if reducao.eixo_central is None:
        return

    eixo = reducao.eixo_central
    momento_e = reducao.momento_q + np.cross(caso.polo_q - eixo.ponto, reducao.resultante)
    if not _nulo(np.cross(momento_e, reducao.resultante), escalas.invariante, tolerancia):
        raise ValueError("o momento no eixo central não é paralelo à resultante")
    if not _nulo(momento_e - reducao.momento_minimo, escalas.momento, tolerancia):
        raise ValueError("o momento mínimo não confere com o eixo central")
    if np.linalg.norm(reducao.momento_minimo) > np.linalg.norm(reducao.momento_q) + tolerancia * escalas.momento:
        raise ValueError("o momento mínimo é maior que o momento no polo Q")


def reduzir(caso: Caso, tolerancia: float = 1e-9) -> Reducao:
    """Reduz um sistema de forças e confere as identidades mecânicas obtidas."""
    if tolerancia <= 0.0:
        raise ValueError("a tolerância deve ser positiva")
    escalas = _escalas(caso)
    resultante = caso.forcas.sum(axis=0)
    momento_q = _momento_no_polo(caso, caso.polo_q)
    momento_a = _momento_no_polo(caso, caso.polo_a)
    torque = float(np.dot(momento_a, caso.versor_u))
    invariante = float(np.dot(resultante, momento_q))
    tipo = _tipo(resultante, momento_q, invariante, escalas, tolerancia)
    eixo_central = None
    momento_minimo = None
    if not _nulo(resultante, escalas.forca, tolerancia):
        modulo_ao_quadrado = float(np.dot(resultante, resultante))
        ponto = caso.polo_q + np.cross(resultante, momento_q) / modulo_ao_quadrado
        eixo_central = EixoCentral(ponto, vetores.versor(resultante))
        momento_minimo = invariante * resultante / modulo_ao_quadrado
    reducao = Reducao(
        caso=caso,
        resultante=resultante,
        momento_q=momento_q,
        momento_a=momento_a,
        torque=torque,
        invariante=invariante,
        tipo=tipo,
        disposicao=_disposicao(caso, escalas, tolerancia),
        eixo_central=eixo_central,
        momento_minimo=momento_minimo,
    )
    _validar(reducao, escalas, tolerancia)
    return reducao
