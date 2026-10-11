# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Linha de comando dos programas das tarefas optativas."""

import argparse
from pathlib import Path

from . import __version__

RAIZ = Path(__file__).resolve().parent.parent
CONFIGS_PADRAO = {
    "tarefa1": RAIZ / "config" / "tarefa_1.toml",
    "tarefa2": RAIZ / "config" / "tarefa_2.toml",
    "tarefa5": RAIZ / "config" / "tarefa_5.toml",
}
MODULOS_DE_CALCULO = {
    "tarefa1": ["campo.py"],
    "tarefa2": ["sistema.py"],
    "tarefa5": ["hipocicloide.py", "cubica.py"],
}


# Lê a linha de comando. Cada tarefa é um subcomando com as opções --config e --saida.
def _argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        prog="momentum",
        description="Gera os relatórios das tarefas optativas de Mecânica I.",
    )
    analisador.add_argument("--version", action="version", version=f"Momentum {__version__}")
    subcomandos = analisador.add_subparsers(dest="tarefa")
    for nome, caminho in CONFIGS_PADRAO.items():
        titulo = nome.replace("tarefa", "Tarefa ")
        comando = subcomandos.add_parser(nome, help=f"gera o PDF da {titulo}")
        comando.add_argument(
            "-c",
            "--config",
            default=None,
            help=f"arquivo TOML de configuração (padrão: {caminho.name})",
        )
        comando.add_argument("-s", "--saida", default=None, help="caminho do PDF gerado")
    return analisador.parse_args()


# Escolhe o TOML da tarefa: o indicado na linha de comando ou o padrão da pasta config.
# Sem nenhum dos dois, a tarefa usa os valores embutidos no seu config.py.
def _caminho_config(tarefa: str, argumento: str | None) -> Path | None:
    if argumento is not None:
        return Path(argumento)
    caminho = CONFIGS_PADRAO[tarefa]
    return caminho if caminho.exists() else None


# Arquivos de cálculo e de configuração cuja listagem vai para o final do PDF.
def _arquivos_do_codigo(tarefa: str, caminho_config: Path | None) -> list[Path]:
    pacote = Path(__file__).parent
    subpacote = tarefa.replace("tarefa", "tarefa_")
    arquivos = [pacote / "comum" / "vetores.py"]
    arquivos += [pacote / subpacote / modulo for modulo in MODULOS_DE_CALCULO[tarefa]]
    if caminho_config is not None and caminho_config.exists():
        arquivos.append(caminho_config)
    return arquivos


# Tarefa 1: amostra o campo de momentos, desenha as vistas e grava o PDF.
def _gerar_tarefa_1(configuracao: str | None, caminho_da_saida: str | None) -> None:
    from .tarefa_1 import campo, config, desenho, relatorio

    caminho_config = _caminho_config("tarefa1", configuracao)
    cfg = config.carregar(caminho_config)
    amostras = campo.gerar_amostras(cfg)
    figuras = desenho.gerar_figuras(cfg, amostras)
    saida = Path(caminho_da_saida or cfg.saida_pdf)
    relatorio.gerar_pdf(cfg, figuras, _arquivos_do_codigo("tarefa1", caminho_config), saida)
    print(f"Tarefa 1: {len(amostras)} pontos O amostrados em {cfg.planos} planos.")
    print(f"PDF gerado em {saida.resolve()}")


# Tarefa 2: reduz cada sistema de forças, desenha as figuras e grava o PDF.
def _gerar_tarefa_2(configuracao: str | None, caminho_da_saida: str | None) -> None:
    from .tarefa_2 import config, desenho, relatorio, sistema

    caminho_config = _caminho_config("tarefa2", configuracao)
    cfg = config.carregar(caminho_config)
    reducoes = [sistema.reduzir(caso, cfg.tolerancia) for caso in cfg.casos]
    figuras = desenho.gerar_figuras(cfg, reducoes)
    saida = Path(caminho_da_saida or cfg.saida_pdf)
    relatorio.gerar_pdf(
        cfg, reducoes, figuras, _arquivos_do_codigo("tarefa2", caminho_config), saida
    )
    print(f"Tarefa 2: {len(reducoes)} sistemas de forças analisados.")
    print(f"PDF gerado em {saida.resolve()}")


# Tarefa 5: calcula curvatura, versores e cinemática da hipociclóide e o triedro da
# curva C, grava o vídeo e depois o PDF, que leva o vídeo anexado.
def _gerar_tarefa_5(configuracao: str | None, caminho_da_saida: str | None) -> None:
    from .tarefa_5 import config, cubica, desenho, hipocicloide, relatorio

    caminho_config = _caminho_config("tarefa5", configuracao)
    cfg = config.carregar(caminho_config)
    h = cfg.hipocicloide
    R, r = h.raio_aro, h.raio_disco
    curvaturas = [hipocicloide.curvatura(R, r, theta) for theta in h.posicoes_curvatura]
    versores = [hipocicloide.curvatura(R, r, theta) for theta in h.posicoes_versores]
    cinematicas = [hipocicloide.cinematica(R, r, h.omega, t) for t in h.instantes]
    triedros = [cubica.triedro(parametro) for parametro in cfg.cubica.parametros]
    animacao = desenho.gravar_animacao(cfg)
    saida = Path(caminho_da_saida or cfg.saida_pdf)
    arquivos = _arquivos_do_codigo("tarefa5", caminho_config)
    relatorio.gerar_pdf(cfg, curvaturas, versores, cinematicas, triedros, arquivos, saida)
    print(f"Tarefa 5: hipociclóide com R/r = {R / r:g} e {len(triedros)} triedros de Frenet.")
    print(f"Animação gravada em {animacao.resolve()}")
    print(f"PDF gerado em {saida.resolve()}")


# Ponto de entrada. Sem subcomando, gera os relatórios de todas as tarefas.
def main() -> None:
    argumentos = _argumentos()
    if argumentos.tarefa in (None, "tarefa1"):
        _gerar_tarefa_1(
            getattr(argumentos, "config", None), getattr(argumentos, "saida", None)
        )
    if argumentos.tarefa in (None, "tarefa2"):
        _gerar_tarefa_2(
            getattr(argumentos, "config", None), getattr(argumentos, "saida", None)
        )
    if argumentos.tarefa in (None, "tarefa5"):
        _gerar_tarefa_5(
            getattr(argumentos, "config", None), getattr(argumentos, "saida", None)
        )


if __name__ == "__main__":
    main()
