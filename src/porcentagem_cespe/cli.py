#!/usr/bin/env python3
"""
Interface de linha de comando para o Porcentagem CESPE.

Uso:
    python -m porcentagem_cespe validar [arquivo.csv]
    python -m porcentagem_cespe analisar [arquivo.csv]
"""

import argparse
import sys
from pathlib import Path

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    # Fallback simples se colorama não estiver instalado
    class Fore:
        GREEN = "\033[92m"
        RED = "\033[91m"
        YELLOW = "\033[93m"
        BLUE = "\033[94m"
        RESET = "\033[0m"

    class Style:
        BRIGHT = "\033[1m"
        RESET_ALL = "\033[0m"

from porcentagem_cespe.analisador import AnalisadorDados
from porcentagem_cespe.validador import ValidadorHierarquia


def obter_diretorio_csv() -> Path:
    """Retorna o diretório padrão dos arquivos CSV."""
    # Tenta encontrar o diretório data/csv relativo ao projeto
    # Estrutura esperada:
    #   root/
    #     data/csv/
    #     src/porcentagem_cespe/cli.py

    # src/porcentagem_cespe/cli.py -> src/porcentagem_cespe -> src -> root
    root_dir = Path(__file__).resolve().parent.parent.parent
    data_csv = root_dir / "datasets" / "por_disciplina"

    if data_csv.exists():
        return data_csv

    # Fallback para diretório atual
    return Path.cwd() / "datasets" / "por_disciplina"


def validar_hierarquia(args: argparse.Namespace) -> int:
    """Comando CLI para validar hierarquia dos dados."""
    csv_dir = obter_diretorio_csv()

    if args.arquivo:
        # Verifica se é caminho absoluto ou relativo ao diretório atual
        caminho = Path(args.arquivo)
        if not caminho.exists():
            # Tenta relativo ao diretório de dados
            caminho = csv_dir / args.arquivo

        arquivos = [caminho]
    else:
        arquivos = sorted(csv_dir.glob("*.csv"))

    if not arquivos:
        print(f"{Fore.RED}❌ Nenhum arquivo CSV encontrado{Style.RESET_ALL}")
        return 1

    print(f"\n{Style.BRIGHT}🔍 VALIDADOR DE HIERARQUIA DE DADOS{Style.RESET_ALL}")
    print("=" * 50)

    validador = ValidadorHierarquia(verbose=args.verbose)

    total_arquivos = 0
    arquivos_ok = 0
    todas_inconsistencias = []

    for arquivo in arquivos:
        if not arquivo.exists():
            print(f"{Fore.RED}❌ Não encontrado: {arquivo}{Style.RESET_ALL}")
            continue

        total_arquivos += 1
        resultado = validador.validar_arquivo(arquivo)

        print(f"\n📄 {Fore.BLUE}{arquivo.name}{Style.RESET_ALL}")

        if resultado.valido:
            print(f"   {Fore.GREEN}✅ OK - Dados íntegros{Style.RESET_ALL}")
            arquivos_ok += 1
        else:
            print(f"   {Fore.RED}❌ {len(resultado.inconsistencias)} erro(s){Style.RESET_ALL}")
            todas_inconsistencias.extend(resultado.inconsistencias)

            if args.verbose:
                for inc in resultado.inconsistencias[:5]:  # Mostra até 5
                    print(f"      • {inc.pai.hierarquia or 'RAIZ'}: "
                          f"esperado {inc.soma_filhos}, encontrado {inc.pai.quantidade}")

                ocultas = len(resultado.inconsistencias) - 5
                if ocultas > 0:
                    print(f"      ... e mais {ocultas} inconsistência(s)")

    # Resumo final
    print("\n" + "=" * 50)
    print(f"{Style.BRIGHT}📊 RESUMO{Style.RESET_ALL}")
    print(f"   Arquivos: {total_arquivos}")
    print(f"   {Fore.GREEN}✅ Íntegros: {arquivos_ok}{Style.RESET_ALL}")
    print(f"   {Fore.RED}❌ Com erros: {total_arquivos - arquivos_ok}{Style.RESET_ALL}")

    if todas_inconsistencias:
        print(f"   Total de inconsistências: {len(todas_inconsistencias)}")

    print("=" * 50)

    return 0 if not todas_inconsistencias else 1


def analisar_dados(args: argparse.Namespace) -> int:
    """Comando CLI para analisar dados."""
    csv_dir = obter_diretorio_csv()

    if not args.arquivo:
        print(f"{Fore.RED}❌ Especifique um arquivo CSV{Style.RESET_ALL}")
        print("   Uso: analisar <arquivo.csv>")
        print("\n   Arquivos disponíveis:")
        if csv_dir.exists():
            for arq in csv_dir.glob("*.csv"):
                print(f"      • {arq.name}")
        return 1

    # Verifica se é caminho absoluto ou relativo ao diretório atual
    arquivo = Path(args.arquivo)
    if not arquivo.exists():
        # Tenta relativo ao diretório de dados
        arquivo = csv_dir / args.arquivo

    if not arquivo.exists():
        print(f"{Fore.RED}❌ Arquivo não encontrado: {arquivo}{Style.RESET_ALL}")
        return 1

    analisador = AnalisadorDados()

    if not analisador.carregar(arquivo):
        print(f"{Fore.RED}❌ Erro ao carregar arquivo{Style.RESET_ALL}")
        return 1

    print(analisador.resumo())

    return 0


def main() -> int:
    """Ponto de entrada principal do CLI."""
    parser = argparse.ArgumentParser(
        description="Porcentagem CESPE - Análise de Questões"
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Comando validar
    parser_validar = subparsers.add_parser(
        "validar", help="Valida integridade dos dados"
    )
    parser_validar.add_argument(
        "arquivo", nargs="?", help="Arquivo CSV específico (opcional)"
    )
    parser_validar.add_argument(
        "-v", "--verbose", action="store_true", help="Modo detalhado"
    )

    # Comando analisar
    parser_analisar = subparsers.add_parser(
        "analisar", help="Analisa estatísticas"
    )
    parser_analisar.add_argument(
        "arquivo", nargs="?", help="Arquivo CSV para analisar"
    )

    args = parser.parse_args()

    if args.comando == "validar":
        return validar_hierarquia(args)
    elif args.comando == "analisar":
        return analisar_dados(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
