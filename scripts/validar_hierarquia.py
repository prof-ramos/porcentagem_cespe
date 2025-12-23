#!/usr/bin/env python3
"""
Script de Validação de Hierarquia de Dados - Porcentagem CESPE

Este script valida a integridade dos dados hierárquicos nos arquivos CSV,
verificando se a soma dos filhos é igual ao valor do pai em cada nível.

Uso:
    python validar_hierarquia.py                    # Valida todos os CSVs
    python validar_hierarquia.py arquivo.csv        # Valida um arquivo específico
    python validar_hierarquia.py --verbose          # Modo detalhado
    python validar_hierarquia.py --verbose          # Modo detalhado

Autor: Automático
Data: 23/12/2024
"""

import csv
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


# Códigos ANSI para cores no terminal
class Cores:
    VERDE = "\033[92m"
    VERMELHO = "\033[91m"
    AMARELO = "\033[93m"
    AZUL = "\033[94m"
    NEGRITO = "\033[1m"
    RESET = "\033[0m"


@dataclass
class Topico:
    """Representa um tópico na hierarquia."""
    hierarquia: str
    indice: str
    quantidade: int
    porcentagem: float
    linha_csv: int

    @property
    def nivel(self) -> int:
        """Retorna o nível de profundidade do tópico."""
        if not self.hierarquia:
            return 0
        return self.hierarquia.count('.') + 1

    def __str__(self) -> str:
        return f"[{self.hierarquia or 'RAIZ'}] {self.indice[:50]}..."


@dataclass
class Inconsistencia:
    """Representa uma inconsistência encontrada."""
    tipo: str
    pai: Topico
    soma_filhos: int
    diferenca: int
    filhos: list

    def __str__(self) -> str:
        return (
            f"{self.tipo}: {self.pai.hierarquia or 'RAIZ'}\n"
            f"  Valor do pai: {self.pai.quantidade}\n"
            f"  Soma dos filhos: {self.soma_filhos}\n"
            f"  Diferença: {self.diferenca}"
        )


