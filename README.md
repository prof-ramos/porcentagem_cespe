# 📊 Porcentagem CESPE

> Análise estatística de questões de concursos CESPE/CEBRASPE organizadas por tópicos hierárquicos.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Estrutura dos Dados](#estrutura-dos-dados)
- [Desenvolvimento](#desenvolvimento)
- [Licença](#licença)

---

## Sobre o Projeto

Este projeto fornece ferramentas para análise de dados estatísticos de questões de concursos públicos organizadas por uma **estrutura hierárquica multinível**.

### Funcionalidades

- ✅ **Validação de Integridade**: Verifica se a soma dos filhos é igual ao valor do pai
- 📊 **Análise Estatística**: Rankings, distribuições e métricas por tópico
- 🔍 **Busca e Filtros**: Encontre tópicos por termo ou nível hierárquico
- 📈 **Relatórios**: Geração de resumos e relatórios detalhados

---

## Estrutura do Projeto

```text
porcentagem_cespe/
├── 📂 src/
│   └── porcentagem_cespe/       # Pacote principal
│       ├── __init__.py          # Exports públicos
│       ├── __main__.py          # Entry point
│       ├── cli.py               # Interface de linha de comando
│       ├── models.py            # Modelos de dados
│       ├── validador.py         # Validação de hierarquia
│       └── analisador.py        # Análise estatística
├── 📂 tests/                    # Testes unitários
│   ├── test_models.py
│   └── test_validador.py
├── 📂 data/                     # Arquivos fonte (XLSX)
│   ├── *.xlsx                   # Planilhas por disciplina
│   └── csv/                     # Arquivos CSV convertidos
├── 📂 datasets/                 # Dataset consolidado
│   ├── dataset_cespe.csv        # Todas as disciplinas
│   ├── dataset_cespe.parquet    # Formato otimizado
│   └── por_disciplina/          # CSVs individuais
├── 📂 docs/                     # Documentação
│   ├── HIERARQUIA_DADOS.md      # Regras de hierarquia
│   └── DATASET.md               # Documentação do dataset
├── 📂 scripts/                  # Scripts utilitários
│   ├── criar_dataset.py         # Gera dataset consolidado
│   └── validar_hierarquia.py    # Script standalone
├── pyproject.toml               # Configuração do projeto
└── README.md
```

---

## Instalação

### Requisitos

- Python 3.10 ou superior
- [uv](https://github.com/astral-sh/uv) (altamente recomendado) ou pip

> **Recomendação**: Utilize o **uv** para uma experiência de desenvolvimento muito mais rápida e confiável. Ele substitui `pip`, `pip-tools` e `virtualenv` com performance superior.

### Instalação com uv

```bash
# Clone o repositório
git clone https://github.com/prof-ramos/porcentagem_cespe.git
cd porcentagem_cespe

# Crie o ambiente virtual e instale dependências
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Instale o projeto em modo desenvolvimento
uv pip install -e ".[dev]"
```

### Instalação com pip

```bash
pip install -e ".[dev]"
```

---

## Uso

### Linha de Comando

```bash
# Validar todos os arquivos CSV
python -m porcentagem_cespe validar

# Validar um arquivo específico
python -m porcentagem_cespe validar DireitoAdm.csv

# Validar com detalhes
python -m porcentagem_cespe validar --verbose

# Analisar um arquivo
python -m porcentagem_cespe analisar DireitoAdm.csv
```

### Como Biblioteca Python

```python
from porcentagem_cespe import ValidadorHierarquia, AnalisadorDados

# Validação
validador = ValidadorHierarquia(verbose=True)
resultado = validador.validar_arquivo("data/csv/DireitoAdm.csv")

if resultado.valido:
    print("✅ Dados íntegros!")
else:
    for inc in resultado.inconsistencias:
        print(f"❌ {inc}")

# Análise
analisador = AnalisadorDados()
analisador.carregar("data/csv/DireitoAdm.csv")

# Top 10 tópicos mais cobrados
for item in analisador.ranking_topicos(nivel=1, limite=10):
    print(f"{item.posicao}. {item.topico.indice}: {item.topico.quantidade}")
```

---

## Estrutura dos Dados

### Regra Fundamental

> **A quantidade de um tópico pai é IGUAL à soma das quantidades de seus filhos diretos.**

```text
Qtd(Pai) = Σ Qtd(Filhos Diretos)
```

### Hierarquia

Os dados utilizam um sistema de numeração decimal com até 5 níveis:

| Nível | Formato | Exemplo |
|-------|---------|---------|
| 0 | (vazio) | Raiz/Total |
| 1 | XX | 01, 02, 03 |
| 2 | XX.XX | 02.01, 10.06 |
| 3 | XX.XX.XX | 05.01.01 |
| 4 | XX.XX.XX.XX | 10.08.22.01 |
| 5 | XX.XX.XX.XX.XX | 10.08.22.01.01 |

### Arquivos CSV Disponíveis

| Arquivo | Disciplina |
|---------|------------|
| `DireitoAdm.csv` | Direito Administrativo |
| `DConst.csv` | Direito Constitucional |
| `AFO.csv` | Administração Financeira e Orçamentária |
| `AdmGeralPublica.csv` | Administração Geral e Pública |
| `Etica.csv` | Ética |
| `Port_RedOficial.csv` | Português e Redação Oficial |
| `GestaoProjetos.csv` | Gestão de Projetos |

### Dataset Consolidado

Todas as disciplinas estão disponíveis em um único dataset em `datasets/`:

```bash
# Gerar/atualizar o dataset consolidado
python scripts/criar_dataset.py
```

| Arquivo | Descrição |
|---------|-----------|
| `dataset_cespe.csv` | Todas as disciplinas (1.322 registros) |
| `dataset_cespe.parquet` | Formato otimizado para análises |
| `por_disciplina/*.csv` | Um CSV por disciplina |

Para mais detalhes, consulte:

- [docs/HIERARQUIA_DADOS.md](docs/HIERARQUIA_DADOS.md) - Regras de hierarquia
- [docs/DATASET.md](docs/DATASET.md) - Documentação do dataset

---

## Desenvolvimento

### Executar Testes

```bash
# Executar todos os testes
pytest

# Com cobertura
pytest --cov=porcentagem_cespe --cov-report=html

# Testes específicos
pytest tests/test_models.py -v
```

### Linting e Formatação

```bash
# Verificar código
ruff check src/

# Formatar código
ruff format src/

# Verificar tipos
mypy src/
```

### Estrutura de um Teste

```python
from porcentagem_cespe.models import Topico

def test_nivel_topico():
    topico = Topico(hierarquia="02.01", indice="Teste", quantidade=100, porcentagem=10.0)
    assert topico.nivel == 2
    assert topico.pai == "02"
```

---

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

*Desenvolvido para análise de questões de concursos públicos* 📚
