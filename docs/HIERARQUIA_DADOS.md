# 📊 Documentação da Hierarquia de Dados - Porcentagem CESPE

> **Versão**: 1.0.0
> **Data**: 23/12/2024
> **Autor**: Documentação gerada automaticamente

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Estrutura do Arquivo CSV](#estrutura-do-arquivo-csv)
3. [Sistema de Hierarquia](#sistema-de-hierarquia)
4. [Regras de Cálculo](#regras-de-cálculo)
5. [Exemplos Práticos](#exemplos-práticos)
6. [Cuidados e Alertas](#cuidados-e-alertas)
7. [Validação de Integridade](#validação-de-integridade)

---

## Visão Geral

Os arquivos CSV deste projeto contêm dados estatísticos de questões de concursos organizados por uma **estrutura hierárquica multinível**. Esta documentação explica as regras fundamentais para evitar erros de cálculo ao manipular esses dados.

### Princípio Fundamental

> **⚠️ IMPORTANTE**: Os valores de quantidade e porcentagem nos níveis superiores da hierarquia são **ACUMULATIVOS**, ou seja, representam a **SOMA** de todos os seus filhos diretos.

---

## Estrutura do Arquivo CSV

### Colunas

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `sheet_name` | String | Nome da planilha de origem (ex: "Índice do Caderno") |
| `Hierarquia` | String | Código hierárquico do tópico (ex: `01`, `02.01`, `02.02.01`) |
| `Índice` | String | Nome/descrição do tópico |
| `Quantidade encontrada` | Integer | Total de questões sobre o tópico |
| `Porcentagem` | Percentage | Porcentagem em relação ao total geral |
| `Quantidade no caderno` | Integer | Quantidade registrada no caderno |
| `Porcentagem.1` | Percentage | Porcentagem no caderno |

### Linha Raiz

A **primeira linha de dados** (após o cabeçalho) representa o **total geral** da disciplina:

```csv
sheet_name,Hierarquia,Índice,Quantidade encontrada,Porcentagem,Quantidade no caderno,Porcentagem.1
Índice do Caderno,,Direito Administrativo,21928,100.00%,150,0.68%
```

- `Hierarquia`: **vazia** (sem código)
- `Quantidade encontrada`: Total de questões da disciplina
- `Porcentagem`: Sempre **100.00%**

---

## Sistema de Hierarquia

### Níveis de Profundidade

A hierarquia utiliza um **sistema de numeração decimal** com até **5 níveis**:

| Nível | Formato | Exemplo | Descrição |
|-------|---------|---------|-----------|
| 0 | (vazio) | - | Raiz/Total Geral |
| 1 | `XX` | `01`, `02` | Categoria Principal |
| 2 | `XX.XX` | `02.01`, `10.06` | Subcategoria |
| 3 | `XX.XX.XX` | `05.01.01` | Sub-subcategoria |
| 4 | `XX.XX.XX.XX` | `10.08.22.01` | Detalhamento |
| 5 | `XX.XX.XX.XX.XX` | `10.08.22.01.01` | Detalhamento Máximo |

### Relação Pai-Filho

```
Pai: 02
├── Filho: 02.01
├── Filho: 02.02
└── Filho: 02.03

Pai: 02.02
├── Filho: 02.02.01
├── Filho: 02.02.02
└── Filho: 02.02.03
```

---

## Regras de Cálculo

### ⚡ Regra 1: Soma Hierárquica

> **A quantidade de um nó pai é IGUAL à soma das quantidades de todos os seus filhos diretos.**

```
Qtd(Pai) = Σ Qtd(Filhos Diretos)
```

**Exemplo**:
```
Qtd(02) = Qtd(02.01) + Qtd(02.02) + Qtd(02.03)
669     = 54        + 411        + 204        ✅
```

### ⚡ Regra 2: Porcentagem Proporcional

> **A porcentagem é calculada em relação ao TOTAL GERAL (raiz), não ao pai imediato.**

```
Porcentagem(X) = (Qtd(X) / Qtd(Total)) × 100
```

**Exemplo**:
```
Porcentagem(02.02) = (411 / 21928) × 100 = 1.87%
```

### ⚡ Regra 3: Consistência Recursiva

> **A regra de soma hierárquica aplica-se RECURSIVAMENTE em todos os níveis.**

```
Qtd(10) = Σ Qtd(10.XX)
Qtd(10.08) = Σ Qtd(10.08.XX)
Qtd(10.08.22) = Σ Qtd(10.08.22.XX)
```

---

## Exemplos Práticos

### Exemplo 1: Regime Jurídico Administrativo

```
Tópico 02 - Regime Jurídico Administrativo: 669 questões (3.05%)

├── 02.01 - Regime Jurídico da Adm.: 54 (0.25%)
├── 02.02 - Princípios Expressos: 411 (1.87%)
└── 02.03 - Princípios Implícitos: 204 (0.93%)

Verificação: 54 + 411 + 204 = 669 ✅
Verificação %: 0.25% + 1.87% + 0.93% = 3.05% ✅
```

### Exemplo 2: Atos Administrativos

```
Tópico 03 - Atos Administrativos: 1538 questões (7.01%)

├── 03.01 - Conceito: 102 (0.47%)
├── 03.02 - Mérito Administrativo: 26 (0.12%)
├── 03.03 - Elementos, Requisitos: 187 (0.85%)
├── 03.04 - Atributos: 238 (1.09%)
├── 03.05 - Espécies, Classificação: 420 (1.92%)
├── 03.06 - Desfazimento: 395 (1.80%)
├── 03.07 - Convalidação e Conversão: 86 (0.39%)
├── 03.08 - Teoria dos Motivos: 50 (0.23%)
└── 03.09 - Tópicos Mesclados: 34 (0.16%)

Verificação: 102 + 26 + 187 + 238 + 420 + 395 + 86 + 50 + 34 = 1538 ✅
```

### Exemplo 3: Hierarquia Profunda (Nível 4)

```
Tópico 10.08.22 - Estatuto Servidores da BA: 44 questões

├── 10.08.22.01 - Do Provimento e da Vacância: 15
├── 10.08.22.02 - Dos Direitos, Vantagens e Benefícios: 6
├── 10.08.22.03 - Do Regime Disciplinar: 15
└── 10.08.22.04 - Do Processo Administrativo Disciplinar: 8

Verificação: 15 + 6 + 15 + 8 = 44 ✅
```

---

## Cuidados e Alertas

### ❌ Erros Comuns a Evitar

#### 1. Dupla Contagem
```
❌ ERRADO: Somar tópico pai + filhos
   Total = Qtd(02) + Qtd(02.01) + Qtd(02.02) + Qtd(02.03)

✅ CORRETO: Usar APENAS o pai OU APENAS os filhos
   Total = Qtd(02)
   OU
   Total = Qtd(02.01) + Qtd(02.02) + Qtd(02.03)
```

#### 2. Mistura de Níveis
```
❌ ERRADO: Somar itens de níveis diferentes
   Total = Qtd(02) + Qtd(03.01) + Qtd(04)

✅ CORRETO: Somar itens do MESMO nível
   Total = Qtd(02) + Qtd(03) + Qtd(04)
```

#### 3. Porcentagem Relativa
```
❌ ERRADO: Calcular % de filho em relação ao pai
   % de 02.01 em relação a 02 = (54/669) × 100 = 8.07%
   (Este valor NÃO está no CSV)

✅ CORRETO: Usar a % já calculada no CSV (relativa ao total)
   % de 02.01 = 0.25% (em relação ao total de 21928)
```

### ⚠️ Casos Especiais

#### Tópicos Folha (Sem Filhos)
Alguns tópicos são "folhas" da árvore e não têm subdivisões:
```
01 - Origem, Conceito e Fontes: 175 questões
(Não possui subtópicos 01.01, 01.02, etc.)
```

#### Tópicos "Mesclados"
Alguns nós têm um filho especial "Tópicos Mesclados" que agrupa questões não classificáveis:
```
03.09 - Tópicos Mesclados de Atos Administrativos: 34
```

---

## Validação de Integridade

### Script de Validação (Pseudocódigo)

> **Pseudocode — conceptual only**

```python
def validar_hierarquia(dados):
    """
    Valida se a soma dos filhos é igual ao pai
    """
    for pai in dados:
        filhos = buscar_filhos_diretos(pai)
        if filhos:
            soma_filhos = sum(filho.quantidade for filho in filhos)
            if pai.quantidade != soma_filhos:
                erro(f"Inconsistência: {pai.hierarquia}")
                erro(f"  Pai: {pai.quantidade}")
                erro(f"  Soma filhos: {soma_filhos}")
                erro(f"  Diferença: {abs(pai.quantidade - soma_filhos)}")
    return True
```

### Regra de Identificação de Filhos

Um nó `Y` é filho direto de `X` se:
1. `Y.hierarquia` começa com `X.hierarquia + "."`
2. `Y` possui exatamente **um nível a mais** que `X`

> **Pseudocode — conceptual only**

```python
def eh_filho_direto(pai, candidato):
    prefixo = pai.hierarquia + "."
    if not candidato.hierarquia.startswith(prefixo):
        return False

    nivel_pai = pai.hierarquia.count(".") + 1
    nivel_candidato = candidato.hierarquia.count(".") + 1

    return nivel_candidato == nivel_pai + 1
```

---

## Diagrama Visual

```
                    ┌─────────────────────────────────┐
                    │     TOTAL GERAL (21928)         │
                    │     Porcentagem: 100.00%        │
                    └───────────────┬─────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐          ┌───────────────┐          ┌───────────────┐
│   01 (175)    │          │   02 (669)    │          │   03 (1538)   │
│   0.80%       │          │   3.05%       │          │   7.01%       │
└───────────────┘          └───────┬───────┘          └───────┬───────┘
                                   │                          │
                    ┌──────────────┼──────────────┐           │
                    │              │              │           │
                    ▼              ▼              ▼           ▼
              ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
              │02.01(54)│   │02.02    │   │02.03    │   │03.01    │
              │ 0.25%   │   │(411)    │   │(204)    │   │(102)    │
              └─────────┘   │ 1.87%   │   │ 0.93%   │   │ 0.47%   │
                            └─────────┘   └─────────┘   └─────────┘

                    ▲                           ▲
                    │                           │
              SOMA = 669                  SOMA = 1538
              (54+411+204)               (102+26+187+...)
```

---

## Resumo das Regras

| # | Regra | Fórmula |
|---|-------|---------|
| 1 | Soma Hierárquica | `Qtd(Pai) = Σ Qtd(Filhos)` |
| 2 | Porcentagem Global | `%(X) = Qtd(X) / Total × 100` |
| 3 | Sem Dupla Contagem | Usar pai **OU** filhos, nunca ambos |
| 4 | Consistência Recursiva | Regras aplicam-se em todos os níveis |
| 5 | Raiz = 100% | Somatório de nível 1 = Total Geral |

---

## Contato e Manutenção

Para dúvidas ou correções nesta documentação, consulte o responsável pelo projeto.

---

*Documentação gerada para o projeto Porcentagem CESPE*