class ValidadorHierarquia:
    """Validador de hierarquia de dados CSV."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.topicos: list[Topico] = []
        self.inconsistencias: list[Inconsistencia] = []
        self.total_geral: Topico | None = None

    def carregar_csv(self, caminho: str) -> bool:
        """Carrega e parseia um arquivo CSV."""
        self.topicos.clear()
        self.inconsistencias.clear()
        self.total_geral = None

        try:
            with open(caminho, encoding='utf-8') as arquivo:
                leitor = csv.DictReader(arquivo)

                for num_linha, linha in enumerate(leitor, start=2):
                    hierarquia = linha.get('Hierarquia', '').strip()
                    indice = linha.get('Índice', '').strip()

                    # Parse quantidade (remove vírgulas se houver)
                    qtd_str = linha.get('Quantidade encontrada', '0')
                    qtd_str = qtd_str.replace(',', '').strip()
                    try:
                        quantidade = int(qtd_str) if qtd_str else 0
                    except ValueError:
                        quantidade = 0
                        if self.verbose:
                            print(
                                f"{Cores.AMARELO}⚠️  Valor inválido para quantidade: "
                                f"'{qtd_str}'. Usando 0.{Cores.RESET}"
                            )

                    # Parse porcentagem
                    pct_str = linha.get('Porcentagem', '0%')
                    pct_str = pct_str.replace('%', '').replace(',', '.').strip()
                    try:
                        porcentagem = float(pct_str) if pct_str else 0.0
                    except ValueError:
                        porcentagem = 0.0
                        if self.verbose:
                            print(
                                f"{Cores.AMARELO}⚠️  Valor inválido para porcentagem: "
                                f"'{pct_str}'. Usando 0.0.{Cores.RESET}"
                            )

                    topico = Topico(
                        hierarquia=hierarquia,
                        indice=indice,
                        quantidade=quantidade,
                        porcentagem=porcentagem,
                        linha_csv=num_linha
                    )

                    self.topicos.append(topico)

                    # Identifica o total geral (hierarquia vazia)
                    if not hierarquia:
                        self.total_geral = topico

            if self.verbose:
                print(f"  📂 Carregados {len(self.topicos)} tópicos")

            return True

        except FileNotFoundError:
            print(f"{Cores.VERMELHO}❌ Arquivo não encontrado: {caminho}{Cores.RESET}")
            return False
        except Exception as e:
            print(f"{Cores.VERMELHO}❌ Erro ao ler arquivo: {e}{Cores.RESET}")
            return False

    def buscar_filhos_diretos(self, pai: Topico) -> list[Topico]:
        """Busca todos os filhos diretos de um tópico."""
        filhos = []
        nivel_esperado = pai.nivel + 1

        for topico in self.topicos:
            # Pula o próprio pai
            if topico.hierarquia == pai.hierarquia:
                continue

            # Verifica se é filho direto
            if topico.nivel == nivel_esperado:
                # Caso especial: pai é a raiz (hierarquia vazia)
                if not pai.hierarquia:
                    filhos.append(topico)
                # Caso normal: verifica prefixo
                elif topico.hierarquia.startswith(pai.hierarquia + '.'):
                    filhos.append(topico)

        return filhos

    def validar(self) -> bool:
        """Executa a validação completa."""
        if not self.topicos:
            print(f"{Cores.AMARELO}⚠️  Nenhum tópico carregado{Cores.RESET}")
            return False

        self.inconsistencias.clear()

        for topico in self.topicos:
            filhos = self.buscar_filhos_diretos(topico)

            # Se não tem filhos, é um nó folha (válido)
            if not filhos:
                continue

            # Calcula a soma dos filhos
            soma_filhos = sum(f.quantidade for f in filhos)

            # Verifica consistência
            if soma_filhos != topico.quantidade:
                diferenca = topico.quantidade - soma_filhos

                self.inconsistencias.append(Inconsistencia(
                    tipo="SOMA_INCORRETA",
                    pai=topico,
                    soma_filhos=soma_filhos,
                    diferenca=diferenca,
                    filhos=filhos
                ))

        return len(self.inconsistencias) == 0

    def validar_porcentagens(self) -> list[Topico]:
        """Valida se as porcentagens estão corretas."""
        erros_pct = []

        if not self.total_geral:
            return erros_pct

        total = self.total_geral.quantidade

        for topico in self.topicos:
            if topico == self.total_geral:
                continue

            pct_esperada = (topico.quantidade / total) * 100 if total > 0 else 0
            diferenca = abs(pct_esperada - topico.porcentagem)

            # Tolerância de 0.01% para arredondamentos
            if diferenca > 0.01:
                erros_pct.append(topico)
                if self.verbose:
                    print(f"  ⚠️  Porcentagem: {topico.hierarquia} - "
                          f"Esperado: {pct_esperada:.2f}%, Encontrado: {topico.porcentagem:.2f}%")

        return erros_pct

    def gerar_relatorio(self, nome_arquivo: str) -> str:
        """Gera um relatório de validação."""
        linhas = []
        linhas.append("=" * 70)
        linhas.append(f"📊 RELATÓRIO DE VALIDAÇÃO: {nome_arquivo}")
        linhas.append("=" * 70)
        linhas.append("")

        # Estatísticas gerais
        linhas.append("📈 ESTATÍSTICAS:")
        linhas.append(f"  • Total de tópicos: {len(self.topicos)}")
        if self.total_geral:
            linhas.append(f"  • Total de questões: {self.total_geral.quantidade:,}")
            linhas.append(f"  • Disciplina: {self.total_geral.indice}")
        linhas.append("")

        # Distribuição por níveis
        niveis = defaultdict(int)
        for t in self.topicos:
            niveis[t.nivel] += 1

        linhas.append("📊 DISTRIBUIÇÃO POR NÍVEL:")
        for nivel in sorted(niveis.keys()):
            linhas.append(f"  • Nível {nivel}: {niveis[nivel]} tópicos")
        linhas.append("")

        # Resultado da validação
        if not self.inconsistencias:
            linhas.append("✅ RESULTADO: DADOS ÍNTEGROS")
            linhas.append("   Todas as somas hierárquicas estão corretas!")
        else:
            linhas.append(
                f"❌ RESULTADO: {len(self.inconsistencias)} INCONSISTÊNCIA(S) ENCONTRADA(S)"
            )
            linhas.append("")

            for i, inc in enumerate(self.inconsistencias, 1):
                linhas.append(f"─── Inconsistência #{i} ───")
                linhas.append(f"  📍 Hierarquia: {inc.pai.hierarquia or 'RAIZ'}")
                linhas.append(f"  📝 Tópico: {inc.pai.indice[:60]}...")
                linhas.append(f"  📊 Valor no CSV: {inc.pai.quantidade:,}")
                linhas.append(f"  📊 Soma dos filhos: {inc.soma_filhos:,}")
                linhas.append(f"  ⚠️  Diferença: {inc.diferenca:+,}")
                linhas.append(f"  📍 Linha no CSV: {inc.pai.linha_csv}")
                linhas.append("")

                if self.verbose:
                    linhas.append("  Filhos diretos:")
                    for filho in inc.filhos:
                        linhas.append(
                            f"    • [{filho.hierarquia}] {filho.quantidade:,} - "
                            f"{filho.indice[:40]}..."
                        )
                    linhas.append("")

        linhas.append("=" * 70)

        return "\n".join(linhas)


def main():
    """Função principal."""
    # Parseia argumentos
    args = sys.argv[1:]
    verbose = "--verbose" in args or "-v" in args

    # Remove flags dos argumentos
    args = [a for a in args if not a.startswith("-")]

    # Define diretório de CSVs
    script_dir = Path(__file__).parent
    csv_dir = script_dir.parent / "data" / "csv"

    if not csv_dir.exists():
        print(f"{Cores.VERMELHO}❌ Diretório não encontrado: {csv_dir}{Cores.RESET}")
        sys.exit(1)

    # Lista arquivos a validar
    if args:
        # Arquivo específico
        arquivos = [csv_dir / args[0]]
    else:
        # Todos os CSVs
        arquivos = sorted(csv_dir.glob("*.csv"))

    print(f"\n{Cores.NEGRITO}🔍 VALIDADOR DE HIERARQUIA DE DADOS{Cores.RESET}")
    print("=" * 50)

    validador = ValidadorHierarquia(verbose=verbose)

    total_arquivos = 0
    arquivos_ok = 0
    arquivos_erro = 0
    todas_inconsistencias = []

    for arquivo in arquivos:
        if not arquivo.exists():
            print(f"{Cores.VERMELHO}❌ Arquivo não encontrado: {arquivo}{Cores.RESET}")
            continue

        total_arquivos += 1
        print(f"\n📄 Validando: {Cores.AZUL}{arquivo.name}{Cores.RESET}")

        if not validador.carregar_csv(str(arquivo)):
            arquivos_erro += 1
            continue

        if validador.validar():
            print(f"   {Cores.VERDE}✅ OK - Dados íntegros{Cores.RESET}")
            arquivos_ok += 1
        else:
            print(
                f"   {Cores.VERMELHO}❌ ERRO - "
                f"{len(validador.inconsistencias)} inconsistência(s){Cores.RESET}"
            )
            arquivos_erro += 1
            todas_inconsistencias.extend(validador.inconsistencias)

            # Mostra detalhes se verbose
            if verbose:
                print(validador.gerar_relatorio(arquivo.name))

        # Valida porcentagens
        erros_pct = validador.validar_porcentagens()
        if erros_pct and verbose:
            print(
                f"   {Cores.AMARELO}⚠️  {len(erros_pct)} "
                f"porcentagem(s) com diferença{Cores.RESET}"
            )

    # Resumo final
    print("\n" + "=" * 50)
    print(f"{Cores.NEGRITO}📊 RESUMO FINAL{Cores.RESET}")
    print(f"   Arquivos analisados: {total_arquivos}")
    print(f"   {Cores.VERDE}✅ Íntegros: {arquivos_ok}{Cores.RESET}")
    print(f"   {Cores.VERMELHO}❌ Com erros: {arquivos_erro}{Cores.RESET}")

    if todas_inconsistencias:
        print(f"\n   Total de inconsistências: {len(todas_inconsistencias)}")

    print("=" * 50)

    # Retorna código de erro se houver inconsistências
    sys.exit(0 if not todas_inconsistencias else 1)


if __name__ == "__main__":
    main()
