"""
Testes para o validador de hierarquia.
"""

import pytest

from porcentagem_cespe.validador import ValidadorHierarquia


@pytest.fixture
def csv_valido(tmp_path):
    """Cria um arquivo CSV válido para testes."""
    conteudo = (
        "sheet_name,Hierarquia,Índice,Quantidade encontrada,"
        "Porcentagem,Quantidade no caderno,Porcentagem.1\n"
        "Índice do Caderno,,Total,100,100.00%,100,100.00%\n"
        "Índice do Caderno,01,Tópico 1,60,60.00%,60,60.00%\n"
        "Índice do Caderno,01.01,Subtópico 1.1,35,35.00%,35,35.00%\n"
        "Índice do Caderno,01.02,Subtópico 1.2,25,25.00%,25,25.00%\n"
        "Índice do Caderno,02,Tópico 2,40,40.00%,40,40.00%\n"
    )
    arquivo = tmp_path / "valido.csv"
    arquivo.write_text(conteudo, encoding="utf-8")
    return arquivo


@pytest.fixture
def csv_invalido(tmp_path):
    """Cria um arquivo CSV com inconsistência."""
    conteudo = (
        "sheet_name,Hierarquia,Índice,Quantidade encontrada,"
        "Porcentagem,Quantidade no caderno,Porcentagem.1\n"
        "Índice do Caderno,,Total,100,100.00%,100,100.00%\n"
        "Índice do Caderno,01,Tópico 1,60,60.00%,60,60.00%\n"
        "Índice do Caderno,01.01,Subtópico 1.1,30,30.00%,30,30.00%\n"
        "Índice do Caderno,01.02,Subtópico 1.2,25,25.00%,25,25.00%\n"
        "Índice do Caderno,02,Tópico 2,40,40.00%,40,40.00%\n"
    )
    # Inconsistência: 01 = 60, mas 01.01 + 01.02 = 55
    arquivo = tmp_path / "invalido.csv"
    arquivo.write_text(conteudo, encoding="utf-8")
    return arquivo


class TestValidadorHierarquia:
    """Testes para ValidadorHierarquia."""

    def test_carregar_csv_valido(self, csv_valido):
        """Deve carregar CSV válido com sucesso."""
        validador = ValidadorHierarquia()
        assert validador.carregar_csv(csv_valido)
        assert len(validador.topicos) == 5

    def test_carregar_csv_inexistente(self):
        """Deve retornar False para arquivo inexistente."""
        validador = ValidadorHierarquia()
        assert not validador.carregar_csv("/caminho/inexistente.csv")

    def test_total_geral_identificado(self, csv_valido):
        """Deve identificar o tópico raiz corretamente."""
        validador = ValidadorHierarquia()
        validador.carregar_csv(csv_valido)

        assert validador.total_geral is not None
        assert validador.total_geral.hierarquia == ""
        assert validador.total_geral.quantidade == 100

    def test_validar_dados_validos(self, csv_valido):
        """Dados válidos não devem gerar inconsistências."""
        validador = ValidadorHierarquia()
        validador.carregar_csv(csv_valido)

        inconsistencias = validador.validar()
        assert len(inconsistencias) == 0

    def test_validar_dados_invalidos(self, csv_invalido):
        """Dados inválidos devem gerar inconsistências."""
        validador = ValidadorHierarquia()
        validador.carregar_csv(csv_invalido)

        inconsistencias = validador.validar()
        assert len(inconsistencias) >= 1

        # A inconsistência deve ser no tópico 01
        inc = inconsistencias[0]
        assert inc.pai.hierarquia == "01"
        assert inc.pai.quantidade == 60
        assert inc.soma_filhos == 55
        assert inc.diferenca == 5

    def test_buscar_filhos_diretos(self, csv_valido):
        """Deve encontrar apenas filhos diretos."""
        validador = ValidadorHierarquia()
        validador.carregar_csv(csv_valido)

        # Encontra o tópico 01
        topico_01 = next((t for t in validador.topicos if t.hierarquia == "01"), None)
        assert topico_01 is not None

        filhos = validador.buscar_filhos_diretos(topico_01)
        assert len(filhos) == 2

        hierarquias = [f.hierarquia for f in filhos]
        assert "01.01" in hierarquias
        assert "01.02" in hierarquias

    def test_buscar_filhos_raiz(self, csv_valido):
        """Deve encontrar filhos da raiz corretamente."""
        validador = ValidadorHierarquia()
        validador.carregar_csv(csv_valido)

        filhos = validador.buscar_filhos_diretos(validador.total_geral)
        assert len(filhos) == 2

        hierarquias = [f.hierarquia for f in filhos]
        assert "01" in hierarquias
        assert "02" in hierarquias

    def test_validar_arquivo_completo(self, csv_valido):
        """Deve validar arquivo e retornar ResultadoValidacao."""
        validador = ValidadorHierarquia()
        resultado = validador.validar_arquivo(csv_valido)

        assert resultado.valido
        assert resultado.total_topicos == 5
        assert resultado.total_questoes == 100
        assert len(resultado.inconsistencias) == 0

    def test_validar_arquivo_invalido(self, csv_invalido):
        """Deve detectar inconsistências em arquivo inválido."""
        validador = ValidadorHierarquia()
        resultado = validador.validar_arquivo(csv_invalido)

        assert not resultado.valido
        assert len(resultado.inconsistencias) >= 1
