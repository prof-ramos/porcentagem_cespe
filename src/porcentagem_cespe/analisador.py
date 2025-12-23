"""
Módulo de análise de dados hierárquicos.

Este módulo fornece a classe AnalisadorDados para realizar
análises estatísticas sobre os dados de questões.
"""

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from porcentagem_cespe.models import Topico
from porcentagem_cespe.validador import ValidadorHierarquia


@dataclass
class EstatisticasNivel:
    """Estatísticas de um nível da hierarquia."""
    nivel: int
    total_topicos: int
    total_questoes: int
    media_questoes: float
    maior_topico: Topico | None
    menor_topico: Topico | None


@dataclass
class RankingTopico:
    """Item do ranking de tópicos."""
    posicao: int
    topico: Topico
    percentual_acumulado: float


class AnalisadorDados:
    """
    Analisador de dados hierárquicos de questões.

    Fornece métodos para análise estatística, rankings,
    e distribuição de questões por tópicos.

    Exemplo de uso:
        >>> analisador = AnalisadorDados()
        >>> analisador.carregar("dados.csv")
        >>> top10 = analisador.ranking_topicos(limite=10)
        >>> for item in top10:
        ...     print(f"{item.posicao}. {item.topico.indice}: {item.topico.quantidade}")
    """

    def __init__(self):
        """Inicializa o analisador."""
        self._validador = ValidadorHierarquia()
        self._topicos: list[Topico] = []
        self._total_geral: Topico | None = None

    @property
    def topicos(self) -> list[Topico]:
        """Retorna uma cópia da lista de tópicos carregados."""
        return self._topicos.copy()

    @property
    def total_questoes(self) -> int:
        """Retorna o total de questões."""
        return self._total_geral.quantidade if self._total_geral else 0

    @property
    def nome_disciplina(self) -> str:
        """Retorna o nome da disciplina."""
        return self._total_geral.indice if self._total_geral else "Desconhecida"

    def carregar(self, caminho: str | Path) -> bool:
        """
        Carrega um arquivo CSV para análise.

        Args:
            caminho: Caminho para o arquivo CSV.

        Returns:
            True se o carregamento foi bem-sucedido.
        """
        if self._validador.carregar_csv(caminho):
            self._topicos = self._validador.topicos
            self._total_geral = self._validador.total_geral
            return True
        return False

    def topicos_por_nivel(self, nivel: int) -> list[Topico]:
        """
        Retorna todos os tópicos de um determinado nível.

        Args:
            nivel: Nível da hierarquia (1, 2, 3, etc.)

        Returns:
            Lista de tópicos do nível especificado.
        """
        return [t for t in self._topicos if t.nivel == nivel]

    def estatisticas_nivel(self, nivel: int) -> EstatisticasNivel:
        """
        Calcula estatísticas de um nível da hierarquia.

        Args:
            nivel: Nível para calcular estatísticas.

        Returns:
            Objeto EstatisticasNivel com as métricas.
        """
        topicos = self.topicos_por_nivel(nivel)

        if not topicos:
            return EstatisticasNivel(
                nivel=nivel,
                total_topicos=0,
                total_questoes=0,
                media_questoes=0.0,
                maior_topico=None,
                menor_topico=None
            )

        total_questoes = sum(t.quantidade for t in topicos)

        return EstatisticasNivel(
            nivel=nivel,
            total_topicos=len(topicos),
            total_questoes=total_questoes,
            media_questoes=total_questoes / len(topicos),
            maior_topico=max(topicos, key=lambda t: t.quantidade),
            menor_topico=min(topicos, key=lambda t: t.quantidade)
        )

    def ranking_topicos(
        self,
        nivel: int | None = None,
        limite: int = 10,
        ordem_crescente: bool = False
    ) -> list[RankingTopico]:
        """
        Gera ranking de tópicos por quantidade de questões.

        Args:
            nivel: Filtrar por nível específico (None = todos)
            limite: Número máximo de itens no ranking
            ordem_crescente: Se True, ordena do menor para o maior

        Returns:
            Lista de RankingTopico ordenada.
        """
        topicos = self._topicos if nivel is None else self.topicos_por_nivel(nivel)

        # Remove a raiz do ranking
        topicos = [t for t in topicos if t.hierarquia]

        # Ordena por quantidade
        ordenados = sorted(
            topicos,
            key=lambda t: t.quantidade,
            reverse=not ordem_crescente
        )[:limite]

        # Calcula percentual acumulado
        ranking: list[RankingTopico] = []
        acumulado = 0.0

        for i, topico in enumerate(ordenados, 1):
            pct = topico.porcentagem
            acumulado += pct

            ranking.append(RankingTopico(
                posicao=i,
                topico=topico,
                percentual_acumulado=acumulado
            ))

        return ranking

    def distribuicao_niveis(self) -> dict[int, int]:
        """
        Calcula a distribuição de tópicos por nível.

        Returns:
            Dicionário com nível -> quantidade de tópicos.
        """
        distribuicao: dict[int, int] = defaultdict(int)

        for topico in self._topicos:
            distribuicao[topico.nivel] += 1

        return dict(sorted(distribuicao.items()))

    def buscar_topicos(self, termo: str) -> list[Topico]:
        """
        Busca tópicos pelo nome/índice.

        Args:
            termo: Termo de busca (case-insensitive).

        Returns:
            Lista de tópicos que contêm o termo.
        """
        termo_lower = termo.lower()
        return [t for t in self._topicos if termo_lower in t.indice.lower()]

    def arvore_topico(self, hierarquia: str) -> dict:
        """
        Retorna a árvore de um tópico com seus filhos.

        Args:
            hierarquia: Código hierárquico do tópico.

        Returns:
            Dicionário representando a árvore.
        """
        # Encontra o tópico
        topico = next((t for t in self._topicos if t.hierarquia == hierarquia), None)

        if not topico:
            return {}

        # Busca filhos recursivamente
        def buscar_filhos(pai: Topico) -> list[dict]:
            filhos = self._validador.buscar_filhos_diretos(pai)
            return [
                {
                    "hierarquia": f.hierarquia,
                    "indice": f.indice,
                    "quantidade": f.quantidade,
                    "porcentagem": f.porcentagem,
                    "filhos": buscar_filhos(f)
                }
                for f in filhos
            ]

        return {
            "hierarquia": topico.hierarquia,
            "indice": topico.indice,
            "quantidade": topico.quantidade,
            "porcentagem": topico.porcentagem,
            "filhos": buscar_filhos(topico)
        }

    def resumo(self) -> str:
        """
        Gera um resumo textual da análise.

        Returns:
            String formatada com o resumo.
        """
        linhas = [
            "=" * 60,
            f"📊 ANÁLISE: {self.nome_disciplina}",
            "=" * 60,
            "",
            f"📈 Total de questões: {self.total_questoes:,}",
            f"📚 Total de tópicos: {len(self._topicos)}",
            "",
            "Distribuição por nível:",
        ]

        for nivel, qtd in self.distribuicao_niveis().items():
            linhas.append(f"  Nível {nivel}: {qtd} tópicos")

        linhas.extend(["", "🏆 TOP 5 Tópicos (Nível 1):"])

        for item in self.ranking_topicos(nivel=1, limite=5):
            t = item.topico
            nome = t.indice[:40] + "..." if len(t.indice) > 40 else t.indice
            linhas.append(
                f"  {item.posicao}. [{t.hierarquia}] {nome} "
                f"({t.quantidade:,} | {t.porcentagem:.2f}%)"
            )

        linhas.append("=" * 60)

        return "\n".join(linhas)
