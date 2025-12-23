"""
Testes para os modelos de dados.
"""



from porcentagem_cespe.models import Inconsistencia, Topico


class TestTopico:
    """Testes para a classe Topico."""

    def test_nivel_raiz(self):
        """Hierarquia vazia deve ter nível 0."""
        topico = Topico(hierarquia="", indice="Total", quantidade=100, porcentagem=100.0)
        assert topico.nivel == 0

    def test_nivel_1(self):
        """Hierarquia simples deve ter nível 1."""
        topico = Topico(hierarquia="01", indice="Tópico 1", quantidade=50, porcentagem=50.0)
        assert topico.nivel == 1

    def test_nivel_2(self):
        """Hierarquia com um ponto deve ter nível 2."""
        topico = Topico(hierarquia="01.02", indice="Subtópico", quantidade=25, porcentagem=25.0)
        assert topico.nivel == 2

    def test_nivel_5(self):
        """Hierarquia profunda deve ter nível correto."""
        topico = Topico(
            hierarquia="10.08.22.01.01",
            indice="Detalhado",
            quantidade=5,
            porcentagem=0.05
        )
        assert topico.nivel == 5

    def test_pai_raiz(self):
        """Tópico raiz não tem pai."""
        topico = Topico(hierarquia="", indice="Total", quantidade=100, porcentagem=100.0)
        assert topico.pai is None

    def test_pai_nivel_1(self):
        """Tópico de nível 1 tem raiz como pai."""
        topico = Topico(hierarquia="01", indice="Tópico", quantidade=50, porcentagem=50.0)
        assert topico.pai == ""

    def test_pai_nivel_2(self):
        """Tópico de nível 2 tem o código correto do pai."""
        topico = Topico(hierarquia="01.02", indice="Subtópico", quantidade=25, porcentagem=25.0)
        assert topico.pai == "01"

    def test_pai_nivel_profundo(self):
        """Tópico profundo tem o código correto do pai."""
        topico = Topico(
            hierarquia="10.08.22.01",
            indice="Detalhado",
            quantidade=5,
            porcentagem=0.05
        )
        assert topico.pai == "10.08.22"

    def test_eh_filho_de_raiz(self):
        """Tópico de nível 1 é filho da raiz."""
        raiz = Topico(hierarquia="", indice="Total", quantidade=100, porcentagem=100.0)
        filho = Topico(hierarquia="01", indice="Tópico", quantidade=50, porcentagem=50.0)
        assert filho.eh_filho_de(raiz)

    def test_eh_filho_direto(self):
        """Verifica filho direto corretamente."""
        pai = Topico(hierarquia="02", indice="Pai", quantidade=100, porcentagem=10.0)
        filho = Topico(hierarquia="02.01", indice="Filho", quantidade=50, porcentagem=5.0)
        neto = Topico(hierarquia="02.01.01", indice="Neto", quantidade=25, porcentagem=2.5)

        assert filho.eh_filho_de(pai)
        assert not neto.eh_filho_de(pai)  # Neto não é filho DIRETO
        assert neto.eh_filho_de(filho)

    def test_nao_eh_filho(self):
        """Verifica que tópicos não relacionados não são filhos."""
        topico1 = Topico(hierarquia="02.01", indice="A", quantidade=50, porcentagem=5.0)
        topico2 = Topico(hierarquia="03.01", indice="B", quantidade=50, porcentagem=5.0)

        assert not topico2.eh_filho_de(topico1)

    def test_str_representacao(self):
        """Verifica representação em string."""
        topico = Topico(hierarquia="01", indice="Conceito", quantidade=100, porcentagem=10.0)
        assert "[01]" in str(topico)
        assert "Conceito" in str(topico)


class TestInconsistencia:
    """Testes para a classe Inconsistencia."""

    def test_gravidade_critica(self):
        """Erro maior que 10% é crítico."""
        pai = Topico(hierarquia="01", indice="Pai", quantidade=100, porcentagem=10.0)
        inc = Inconsistencia(
            tipo="SOMA_INCORRETA",
            pai=pai,
            soma_filhos=85,  # 15% de diferença
            diferenca=15,
            filhos=[]
        )
        assert inc.gravidade == "CRÍTICA"

    def test_gravidade_alta(self):
        """Erro entre 5% e 10% é alta."""
        pai = Topico(hierarquia="01", indice="Pai", quantidade=100, porcentagem=10.0)
        inc = Inconsistencia(
            tipo="SOMA_INCORRETA",
            pai=pai,
            soma_filhos=93,  # 7% de diferença
            diferenca=7,
            filhos=[]
        )
        assert inc.gravidade == "ALTA"

    def test_gravidade_media(self):
        """Erro entre 1% e 5% é média."""
        pai = Topico(hierarquia="01", indice="Pai", quantidade=100, porcentagem=10.0)
        inc = Inconsistencia(
            tipo="SOMA_INCORRETA",
            pai=pai,
            soma_filhos=97,  # 3% de diferença
            diferenca=3,
            filhos=[]
        )
        assert inc.gravidade == "MÉDIA"

    def test_gravidade_baixa(self):
        """Erro menor que 1% é baixa."""
        pai = Topico(hierarquia="01", indice="Pai", quantidade=1000, porcentagem=10.0)
        inc = Inconsistencia(
            tipo="SOMA_INCORRETA",
            pai=pai,
            soma_filhos=995,  # 0.5% de diferença
            diferenca=5,
            filhos=[]
        )
        assert inc.gravidade == "BAIXA"

    def test_gravidade_limites(self):
        """Testa os limites exatos das faixas de gravidade."""
        pai = Topico(hierarquia="01", indice="Pai", quantidade=100, porcentagem=10.0)

        # Exatamente 10% -> ALTA (pois é > 10 para ser CRÍTICA)
        inc10 = Inconsistencia("SOMA", pai, 90, 10)
        assert inc10.gravidade == "ALTA"

        # Exatamente 5% -> MÉDIA (pois é > 5 para ser ALTA)
        inc5 = Inconsistencia("SOMA", pai, 95, 5)
        assert inc5.gravidade == "MÉDIA"

        # Exatamente 1% -> BAIXA (pois é > 1 para ser MÉDIA)
        inc1 = Inconsistencia("SOMA", pai, 99, 1)
        assert inc1.gravidade == "BAIXA"

        # Um pouco acima dos limites
        assert Inconsistencia("SOMA", pai, 89, 11).gravidade == "CRÍTICA"
        assert Inconsistencia("SOMA", pai, 94, 6).gravidade == "ALTA"
        assert Inconsistencia("SOMA", pai, 98, 2).gravidade == "MÉDIA"
