"""
Módulo de validação de hierarquia de dados.

Este módulo fornece a classe ValidadorHierarquia para verificar
a integridade dos dados hierárquicos nos arquivos CSV.
"""

import csv
from pathlib import Path

from porcentagem_cespe.models import Inconsistencia, ResultadoValidacao, Topico


class ValidadorHierarquia:
    """
    Validador de hierarquia de dados CSV.

    Verifica se a soma das quantidades dos filhos é igual
    ao valor do pai em todos os níveis da hierarquia.

    Exemplo de uso:
        >>> validador = ValidadorHierarquia()
        >>> resultado = validador.validar_arquivo("dados.csv")
        >>> print(resultado.resumo)
    """

    def __init__(self, verbose: bool = False):
        """
        Inicializa o validador.

        Args:
            verbose: Se True, imprime detalhes durante a validação.
        """
        self.verbose = verbose
        self._topicos: list[Topico] = []
        self._total_geral: Topico | None = None

    @property
    def topicos(self) -> list[Topico]:
        """Retorna a lista de tópicos carregados."""
        return self._topicos

    @property
    def total_geral(self) -> Topico | None:
        """Retorna o tópico raiz (total geral)."""
        return self._total_geral

    def carregar_csv(self, caminho: str | Path) -> bool:
        """
        Carrega e parseia um arquivo CSV.

        Args:
            caminho: Caminho para o arquivo CSV.

        Returns:
            True se o carregamento foi bem-sucedido, False caso contrário.
        """
        self._topicos.clear()
        self._total_geral = None

        caminho = Path(caminho)

        if not caminho.exists():
            if self.verbose:
                print(f"❌ Arquivo não encontrado: {caminho}")
            return False

        try:
            with open(caminho, encoding='utf-8') as arquivo:
                leitor = csv.DictReader(arquivo)

                for num_linha, linha in enumerate(leitor, start=2):
                    topico = self._parsear_linha(linha, num_linha)
                    self._topicos.append(topico)

                    # Identifica o total geral (hierarquia vazia)
                    if not topico.hierarquia:
                        self._total_geral = topico

            if self.verbose:
                print(f"📂 Carregados {len(self._topicos)} tópicos de {caminho.name}")

            return True

        except Exception as e:
            if self.verbose:
                print(f"❌ Erro ao ler arquivo: {e}")
            return False

    def _parsear_linha(self, linha: dict, num_linha: int) -> Topico:
        """Parseia uma linha do CSV em um objeto Topico."""
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
                print(f"⚠️  Valor inválido para quantidade: '{qtd_str}'. Usando 0.")

        # Parse porcentagem
        pct_str = linha.get('Porcentagem', '0%')
        pct_str = pct_str.replace('%', '').replace(',', '.').strip()
        try:
            porcentagem = float(pct_str) if pct_str else 0.0
        except ValueError:
            porcentagem = 0.0
            if self.verbose:
                print(f"⚠️  Valor inválido para porcentagem: '{pct_str}'. Usando 0.0.")

        return Topico(
            hierarquia=hierarquia,
            indice=indice,
            quantidade=quantidade,
            porcentagem=porcentagem,
            linha_csv=num_linha
        )

    def buscar_filhos_diretos(self, pai: Topico) -> list[Topico]:
        """
        Busca todos os filhos diretos de um tópico.

        Args:
            pai: Tópico para buscar os filhos.

        Returns:
            Lista de tópicos que são filhos diretos do pai.
        """
        filhos = []
        nivel_esperado = pai.nivel + 1

        for topico in self._topicos:
            # Pula o próprio pai
            if topico.hierarquia == pai.hierarquia:
                continue

            # Verifica se é filho direto
            if topico.nivel == nivel_esperado and topico.eh_filho_de(pai):
                filhos.append(topico)

        return filhos

    def validar(self) -> list[Inconsistencia]:
        """
        Executa a validação completa dos dados carregados.

        Returns:
            Lista de inconsistências encontradas.
        """
        if not self._topicos:
            return []

        inconsistencias: list[Inconsistencia] = []

        for topico in self._topicos:
            filhos = self.buscar_filhos_diretos(topico)

            # Se não tem filhos, é um nó folha (válido)
            if not filhos:
                continue

            # Calcula a soma dos filhos
            soma_filhos = sum(f.quantidade for f in filhos)

            # Verifica consistência
            if soma_filhos != topico.quantidade:
                diferenca = topico.quantidade - soma_filhos

                inconsistencias.append(Inconsistencia(
                    tipo="SOMA_INCORRETA",
                    pai=topico,
                    soma_filhos=soma_filhos,
                    diferenca=diferenca,
                    filhos=filhos
                ))

        return inconsistencias

    def validar_arquivo(self, caminho: str | Path) -> ResultadoValidacao:
        """
        Valida um arquivo CSV completo.

        Args:
            caminho: Caminho para o arquivo CSV.

        Returns:
            Objeto ResultadoValidacao com o resultado completo.
        """
        caminho = Path(caminho)

        if not self.carregar_csv(caminho):
            return ResultadoValidacao(
                arquivo=caminho.name,
                total_topicos=0,
                total_questoes=0,
                inconsistencias=[]
            )

        inconsistencias = self.validar()

        return ResultadoValidacao(
            arquivo=caminho.name,
            total_topicos=len(self._topicos),
            total_questoes=self._total_geral.quantidade if self._total_geral else 0,
            inconsistencias=inconsistencias
        )

    def validar_porcentagens(self, tolerancia: float = 0.01) -> list[Topico]:
        """
        Valida se as porcentagens estão corretas.

        Args:
            tolerancia: Tolerância para diferenças de arredondamento (padrão: 0.01%)

        Returns:
            Lista de tópicos com porcentagens incorretas.
        """
        erros: list[Topico] = []

        if not self._total_geral:
            return erros

        total = self._total_geral.quantidade

        for topico in self._topicos:
            if topico == self._total_geral:
                continue

            pct_esperada = (topico.quantidade / total) * 100 if total > 0 else 0
            diferenca = abs(pct_esperada - topico.porcentagem)

            if diferenca > tolerancia:
                erros.append(topico)
                if self.verbose:
                    print(
                        f"⚠️  Porcentagem: {topico.hierarquia} - "
                        f"Esperado: {pct_esperada:.2f}%, "
                        f"Encontrado: {topico.porcentagem:.2f}%"
                    )

        return erros
