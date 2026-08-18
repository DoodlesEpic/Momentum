# Momentum - programas das tarefas optativas de PME0100 Mecânica I
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior. Veja o arquivo LICENSE.

"""Linha de comando dos programas das tarefas optativas."""

import argparse
from pathlib import Path

from . import __version__

RAIZ = Path(__file__).resolve().parent.parent
CONFIGS_PADRAO = {
    "tarefa1": RAIZ / "config_tarefa_1.toml",
    "tarefa2": RAIZ / "config_tarefa_2.toml",
}


def _argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        prog="momentum",
        description="Gera os relatórios das tarefas optativas de Mecânica I.",
    )
    analisador.add_argument("--version", action="version", version=f"Momentum {__version__}")
    subcomandos = analisador.add_subparsers(dest="tarefa")
    for nome, titulo in (("tarefa1", "Tarefa 1"), ("tarefa2", "Tarefa 2")):
        comando = subcomandos.add_parser(nome, help=f"gera o PDF da {titulo}")
        comando.add_argument(
            "-c",
            "--config",
            default=None,
            help=f"arquivo TOML de configuração (padrão: {CONFIGS_PADRAO[nome].name})",
        )
        comando.add_argument("-s", "--saida", default=None, help="caminho do PDF gerado")
    return analisador.parse_args()


def _caminho_config(tarefa: str, argumento: str | None) -> Path | None:
    """Resolve a configuração explícita ou usa os valores embutidos se faltar o padrão."""
    if argumento is not None:
        return Path(argumento)
    caminho = CONFIGS_PADRAO[tarefa]
    return caminho if caminho.exists() else None


def _arquivos_do_codigo(tarefa: str, caminho_config: Path | None) -> list[Path]:
    """Fontes que entram na listagem do PDF da tarefa escolhida."""
    pacote = Path(__file__).parent
    arquivos = [pacote / "__init__.py", pacote / "__main__.py"]
    arquivos += sorted((pacote / "comum").glob("*.py"))
    arquivos += sorted((pacote / tarefa.replace("tarefa", "tarefa_")).glob("*.py"))
    if caminho_config is not None and caminho_config.exists():
        arquivos.append(caminho_config)
    return arquivos


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


if __name__ == "__main__":
    main()
