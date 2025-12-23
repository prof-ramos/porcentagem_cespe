#!/usr/bin/env python3
"""
Script de validação: compara o dataset consolidado com os arquivos XLSX originais.
"""

import sys
from pathlib import Path

import pandas as pd

from porcentagem_cespe.constants import DISCIPLINAS

DATA_DIR = Path(__file__).parent.parent / "data"
DATASET_PATH = Path(__file__).parent.parent / "datasets" / "dataset_cespe.csv"

# Constantes de Colunas
COL_DISCIPLINA = "Disciplina"
COL_QUANTIDADE = "Quantidade"
COL_QUANTIDADE_ENC = "Quantidade encontrada"
COL_NIVEL = "Nivel"


def validar() -> bool:
    """
    Valida o dataset consolidado comparando com os arquivos originais.

    Returns:
        bool: True se a validação for bem-sucedida, False caso contrário.
    """
    # Carregar dataset criado
    try:
        df_dataset = pd.read_csv(DATASET_PATH)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as e:
        print(f"❌ Erro ao carregar dataset consolidado: {e}")
        return False

    print("=" * 70)
    print("VALIDAÇÃO: DATASET vs ARQUIVOS XLSX ORIGINAIS")
    print("=" * 70)

    erros = []

    for arquivo, disciplina in DISCIPLINAS.items():
        filepath = DATA_DIR / arquivo
        if not filepath.exists():
            continue

        # Carregar original
        try:
            df_orig = pd.read_excel(filepath, engine="openpyxl")
        except Exception as e:
            msg = f"{arquivo}: Erro ao ler arquivo Excel ({e})"
            erros.append(msg)
            print(f"   ❌ {msg}")
            continue

        if df_orig.empty:
            msg = f"{arquivo}: Arquivo vazio"
            erros.append(msg)
            print(f"   ❌ {msg}")
            continue

        # Filtrar dataset pela disciplina
        if COL_DISCIPLINA not in df_dataset.columns:
            print(f"❌ Coluna '{COL_DISCIPLINA}' não encontrada no dataset.")
            return False

        df_disc = df_dataset[df_dataset[COL_DISCIPLINA] == disciplina]

        print(f"\n📄 {arquivo} → {disciplina}")

        # Verificar contagem de linhas
        orig_rows = len(df_orig)
        dataset_rows = len(df_disc)

        if orig_rows != dataset_rows:
            erros.append(
                f"{arquivo}: Linhas diferem (orig={orig_rows}, dataset={dataset_rows})"
            )
            print(f"   ❌ Linhas: {orig_rows} vs {dataset_rows}")
        else:
            print(f"   ✅ Linhas: {orig_rows} == {dataset_rows}")

        # Verificar soma total de Quantidade
        if COL_QUANTIDADE_ENC not in df_orig.columns:
            msg = f"{arquivo}: Coluna '{COL_QUANTIDADE_ENC}' não encontrada"
            erros.append(msg)
            print(f"   ❌ {msg}")
            continue

        orig_total = df_orig[COL_QUANTIDADE_ENC].sum()
        dataset_total = df_disc[COL_QUANTIDADE].sum()

        if orig_total != dataset_total:
            erros.append(
                f"{arquivo}: Soma Quantidade diferem (orig={orig_total}, dataset={dataset_total})"
            )
            print(f"   ❌ Soma Quantidade: {orig_total} vs {dataset_total}")
        else:
            print(f"   ✅ Soma Quantidade: {orig_total} == {dataset_total}")

        # Verificar soma dos tópicos raiz (nível 0)
        # Alguns arquivos podem ter múltiplos tópicos raiz (ex: Port_RedOficial)
        mask_raiz_orig = df_orig["Hierarquia"].isna() | (
            df_orig["Hierarquia"].astype(str).str.strip() == ""
        )
        orig_raiz_sum = df_orig[mask_raiz_orig][COL_QUANTIDADE_ENC].sum()

        # Agregar nível 0 no dataset
        dataset_nivel_0 = df_disc[df_disc[COL_NIVEL] == 0]

        if dataset_nivel_0.empty:
            # Se não houver nível 0, pode ser um erro ou estrutura diferente
            pass
        else:
            dataset_raiz_sum = dataset_nivel_0[COL_QUANTIDADE].sum()

            if orig_raiz_sum != dataset_raiz_sum:
                erros.append(
                    f"{arquivo}: Total disciplina difere "
                    f"(orig={orig_raiz_sum}, dataset={dataset_raiz_sum})"
                )
                print(f"   ❌ Total Disciplina: {orig_raiz_sum} vs {dataset_raiz_sum}")
            else:
                print(f"   ✅ Total Disciplina: {orig_raiz_sum} == {dataset_raiz_sum}")

    print("\n" + "=" * 70)
    if erros:
        print(f"❌ FALHA: {len(erros)} erro(s) encontrado(s)")
        for e in erros:
            print(f"   • {e}")
    else:
        print("✅ SUCESSO: Todos os valores conferem com os originais!")
    print("=" * 70)

    return len(erros) == 0


if __name__ == "__main__":
    sucesso = validar()
    sys.exit(0 if sucesso else 1)
