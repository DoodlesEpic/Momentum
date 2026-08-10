# Momentum - visualização do campo de momentos de uma força
# Copyright (C) 2026 Eduardo Lima Moraes
# Licenciado sob a GNU GPL v3 ou posterior; veja o arquivo LICENSE.

"""Linha de comando: lê a configuração, desenha as vistas e grava o PDF."""

import argparse
from pathlib import Path

from . import __version__, campo, config, desenho, relatorio

RAIZ = Path(__file__).resolve().parent.parent
CONFIG_PADRAO = RAIZ / "config.toml"


def _argumentos() -> argparse.Namespace:
    analisador = argparse.ArgumentParser(
        prog="momentum",
        description="Desenha o campo de momentos de uma força e gera um relatório em PDF.",
    )
    analisador.add_argument(
        "-c",
        "--config",
        default=None,
        help=f"arquivo TOML de configuração (padrão: {CONFIG_PADRAO.name})",
    )
    analisador.add_argument("-s", "--saida", default=None, help="caminho do PDF gerado")
    analisador.add_argument("--version", action="version", version=f"Momentum {__version__}")
    return analisador.parse_args()


def _arquivos_do_codigo(caminho_config: Path | None) -> list[Path]:
    """Fontes que entram na listagem do PDF: os módulos e a configuração usada."""
    arquivos = sorted(Path(__file__).parent.glob("*.py"))
    if caminho_config is not None and caminho_config.exists():
        arquivos.append(caminho_config)
    return arquivos


def main() -> None:
    argumentos = _argumentos()
    caminho_config = Path(argumentos.config) if argumentos.config else CONFIG_PADRAO
    if argumentos.config is None and not caminho_config.exists():
        caminho_config = None  # sem arquivo: usa os valores padrão do programa

    cfg = config.carregar(caminho_config)
    amostras = campo.gerar_amostras(cfg)
    figuras = desenho.gerar_figuras(cfg, amostras)
    saida = Path(argumentos.saida or cfg.saida_pdf)
    relatorio.gerar_pdf(cfg, figuras, _arquivos_do_codigo(caminho_config), saida)

    print(f"{len(amostras)} pontos O amostrados em {cfg.planos} planos.")
    print(f"PDF gerado em {saida.resolve()}")


if __name__ == "__main__":
    main()
