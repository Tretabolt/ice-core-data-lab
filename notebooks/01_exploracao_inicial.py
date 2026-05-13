"""
Análise exploratória inicial dos dados de ice cores.
Gera visualizações comparativas de CO2, CH4, isótopos estáveis e temperatura
ao longo dos últimos 800.000 anos.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path
from scipy import signal

OUTPUT = Path("output")
OUTPUT.mkdir(exist_ok=True)

# ============================================================
# 1. LEITURA DOS DADOS
# ============================================================

def read_noaa_simple(filepath):
    """Lê arquivo NOAA de forma robusta, ignorando metadados."""
    with open(filepath) as f:
        lines = f.readlines()
    # Encontra primeira linha de dados (não começa com #, ---, ou texto)
    data_start = 0
    header = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('#') or stripped.startswith('---'):
            continue
        parts = stripped.split()
        try:
            [float(x) for x in parts]
            data_start = i
            break
        except ValueError:
            # Pode ser cabeçalho de texto
            if any(c.isalpha() for c in stripped) and not stripped[0].isdigit():
                header = stripped
                continue
    # Lê como whitespace-separated
    df = pd.read_csv(filepath, sep=r'\s+', skiprows=data_start, header=None,
                     on_bad_lines='skip', na_values=['-999', '-9999', '-9999.0'])
    return df, header


def parse_epica_isotopes(filepath):
    """Parse manual do EPICA Dome C (colunas misturadas)."""
    rows = []
    with open(filepath) as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue
            try:
                bag = int(parts[0])
            except ValueError:
                continue
            if len(parts) >= 5:
                rows.append([float(parts[1]), float(parts[2]), float(parts[3]), float(parts[4])])
            elif len(parts) == 4:
                rows.append([float(parts[1]), float(parts[2]), float(parts[3]), np.nan])
            elif len(parts) == 3:
                rows.append([float(parts[1]), float(parts[2]), np.nan, np.nan])

    df = pd.DataFrame(rows, columns=['depth_m', 'age_BP', 'dD_permil', 'temp_C'])
    df = df[df['age_BP'] > 0].copy()
    df['age_ka'] = df['age_BP'] / 1000
    return df


# --- EPICA Dome C isotopes ---
df_iso = parse_epica_isotopes("data/raw/noaa/epica_domec_isotopes.txt")
print(f"EPICA Isotopes: {len(df_iso)} registros, {df_iso['age_ka'].max():.0f} ka")

# --- CO2 composite ---
df_co2 = pd.read_csv("data/raw/noaa/antarctica_co2_composite.txt", sep='\t', comment='#')
df_co2.columns = [c.strip() for c in df_co2.columns]
df_co2 = df_co2[pd.to_numeric(df_co2.iloc[:,0], errors='coerce') > 0].copy()
df_co2['age_ka'] = pd.to_numeric(df_co2.iloc[:,0], errors='coerce') / 1000
df_co2['co2'] = pd.to_numeric(df_co2.iloc[:,1], errors='coerce')
print(f"CO2 Composite: {len(df_co2)} registros, {df_co2['age_ka'].max():.0f} ka")

# --- EPICA CH4 long record ---
df_ch4_raw, _ = read_noaa_simple("data/raw/noaa/epica_ch4_650k.txt")
if len(df_ch4_raw.columns) >= 2:
    df_ch4 = pd.DataFrame()
    df_ch4['age_BP'] = pd.to_numeric(df_ch4_raw.iloc[:,0], errors='coerce')
    df_ch4['ch4_ppb'] = pd.to_numeric(df_ch4_raw.iloc[:,1], errors='coerce')
    df_ch4 = df_ch4[df_ch4['age_BP'] > 0].dropna()
    df_ch4['age_ka'] = df_ch4['age_BP'] / 1000
    print(f"CH4: {len(df_ch4)} registros, {df_ch4['age_ka'].max():.0f} ka")
else:
    df_ch4 = pd.DataFrame(columns=['age_ka', 'ch4_ppb'])

# --- Vostok deuterium ---
df_vostok_d_raw, _ = read_noaa_simple("data/raw/noaa/vostok_deuterium.txt")
if len(df_vostok_d_raw.columns) >= 3:
    df_vostok_d = pd.DataFrame()
    df_vostok_d['age_BP'] = pd.to_numeric(df_vostok_d_raw.iloc[:,1], errors='coerce')
    df_vostok_d['dD_permil'] = pd.to_numeric(df_vostok_d_raw.iloc[:,2], errors='coerce')
    df_vostok_d = df_vostok_d[df_vostok_d['age_BP'] > 0].dropna()
    df_vostok_d['age_ka'] = df_vostok_d['age_BP'] / 1000
    print(f"Vostok dD: {len(df_vostok_d)} registros, {df_vostok_d['age_ka'].max():.0f} ka")

# --- Vostok dust ---
df_vostok_dust_raw, _ = read_noaa_simple("data/raw/noaa/vostok_dust.txt")
if len(df_vostok_dust_raw.columns) >= 2:
    df_vostok_dust = pd.DataFrame()
    df_vostok_dust['age_BP'] = pd.to_numeric(df_vostok_dust_raw.iloc[:,0], errors='coerce')
    df_vostok_dust['dust'] = pd.to_numeric(df_vostok_dust_raw.iloc[:,1], errors='coerce')
    df_vostok_dust = df_vostok_dust[df_vostok_dust['age_BP'] > 0].dropna()
    df_vostok_dust['age_ka'] = df_vostok_dust['age_BP'] / 1000
    print(f"Vostok Dust: {len(df_vostok_dust)} registros, {df_vostok_dust['age_ka'].max():.0f} ka")

# ============================================================
# 2. GRÁFICO COMPARATIVO - 800k anos
# ============================================================

fig = plt.figure(figsize=(16, 20))
gs = gridspec.GridSpec(5, 1, hspace=0.15)

# --- CO2 ---
ax1 = fig.add_subplot(gs[0])
mask = df_co2['age_ka'] > 0
ax1.plot(df_co2.loc[mask, 'age_ka'], df_co2.loc[mask, 'co2'], 'b-', linewidth=0.5, alpha=0.8)
ax1.fill_between(df_co2.loc[mask, 'age_ka'], df_co2.loc[mask, 'co2'], alpha=0.2, color='blue')
ax1.set_ylabel('CO₂ (ppm)', fontsize=12, fontweight='bold')
ax1.set_title('Composição Atmosférica e Clima da Antártica — 800.000 Anos\n(EPICA Dome C + Vostok)',
              fontsize=14, fontweight='bold', pad=15)
ax1.set_xlim(0, 820)
ax1.grid(True, alpha=0.3)
ax1.axhline(y=280, color='gray', linestyle='--', alpha=0.5, label='Pré-industrial (280 ppm)')
ax1.axhline(y=420, color='red', linestyle='--', alpha=0.7, label='Atual (~420 ppm)')
ax1.legend(loc='upper right', fontsize=9)

# --- CH4 ---
ax2 = fig.add_subplot(gs[1])
if len(df_ch4) > 0:
    mask = df_ch4['age_ka'] > 0
    ax2.plot(df_ch4.loc[mask, 'age_ka'], df_ch4.loc[mask, 'ch4_ppb'], 'g-', linewidth=0.5, alpha=0.8)
    ax2.fill_between(df_ch4.loc[mask, 'age_ka'], df_ch4.loc[mask, 'ch4_ppb'], alpha=0.2, color='green')
ax2.set_ylabel('CH₄ (ppb)', fontsize=12, fontweight='bold')
ax2.set_xlim(0, 820)
ax2.grid(True, alpha=0.3)
ax2.axhline(y=700, color='gray', linestyle='--', alpha=0.5, label='Pré-industrial (~700 ppb)')
ax2.axhline(y=1900, color='red', linestyle='--', alpha=0.7, label='Atual (~1900 ppb)')
ax2.legend(loc='upper right', fontsize=9)

# --- Deuterium (temperatura proxy) ---
ax3 = fig.add_subplot(gs[2])
mask = (df_iso['age_ka'] > 0) & df_iso['dD_permil'].notna()
ax3.plot(df_iso.loc[mask, 'age_ka'], df_iso.loc[mask, 'dD_permil'], 'r-', linewidth=0.3, alpha=0.7)
ax3.set_ylabel('δD (‰)', fontsize=12, fontweight='bold')
ax3.set_xlim(0, 820)
ax3.grid(True, alpha=0.3)
ax3.invert_yaxis()
ax3.annotate('Mais frio ↑', xy=(0.02, 0.95), xycoords='axes fraction', fontsize=9, color='blue')
ax3.annotate('Mais quente ↓', xy=(0.02, 0.05), xycoords='axes fraction', fontsize=9, color='red')

# --- Temperature anomaly ---
ax4 = fig.add_subplot(gs[3])
mask = (df_iso['age_ka'] > 0) & df_iso['temp_C'].notna()
ax4.plot(df_iso.loc[mask, 'age_ka'], df_iso.loc[mask, 'temp_C'], 'orange', linewidth=0.3, alpha=0.7)
ax4.fill_between(df_iso.loc[mask, 'age_ka'], df_iso.loc[mask, 'temp_C'],
                  where=df_iso.loc[mask, 'temp_C'] > 0, alpha=0.3, color='red', label='Mais quente')
ax4.fill_between(df_iso.loc[mask, 'age_ka'], df_iso.loc[mask, 'temp_C'],
                  where=df_iso.loc[mask, 'temp_C'] < 0, alpha=0.3, color='blue', label='Mais frio')
ax4.axhline(y=0, color='black', linewidth=0.5)
ax4.set_ylabel('ΔT (°C vs média 1ka)', fontsize=12, fontweight='bold')
ax4.set_xlim(0, 820)
ax4.grid(True, alpha=0.3)
ax4.legend(loc='upper right', fontsize=9)

# --- Dust (Vostok) ---
ax5 = fig.add_subplot(gs[4])
if 'dust' in df_vostok_dust.columns:
    mask = df_vostok_dust['age_ka'] > 0
    ax5.plot(df_vostok_dust.loc[mask, 'age_ka'], df_vostok_dust.loc[mask, 'dust'],
             'brown', linewidth=0.5, alpha=0.7)
    ax5.fill_between(df_vostok_dust.loc[mask, 'age_ka'], df_vostok_dust.loc[mask, 'dust'],
                      alpha=0.2, color='brown')
ax5.set_ylabel('Poeira (concentração)', fontsize=12, fontweight='bold')
ax5.set_xlabel('Idade (milhares de anos)', fontsize=12)
ax5.set_xlim(0, 820)
ax5.grid(True, alpha=0.3)

# Períodos interglaciais
for ax in [ax1, ax2, ax3, ax4, ax5]:
    for start, end, name in [(0, 12, 'Holoceno'), (115, 130, 'MIS 5e'),
                              (190, 210, 'MIS 7'), (310, 340, 'MIS 9'),
                              (390, 420, 'MIS 11')]:
        ax.axvspan(start, end, alpha=0.1, color='yellow')

plt.savefig(OUTPUT / "ice_cores_800kyr_overview.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"✅ Gráfico salvo: {OUTPUT / 'ice_cores_800kyr_overview.png'}")

# ============================================================
# 3. CORRELAÇÃO CO2 vs TEMPERATURA
# ============================================================

df_co2_clean = df_co2[['age_ka', 'co2']].dropna()
df_iso_clean = df_iso[['age_ka', 'dD_permil', 'temp_C']].dropna()

bins = np.arange(0, 810, 2)
df_co2_clean['bin'] = pd.cut(df_co2_clean['age_ka'], bins)
df_iso_clean['bin'] = pd.cut(df_iso_clean['age_ka'], bins)

co2_binned = df_co2_clean.groupby('bin', observed=True)['co2'].mean()
iso_binned = df_iso_clean.groupby('bin', observed=True)[['dD_permil', 'temp_C']].mean()

merged = pd.DataFrame({'co2': co2_binned, 'dD': iso_binned['dD_permil'], 'temp': iso_binned['temp_C']}).dropna()

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

colors = np.arange(len(merged))
axes[0].scatter(merged['co2'], merged['dD'], c=colors, cmap='viridis', s=5, alpha=0.6)
axes[0].set_xlabel('CO₂ (ppm)', fontsize=12)
axes[0].set_ylabel('δD (‰)', fontsize=12)
axes[0].set_title('CO₂ vs δD (proxy de temperatura)', fontsize=12)
corr = merged['co2'].corr(merged['dD'])
axes[0].text(0.05, 0.95, f'r = {corr:.3f}', transform=axes[0].transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
axes[0].grid(True, alpha=0.3)

axes[1].scatter(merged['co2'], merged['temp'], c=colors, cmap='viridis', s=5, alpha=0.6)
axes[1].set_xlabel('CO₂ (ppm)', fontsize=12)
axes[1].set_ylabel('ΔT (°C)', fontsize=12)
axes[1].set_title('CO₂ vs Anomalia de Temperatura', fontsize=12)
corr2 = merged['co2'].corr(merged['temp'])
axes[1].text(0.05, 0.95, f'r = {corr2:.3f}', transform=axes[1].transAxes, fontsize=12,
             verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT / "co2_temperature_correlation.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"✅ Gráfico salvo: {OUTPUT / 'co2_temperature_correlation.png'}")

# ============================================================
# 4. POWER SPECTRUM - ciclos orbitais
# ============================================================

df_iso_uniform = df_iso[['age_ka', 'dD_permil']].dropna().sort_values('age_ka')
age_reg = np.arange(0, 800, 0.5)
dD_reg = np.interp(age_reg, df_iso_uniform['age_ka'].values[::-1], df_iso_uniform['dD_permil'].values[::-1])

fs = 1 / 0.5
frequencies, power = signal.periodogram(dD_reg, fs=fs)
periods = 1 / frequencies[1:]
power = power[1:]

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(periods, power, 'b-', linewidth=1)
ax.set_xscale('log')
ax.set_xlabel('Período (milhares de anos)', fontsize=12)
ax.set_ylabel('Densidade espectral de potência', fontsize=12)
ax.set_title('Espectro de Potência do δD — EPICA Dome C\nCiclos orbitais de Milankovitch', fontsize=13)
ax.grid(True, alpha=0.3)

for period, name, color in [(41, 'Obliquidade (41 ka)', 'red'),
                              (100, 'Excentricidade (100 ka)', 'green'),
                              (23, 'Precessão (23 ka)', 'orange')]:
    ax.axvline(x=period, color=color, linestyle='--', alpha=0.7, linewidth=2)
    ax.annotate(name, xy=(period, ax.get_ylim()[1]*0.9), fontsize=10, color=color,
                ha='center', fontweight='bold')

ax.set_xlim(10, 500)
plt.tight_layout()
plt.savefig(OUTPUT / "power_spectrum_milankovitch.png", dpi=150, bbox_inches='tight',
            facecolor='white', edgecolor='none')
print(f"✅ Gráfico salvo: {OUTPUT / 'power_spectrum_milankovitch.png'}")

# ============================================================
# 5. ESTATÍSTICAS RESUMIDAS
# ============================================================
print("\n" + "="*70)
print("RESUMO ESTATÍSTICO DOS DADOS DE ICE CORES")
print("="*70)
print(f"\n📊 EPICA Dome C Isotopes: {len(df_iso)} registros, {df_iso['age_ka'].max():.0f} ka")
print(f"   δD: {df_iso['dD_permil'].min():.1f} a {df_iso['dD_permil'].max():.1f} ‰")
print(f"   ΔT: {df_iso['temp_C'].min():.1f} a {df_iso['temp_C'].max():.1f} °C")

print(f"\n📊 CO₂ Composite: {len(df_co2)} registros, {df_co2['age_ka'].max():.0f} ka")
print(f"   CO₂: {df_co2['co2'].min():.1f} a {df_co2['co2'].max():.1f} ppm")

if len(df_ch4) > 0:
    print(f"\n📊 CH₄ (EPICA): {len(df_ch4)} registros")
    print(f"   CH₄: {df_ch4['ch4_ppb'].min():.0f} a {df_ch4['ch4_ppb'].max():.0f} ppb")

print(f"\n📊 Correlação CO₂-δD: r = {corr:.3f}")
print(f"📊 Correlação CO₂-ΔT: r = {corr2:.3f}")

print(f"\n✅ Todos os gráficos salvos em: {OUTPUT}/")
