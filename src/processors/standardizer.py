"""
Processador padronizador de dados de ice cores.

Converte dados de diferentes formatos (NOAA, PANGAEA, ICE-D) em um
schema unificado para análise comparativa.

Schema padronizado:
    - core_id: identificador do ice core
    - depth_m: profundidade em metros
    - age_years: idade em anos (antes do presente, BP)
    - age_ka: idade em milhares de anos
    - region: região geográfica
    - variable: nome da variável
    - value: valor numérico
    - unit: unidade de medida
    - source: fonte dos dados
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime


# Mapeamento de nomes de colunas comuns para o schema padronizado
COLUMN_MAPPING = {
    # Profundidade
    "depth": "depth_m", "Depth": "depth_m", "DEPTH": "depth_m",
    "depth_m": "depth_m", "depth (m)": "depth_m",
    "Top": "depth_m", "bottom": "depth_m",
    "DepthTop": "depth_m", "DepthBottom": "depth_m_end",
    "depth_top_m": "depth_m", "depth_bottom_m": "depth_m_end",

    # Idade
    "age": "age_years", "Age": "age_years", "AGE": "age_years",
    "age_years": "age_years", "age (yr BP)": "age_years",
    "Age (yr BP)": "age_years", "age [ka BP]": "age_ka",
    "Age_ice (yr BP)": "age_years", "Age_gas (yr BP)": "age_years_gas",
    "yr_BP": "age_years", "Time": "age_years",

    # Isótopos estáveis
    "d18O": "d18O", "delta18O": "d18O", "δ18O": "d18O",
    "d18O (‰)": "d18O", "d18O [‰ SMOW]": "d18O",
    "d18O_h2o": "d18O", "d18O (permil)": "d18O",
    "dD": "dD", "deltaD": "dD", "δD": "dD",
    "dD (‰)": "dD", "dD [‰ SMOW]": "dD",

    # Gases
    "CO2": "co2_ppm", "CO2 (ppmv)": "co2_ppm", "co2": "co2_ppm",
    "CH4": "ch4_ppb", "CH4 (ppbv)": "ch4_ppb", "ch4": "ch4_ppb",
    "N2O": "n2o_ppb", "N2O (ppbv)": "n2o_ppb",

    # Química iônica
    "Na": "na_ppb", "Na+": "na_ppb", "Na (ppb)": "na_ppb",
    "Ca": "ca_ppb", "Ca2+": "ca_ppb", "Ca (ppb)": "ca_ppb",
    "Mg": "mg_ppb", "Mg2+": "mg_ppb",
    "K": "k_ppb", "K+": "k_ppb",
    "Cl": "cl_ppb", "Cl-": "cl_ppb", "Cl (ppb)": "cl_ppb",
    "SO4": "so4_ppb", "SO42-": "so4_ppb", "SO4 (ppb)": "so4_ppb",
    "NO3": "no3_ppb", "NO3-": "no3_ppb", "NO3 (ppb)": "no3_ppb",

    # Isótopos cosmogênicos
    "10Be": "be10_atoms_g", "10Be (at/g)": "be10_atoms_g",
    "Be-10": "be10_atoms_g", "10Be concentration": "be10_atoms_g",
    "36Cl": "cl36_atoms_g", "36Cl (at/g)": "cl36_atoms_g",
    "26Al": "al26_atoms_g", "26Al (at/g)": "al26_atoms_g",
    "60Fe": "fe60_atoms_g", "Fe-60": "fe60_atoms_g",

    # Poeira
    "dust": "dust_ppm", "Dust": "dust_ppm", "Dust (ppm)": "dust_ppm",
    "insoluble particles": "dust_ppm",

    # Propriedades físicas
    "cond": "conductivity_us", "Conductivity": "conductivity_us",
    "acidity": "acidity_meq_kg", "H+": "acidity_meq_kg",
    "deposition": "accumulation_cm_yr",
}


def standardize_columns(df, source="unknown"):
    """Renomeia colunas para o schema padronizado."""
    rename_map = {}
    for col in df.columns:
        col_clean = col.strip()
        if col_clean in COLUMN_MAPPING:
            rename_map[col] = COLUMN_MAPPING[col_clean]

    df_std = df.rename(columns=rename_map)
    df_std["_source"] = source
    return df_std


def infer_age_from_depth(df, core_info=None):
    """
    Se não houver coluna de idade, tenta estimar a partir da profundidade
    usando uma taxa de acumulação típica.
    """
    if "age_years" in df.columns and df["age_years"].notna().sum() > 10:
        return df

    if "depth_m" in df.columns and core_info:
        accumulation_rate = core_info.get("accumulation_cm_yr", 10)  # cm/ano
        accumulation_m_yr = accumulation_rate / 100
        df["age_years"] = df["depth_m"] / accumulation_m_yr
        print(f"  Idade estimada a partir da profundidade (taxa: {accumulation_rate} cm/ano)")

    return df


def add_derived_columns(df):
    """Adiciona colunas derivadas úteis para análise."""
    if "age_years" in df.columns:
        df["age_ka"] = df["age_years"] / 1000
        df["age_Ma"] = df["age_years"] / 1e6

    if "d18O" in df.columns and "dD" in df.columns:
        df["d_excess"] = df["dD"] - 8 * df["d18O"]

    return df


def standardize_file(filepath, source="auto", core_id=None):
    """
    Lê e padroniza um arquivo de dados de ice core.
    Detecta automaticamente o formato (NOAA, PANGAEA, CSV genérico).
    """
    filepath = Path(filepath)

    # Detecta formato
    if source == "auto":
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            first_lines = [f.readline() for _ in range(20)]
        content = "\n".join(first_lines)
        if "PANGAEA" in content or "/*" in content:
            source = "pangaea"
        elif content.count("#") > 5:
            source = "noaa"
        else:
            source = "csv"

    # Lê dados
    if source == "pangaea":
        from src.collectors.pangaea_collector import parse_pangaea_file
        df, metadata = parse_pangaea_file(filepath)
    elif source == "noaa":
        from src.collectors.noaa_collector import parse_noaa_file
        df, metadata = parse_noaa_file(filepath)
    else:
        # CSV genérico
        for sep in ["\t", ",", ";", " "]:
            try:
                df = pd.read_csv(filepath, sep=sep, comment="#", skip_blank_lines=True)
                if len(df.columns) > 2:
                    break
            except Exception:
                continue
        metadata = {}

    if df is None:
        print(f"  Não foi possível ler: {filepath.name}")
        return None

    # Padroniza
    df = standardize_columns(df, source)
    df = infer_age_from_depth(df, metadata)
    df = add_derived_columns(df)

    if core_id:
        df["core_id"] = core_id
    elif "core_id" not in df.columns:
        df["core_id"] = filepath.stem

    print(f"  Padronizado: {filepath.name} → {len(df)} linhas, {len(df.columns)} colunas")
    return df


def process_directory(input_dir, output_file=None):
    """Processa todos os arquivos de um diretório e gera dataset unificado."""
    input_dir = Path(input_dir)
    all_dfs = []

    files = list(input_dir.glob("**/*.txt")) + list(input_dir.glob("**/*.csv"))
    print(f"Processando {len(files)} arquivos em {input_dir}")

    for filepath in sorted(files):
        try:
            df = standardize_file(filepath)
            if df is not None:
                all_dfs.append(df)
        except Exception as e:
            print(f"  Erro em {filepath.name}: {e}")

    if not all_dfs:
        print("Nenhum arquivo processado com sucesso.")
        return None

    # Consolida
    combined = pd.concat(all_dfs, ignore_index=True, sort=True)
    print(f"\nDataset consolidado: {len(combined)} linhas, {len(combined.columns)} colunas")

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_parquet(output_path, index=False)
        print(f"Salvo em: {output_path}")

    return combined


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Padronizador de dados de ice cores")
    parser.add_argument("--input", required=True, help="Diretório ou arquivo de entrada")
    parser.add_argument("--output", default="data/processed/ice_cores_standardized.parquet")
    parser.add_argument("--source", default="auto", choices=["auto", "noaa", "pangaea", "csv"])
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_dir():
        process_directory(input_path, args.output)
    elif input_path.is_file():
        df = standardize_file(input_path, args.source)
        if df is not None:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(output_path, index=False)
            print(f"Salvo em: {output_path}")
