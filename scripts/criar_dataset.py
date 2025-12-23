#!/usr/bin/env python3
"""
Script para criar dataset consolidado a partir dos arquivos XLSX.

Este script:
1. Lê todos os arquivos .xlsx do diretório data/
2. Padroniza as colunas (alguns têm 4, outros têm 6 colunas)
3. Adiciona coluna 'Disciplina' para identificar a origem
4. Calcula o nível hierárquico automaticamente
5. Salva em CSV e Parquet

Regras baseadas em: docs/HIERARQUIA_DADOS.md
"""

import re
import sys
from pathlib import Path

import pandas as pd

from porcentagem_cespe.constants import DISCIPLINAS

# Configurações
DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "datasets"

# Colunas padrão do dataset final
COLUNAS_PADRAO = [
    "Disciplina",
    "Hierarquia",
    "Nivel",
    "Indice",
    "Quantidade",
    "Quantidade_Caderno",
]


def calcular_nivel(hierarquia: str) -> int:
    """
    Calcula o nível hierárquico baseado no código.

    Retorna:
        0 = Raiz (hierarquia vazia)
        1 = Nível principal (01, 02, etc.)
        2 = Subnível (01.01, 02.03, etc.)
        ...
    """
    if pd.isna(hierarquia) or str(hierarquia).strip() == "":
        return 0
    return str(hierarquia).count(".") + 1


def processar_arquivo(filepath: Path, disciplina: str) -> pd.DataFrame:
    """
    Processa um arquivo XLSX e retorna DataFrame padronizado.
    """
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
    except Exception as e:
        print(f"   ❌ Erro ao ler {filepath.name}: {e}")
        return pd.DataFrame()

    # Validação de colunas obrigatórias
    required_cols = {"Hierarquia", "Índice", "Quantidade encontrada"}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        print(f"   ❌ Colunas ausentes em {filepath.name}: {missing}")
        return pd.DataFrame()

    # Cria DataFrame padronizado
    df_padrao = pd.DataFrame()

    # Adiciona disciplina (repetida para todas as linhas)
    df_padrao["Disciplina"] = [disciplina] * len(df)

    # Hierarquia (converte para string e limpa)
    df_padrao["Hierarquia"] = df["Hierarquia"].apply(
        lambda x: "" if pd.isna(x) else str(x).strip()
    )

    # Calcula nível
    df_padrao["Nivel"] = df_padrao["Hierarquia"].apply(calcular_nivel)

    # Índice (nome do tópico)
    df_padrao["Indice"] = df["Índice"].fillna("")

    # Quantidade encontrada
    df_padrao["Quantidade"] = df["Quantidade encontrada"].fillna(0).astype(int)

    # Colunas opcionais (existem apenas em alguns arquivos)
    if "Quantidade no caderno" in df.columns:
        df_padrao["Quantidade_Caderno"] = (
            df["Quantidade no caderno"].fillna(0).astype(int)
        )
    else:
        df_padrao["Quantidade_Caderno"] = df_padrao["Quantidade"]

    return df_padrao


def criar_dataset():
    """
    Cria o dataset consolidado a partir de todos os arquivos XLSX.
    """
    print("=" * 60)
    print("CRIANDO DATASET CONSOLIDADO")
    print("=" * 60)

    try:
        # Cria diretório de saída se não existir
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"❌ Erro ao criar diretório de saída: {e}")
        sys.exit(1)

    # Lista para armazenar todos os DataFrames
    dfs = []

    # Processa cada arquivo
    for arquivo, disciplina in DISCIPLINAS.items():
        filepath = DATA_DIR / arquivo
        if filepath.exists():
            print(f"\n📄 Processando: {arquivo}")
            df = processar_arquivo(filepath, disciplina)
            if not df.empty:
                print(f"   → {len(df)} registros carregados")
                dfs.append(df)
            else:
                print("   ⚠️  Arquivo ignorado (vazio ou inválido)")
        else:
            print(f"\n⚠️  Arquivo não encontrado: {arquivo}")

    if not dfs:
        print("\n❌ Nenhum dado foi carregado. Verifique os arquivos de entrada.")
        sys.exit(1)

    # Concatena todos os DataFrames
    df_final = pd.concat(dfs, ignore_index=True)

    # Ordena por Disciplina e Hierarquia
    df_final = df_final.sort_values(["Disciplina", "Hierarquia"]).reset_index(drop=True)

    print("\n" + "=" * 60)
    print("RESUMO DO DATASET")
    print("=" * 60)
    print(f"\n📊 Total de registros: {len(df_final)}")
    print(f"📚 Disciplinas: {df_final['Disciplina'].nunique()}")

    # Estatísticas por disciplina
    print("\n📈 Registros por disciplina:")
    for disciplina, count in df_final.groupby("Disciplina").size().items():
        print(f"   • {disciplina}: {count}")

    # Estatísticas por nível
    print("\n📈 Registros por nível hierárquico:")
    for nivel, count in df_final.groupby("Nivel").size().items():
        print(f"   • Nível {nivel}: {count}")

    try:
        # Salva em CSV
        csv_path = OUTPUT_DIR / "dataset_cespe.csv"
        df_final.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"\n✅ CSV salvo: {csv_path}")

        # Salva em Parquet (mais eficiente para análises)
        parquet_path = OUTPUT_DIR / "dataset_cespe.parquet"
        try:
            import pyarrow  # noqa: F401
            df_final.to_parquet(parquet_path, index=False, engine="pyarrow")
            print(f"✅ Parquet salvo: {parquet_path}")
        except ImportError:
            print("⚠️  pyarrow não instalado. Pulando geração de Parquet.")
        except Exception as e:
            print(f"❌ Erro ao salvar Parquet: {e}")

        # Também salva um CSV por disciplina para facilitar análises individuais
        disciplinas_dir = OUTPUT_DIR / "por_disciplina"
        disciplinas_dir.mkdir(exist_ok=True)

        for disciplina in df_final["Disciplina"].unique():
            if pd.isna(disciplina):
                continue
            df_disc = df_final[df_final["Disciplina"] == disciplina]

            # Sanitização segura do nome do arquivo
            nome_arquivo = re.sub(r"[^A-Za-z0-9._-]", "_", str(disciplina).strip())
            nome_arquivo = re.sub(r"_+", "_", nome_arquivo).strip("_")

            csv_disc_path = disciplinas_dir / f"{nome_arquivo}.csv"
            df_disc.to_csv(csv_disc_path, index=False, encoding="utf-8")

        print(f"✅ CSVs individuais salvos em: {disciplinas_dir}")

    except Exception as e:
        print(f"\n❌ Erro ao salvar arquivos: {e}")
        sys.exit(1)

    return df_final


if __name__ == "__main__":
    try:
        df = criar_dataset()
        print("\n" + "=" * 60)
        print("AMOSTRA DO DATASET (primeiras 10 linhas)")
        print("=" * 60)
        print(df.head(10).to_string(index=False))
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)
