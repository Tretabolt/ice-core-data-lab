"""
Módulo de análise exploratória de dados de ice cores.

Fornece funções para:
- Perfilamento estatístico dos dados
- Visualização de séries temporais
- Análise de correlações entre variáveis
- Detecção de eventos (supernovas, erupções vulcânicas, excursões geomagnéticas)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def profile_dataset(df):
    """Gera um perfil estatístico do dataset."""
    print("=" * 60)
    print("PERFIL DO DATASET")
    print("=" * 60)
    print(f"Linhas: {len(df):,}")
    print(f"Colunas: {len(df.columns)}")
    print(f"\nColunas numéricas: {df.select_dtypes(include=[np.number]).columns.tolist()}")
    print(f"Colunas categóricas: {df.select_dtypes(include=['object']).columns.tolist()}")

    # Estatísticas descritivas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    stats = df[numeric_cols].describe()
    print(f"\nEstatísticas descritivas:")
    print(stats.to_string())

    # Valores ausentes
    missing = df[numeric_cols].isnull().sum()
    missing_pct = (missing / len(df) * 100).round(1)
    missing_df = pd.DataFrame({"missing": missing, "pct": missing_pct})
    missing_df = missing_df[missing_df["missing"] > 0].sort_values("pct", ascending=False)
    if len(missing_df) > 0:
        print(f"\nValores ausentes:")
        print(missing_df.to_string())
    else:
        print(f"\nSem valores ausentes nas colunas numéricas.")

    # Cobertura temporal
    if "age_years" in df.columns:
        age = df["age_years"].dropna()
        print(f"\nCobertura temporal:")
        print(f"  Idade mínima: {age.min():,.0f} anos")
        print(f"  Idade máxima: {age.max():,.0f} anos")
        print(f"  Idade mediana: {age.median():,.0f} anos")

    if "age_ka" in df.columns:
        age_ka = df["age_ka"].dropna()
        print(f"  Em milhares de anos: {age_ka.min():.1f} - {age_ka.max():.1f} ka")

    return stats


def plot_timeseries(df, variables=None, age_col="age_ka", figsize=(14, 8)):
    """Plota séries temporais de variáveis selecionadas."""
    if variables is None:
        # Auto-detecta variáveis com dados suficientes
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        variables = [c for c in numeric_cols
                     if c not in [age_col, "age_years", "age_Ma", "depth_m", "depth_m_end"]
                     and df[c].notna().sum() > 50]

    n_vars = len(variables)
    fig, axes = plt.subplots(n_vars, 1, figsize=figsize, sharex=True)
    if n_vars == 1:
        axes = [axes]

    for ax, var in zip(axes, variables):
        mask = df[age_col].notna() & df[var].notna()
        if mask.sum() < 10:
            continue
        ax.plot(df.loc[mask, age_col], df.loc[mask, var], ".", markersize=1, alpha=0.5)
        ax.set_ylabel(var)
        ax.grid(True, alpha=0.3)

    axes[-1].set_xlabel(f"Idade ({age_col})")
    axes[0].set_title("Séries temporais de ice cores")
    plt.tight_layout()
    return fig


def plot_correlation_matrix(df, variables=None, figsize=(10, 8)):
    """Matriz de correlação entre variáveis."""
    if variables is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        variables = [c for c in numeric_cols
                     if c not in ["age_years", "age_ka", "age_Ma", "depth_m", "depth_m_end"]
                     and df[c].notna().sum() > 50]

    corr = df[variables].corr()

    fig, ax = plt.subplots(figsize=figsize)
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r",
                center=0, square=True, ax=ax)
    ax.set_title("Matriz de correlação")
    plt.tight_layout()
    return fig


def detect_anomalies(series, window=100, threshold=3.0):
    """
    Detecta anomalias em uma série temporal usando z-score móvel.
    Útil para identificar eventos como erupções vulcânicas ou picos de isótopos cosmogênicos.
    """
    rolling_mean = series.rolling(window, center=True).mean()
    rolling_std = series.rolling(window, center=True).std()
    z_score = (series - rolling_mean) / rolling_std
    anomalies = series[np.abs(z_score) > threshold]
    return anomalies, z_score


def find_supernova_signals(df, be10_col="be10_atoms_g", age_col="age_years"):
    """
    Busca sinais de supernovas em dados de ¹⁰Be.
    Supernovas causam picos detectáveis em isótopos cosmogênicos.
    """
    if be10_col not in df.columns:
        print(f"Coluna {be10_col} não encontrada")
        return None

    mask = df[age_col].notna() & df[be10_col].notna()
    series = df.loc[mask, be10_col]
    ages = df.loc[mask, age_col]

    anomalies, z_scores = detect_anomalies(series)

    if len(anomalies) > 0:
        print(f"Encontrados {len(anomalies)} eventos anômalos em ¹⁰Be:")
        for idx in anomalies.index:
            age = ages.loc[idx]
            value = series.loc[idx]
            z = z_scores.loc[idx]
            print(f"  Idade: {age:,.0f} anos | ¹⁰Be: {value:.2e} atoms/g | z-score: {z:.1f}")

    return anomalies


def compare_cores(df, core_id_col="core_id", variable="d18O", age_col="age_ka"):
    """Compara uma variável entre diferentes ice cores."""
    if core_id_col not in df.columns:
        print("Coluna core_id não encontrada")
        return

    cores = df[core_id_col].unique()
    fig, ax = plt.subplots(figsize=(14, 6))

    for core in cores:
        subset = df[df[core_id_col] == core]
        mask = subset[age_col].notna() & subset[variable].notna()
        if mask.sum() < 10:
            continue
        ax.plot(subset.loc[mask, age_col], subset.loc[mask, variable],
                ".", markersize=1, alpha=0.5, label=core)

    ax.set_xlabel(f"Idade ({age_col})")
    ax.set_ylabel(variable)
    ax.set_title(f"Comparação de {variable} entre ice cores")
    ax.legend(markerscale=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    return fig


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Análise exploratória de ice cores")
    parser.add_argument("--input", required=True, help="Arquivo parquet ou CSV de entrada")
    parser.add_argument("--profile", action="store_true", help="Perfil do dataset")
    parser.add_argument("--plot", action="store_true", help="Séries temporais")
    parser.add_argument("--corr", action="store_true", help="Matriz de correlação")
    parser.add_argument("--anomalies", action="store_true", help="Detecção de anomalias")
    parser.add_argument("--output", default="output/")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.suffix == ".parquet":
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.profile:
        profile_dataset(df)

    if args.plot:
        fig = plot_timeseries(df)
        fig.savefig(output_dir / "timeseries.png", dpi=150, bbox_inches="tight")
        print(f"Gráfico salvo em {output_dir / 'timeseries.png'}")

    if args.corr:
        fig = plot_correlation_matrix(df)
        fig.savefig(output_dir / "correlation.png", dpi=150, bbox_inches="tight")
        print(f"Gráfico salvo em {output_dir / 'correlation.png'}")

    if args.anomalies:
        find_supernova_signals(df)
