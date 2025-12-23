"""
Modelos de dados para representação de tópicos e validações.
"""

from dataclasses import dataclass, field


@dataclass
class Topico:
    """
    Representa um tópico na hierarquia de dados.

    Attributes:
        hierarquia: Código hierárquico (ex: '02.01.03')
        indice: Nome/descrição do tópico
        quantidade: Total de questões sobre o tópico
        porcentagem: Porcentagem em relação ao total geral
        linha_csv: Número da linha no arquivo CSV original
    """
    hierarquia: str
    indice: str
    quantidade: int
    porcentagem: float
    linha_csv: int = 0

    @property
    def nivel(self) -> int:
        """
        Retorna o nível de profundidade do tópico.

        - Nível 0: Raiz (hierarquia vazia)
        - Nível 1: Categorias principais (01, 02, 03...)
        - Nível 2: Subcategorias (01.01, 02.03...)
        - E assim por diante
        """
        if not self.hierarquia:
            return 0
        return self.hierarquia.count('.') + 1

    @property
    def pai(self) -> str | None:
        """
        Retorna o código hierárquico do tópico pai.

        Exemplos:
            - '02.01.03' -> '02.01'
            - '02.01' -> '02'
            - '02' -> '' (raiz)
            - '' -> None
        """
        if not self.hierarquia:
            return None
        if '.' not in self.hierarquia:
            return ""  # O pai é a raiz
        return '.'.join(self.hierarquia.split('.')[:-1])

    @property
    def codigo_curto(self) -> str:
        """Retorna apenas o último segmento do código."""
        if not self.hierarquia:
            return "RAIZ"
        return self.hierarquia.split('.')[-1]

    def eh_filho_de(self, outro: "Topico") -> bool:
        """Verifica se este tópico é filho direto de outro."""
        if not outro.hierarquia:
            # O outro é a raiz, então este é filho se for nível 1
            return self.nivel == 1

        prefixo = outro.hierarquia + "."
        if not self.hierarquia.startswith(prefixo):
            return False

        # Verifica se é filho DIRETO (apenas um nível abaixo)
        resto = self.hierarquia[len(prefixo):]
        return '.' not in resto

    def __str__(self) -> str:
        codigo = self.hierarquia or "RAIZ"
        nome = self.indice[:50] + "..." if len(self.indice) > 50 else self.indice
        return f"[{codigo}] {nome}"

    def __repr__(self) -> str:
        return (
            f"Topico(hierarquia='{self.hierarquia}', "
            f"quantidade={self.quantidade}, nivel={self.nivel})"
        )


@dataclass
class Inconsistencia:
    """
    Representa uma inconsistência encontrada na validação.

    Attributes:
        tipo: Tipo de inconsistência (SOMA_INCORRETA, PORCENTAGEM_INCORRETA, etc.)
        pai: Tópico pai onde a inconsistência foi encontrada
        soma_filhos: Soma das quantidades dos filhos diretos
        diferenca: Diferença entre valor do pai e soma dos filhos
        filhos: Lista de tópicos filhos diretos
    """
    tipo: str
    pai: Topico
    soma_filhos: int
    diferenca: int
    filhos: list[Topico] = field(default_factory=list)

    @property
    def gravidade(self) -> str:
        """Classifica a gravidade da inconsistência."""
        pct_erro = abs(self.diferenca) / self.pai.quantidade * 100 if self.pai.quantidade else 0

        if pct_erro > 10:
            return "CRÍTICA"
        elif pct_erro > 5:
            return "ALTA"
        elif pct_erro > 1:
            return "MÉDIA"
        else:
            return "BAIXA"

    def __str__(self) -> str:
        return (
            f"[{self.gravidade}] {self.tipo}: {self.pai.hierarquia or 'RAIZ'}\n"
            f"  Valor do pai: {self.pai.quantidade:,}\n"
            f"  Soma dos filhos: {self.soma_filhos:,}\n"
            f"  Diferença: {self.diferenca:+,}"
        )


@dataclass
class ResultadoValidacao:
    """
    Resultado completo de uma validação.

    Attributes:
        arquivo: Nome do arquivo validado
        total_topicos: Total de tópicos encontrados
        total_questoes: Total de questões
        inconsistencias: Lista de inconsistências encontradas
        valido: Se os dados estão íntegros
    """
    arquivo: str
    total_topicos: int
    total_questoes: int
    inconsistencias: list[Inconsistencia] = field(default_factory=list)

    @property
    def valido(self) -> bool:
        """
        Indica se o arquivo é considerado válido (sem inconsistências).

        Returns:
            True se a lista de inconsistências estiver vazia, False caso contrário.
        """
        return not self.inconsistencias

    @property
    def resumo(self) -> str:
        """Retorna um resumo da validação."""
        status = "✅ ÍNTEGRO" if self.valido else f"❌ {len(self.inconsistencias)} ERRO(S)"
        return (
            f"{self.arquivo}: {status} "
            f"({self.total_topicos} tópicos, {self.total_questoes:,} questões)"
        )
