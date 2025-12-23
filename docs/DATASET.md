# 📊 Dataset Consolidado - Porcentagem CESPE

> **Versão**: 1.0.0
> **Data de Criação**: 23/12/2024
> **Autor**: Gerado automaticamente via `scripts/criar_dataset.py`

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquivos Gerados](#arquivos-gerados)
3. [Estrutura do Dataset](#estrutura-do-dataset)
4. [Fontes de Dados](#fontes-de-dados)
5. [Como Usar](#como-usar)
6. [Boas Práticas](#boas-práticas)
7. [Regenerar o Dataset](#regenerar-o-dataset)

---

## Visão Geral

O dataset consolidado reúne todas as estatísticas de questões de concursos CESPE/CEBRASPE em um único arquivo, facilitando análises comparativas entre disciplinas.

### Características

| Métrica | Valor |
|---------|-------|
| **Total de registros** | 1.322 |
| **Disciplinas** | 8 |
| **Níveis hierárquicos** | 0 a 5 |
| **Formatos disponíveis** | CSV, Parquet |

---

## Arquivos Gerados

```text
datasets/
├── dataset_cespe.csv          # Dataset consolidado (127 KB)
├── dataset_cespe.parquet      # Dataset em Parquet (48 KB)
└── por_disciplina/            # CSVs individuais
    ├── Administração_Financeira_e_Orçamentária.csv
    ├── Administração_Geral_e_Pública.csv
    ├── Administração_de_Recursos_Materiais.csv
    ├── Direito_Administrativo.csv
    ├── Direito_Constitucional.csv
    ├── Gestão_de_Projetos_PMBOK.csv
    ├── Língua_Portuguesa_e_Redação_Oficial.csv
    └── Ética_no_Serviço_Público.csv
```

### Quando usar cada formato

| Formato | Uso Recomendado |
|---------|-----------------|
| **CSV** | Visualização em Excel/Google Sheets, compatibilidade universal |
| **Parquet** | Análises com pandas/polars, melhor performance e menor tamanho |
| **Por disciplina** | Análises focadas em uma única disciplina |

---

## Estrutura do Dataset

### Colunas

| Coluna | Tipo | Descrição | Exemplo |
|--------|------|-----------|---------|
| `Disciplina` | String | Nome completo da disciplina | `Direito Administrativo` |
| `Hierarquia` | String | Código hierárquico do tópico | `02.01.03` |
| `Nivel` | Integer | Nível na hierarquia (0=raiz, 1-5=subníveis) | `2` |
| `Indice` | String | Nome/descrição do tópico | `Princípios Expressos` |
| `Quantidade` | Integer | Total de questões encontradas sobre o tópico | `411` |
| `Quantidade_Caderno` | Integer | Quantidade registrada no caderno | `411` |

### Sobre a coluna `Quantidade_Caderno`

Na maioria dos casos, `Quantidade` e `Quantidade_Caderno` são idênticos. Porém, existe pelo menos uma diferença significativa:

| Disciplina | Tópico | Quantidade | Quantidade_Caderno |
|------------|--------|------------|-------------------|
| Gestão de Projetos | PMBOK 7ª Edição | 74 | 49 |

Isso pode indicar questões encontradas mas não incluídas no caderno final.

### Níveis Hierárquicos

| Nível | Descrição | Quantidade de Registros | Exemplo |
|-------|-----------|------------------------|---------|
| 0 | **Total da disciplina** (soma de todos os tópicos) | 9 | `(vazio)` |
| 1 | Categoria principal | 145 | `01`, `02` |
| 2 | Subcategoria | 578 | `02.01`, `03.05` |
| 3 | Sub-subcategoria | 383 | `02.01.01` |
| 4 | Detalhamento | 188 | `10.08.22.01` |
| 5 | Detalhamento máximo | 19 | `10.08.22.01.01` |

> **Nota**: O nível 0 contém a soma total de questões de cada disciplina. A soma de todos os itens de nível 1 deve ser igual ao valor do nível 0.

---

## Fontes de Dados

O dataset é gerado a partir dos seguintes arquivos XLSX:

| Arquivo Origem | Disciplina | Registros |
|---------------|------------|-----------|
| `AFO.xlsx` | Administração Financeira e Orçamentária | 148 |
| `AdmGeralPublica.xlsx` | Administração Geral e Pública | 164 |
| `DConst.xlsx` | Direito Constitucional | 308 |
| `DireitoAdm.xlsx` | Direito Administrativo | 478 |
| `Etica.xlsx` | Ética no Serviço Público | 15 |
| `GestaoProjetos.xlsx` | Gestão de Projetos (PMBOK) | 38 |
| `Port_RedOficial.xlsx` | Língua Portuguesa e Redação Oficial | 134 |
| `adm_de_recursos_materiais.xlsx` | Administração de Recursos Materiais | 37 |

> **Nota**: O arquivo `todsass.xlsx` foi excluído por ser um consolidado parcial.

---

## Como Usar

### Com pandas (Python)

```python
import pandas as pd

# Carregar CSV
df = pd.read_csv("datasets/dataset_cespe.csv")

# Ou carregar Parquet (mais eficiente)
df = pd.read_parquet("datasets/dataset_cespe.parquet")

# Filtrar por disciplina
dir_adm = df[df["Disciplina"] == "Direito Administrativo"]

# Filtrar por nível (apenas categorias principais)
nivel1 = df[df["Nivel"] == 1]

# Top 10 tópicos mais cobrados
top10 = df[df["Nivel"] == 1].nlargest(10, "Quantidade")
print(top10[["Disciplina", "Indice", "Quantidade"]])
```

### Calcular Porcentagens

```python
# Porcentagem dentro de cada disciplina
df["Porcentagem"] = df.groupby("Disciplina")["Quantidade"].transform(
    lambda x: (x / x.max()) * 100
)

# Porcentagem relativa ao total geral
total_geral = df[df["Nivel"] == 0]["Quantidade"].sum()
df["Porcentagem_Global"] = (df["Quantidade"] / total_geral) * 100
```

### Com polars (mais rápido)

```python
import polars as pl

# Carregar
df = pl.read_parquet("datasets/dataset_cespe.parquet")

# Filtrar e agregar
resultado = (
    df.filter(pl.col("Nivel") == 1)
    .group_by("Disciplina")
    .agg(pl.col("Quantidade").sum())
    .sort("Quantidade", descending=True)
)
```

---

## Boas Práticas

### ✅ Faça

1. **Calcule porcentagens na análise, não no armazenamento** - As colunas de porcentagem foram removidas intencionalmente
2. **Use o nível correto** - Para totais por disciplina, filtre `Nivel == 0`
3. **Evite dupla contagem** - Use pai **OU** filhos, nunca ambos (ver- [HIERARQUIA_DADOS.md](HIERARQUIA_DADOS.md) - Regras de hierarquia
- [DATASET.md](DATASET.md) - Documentação do dataset rápido

### ❌ Evite

1. **Somar pai + filhos** - Resulta em dupla contagem
2. **Misturar níveis diferentes** - Compare apenas itens do mesmo nível
3. **Ignorar a hierarquia** - Os dados têm relacionamento pai-filho

---

## Regenerar o Dataset

Para regenerar o dataset após alterações nos arquivos XLSX:

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Executar script
python scripts/criar_dataset.py
```

### Dependências

```bash
uv pip install pandas openpyxl pyarrow
```

### Saída esperada

```text
============================================================
CRIANDO DATASET CONSOLIDADO
============================================================

📄 Processando: AFO.xlsx
   → 148 registros carregados
...

✅ CSV salvo: datasets/dataset_cespe.csv
✅ Parquet salvo: datasets/dataset_cespe.parquet
✅ CSVs individuais salvos em: datasets/por_disciplina
```

---

## Validação de Integridade

O dataset segue as regras de hierarquia documentadas em [HIERARQUIA_DADOS.md](HIERARQUIA_DADOS.md).

Para validar a integridade dos dados:

```bash
python -m porcentagem_cespe validar
```

---

## Changelog

### v1.0.0 (23/12/2024)

- Criação inicial do dataset consolidado
- Suporte a CSV e Parquet
- 8 disciplinas, 1.322 registros
- Remoção das colunas de porcentagem (devem ser calculadas na análise)

---

Documentação gerada para o projeto Porcentagem CESPE
