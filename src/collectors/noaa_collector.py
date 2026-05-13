"""
Coletor de dados de ice cores do NOAA NCEI Paleoclimatology.

O NOAA mantém o maior arquivo aberto de dados de paleoclima do mundo.
Este script busca e baixa datasets de ice cores por região, variável e período.

Uso:
    python noaa_collector.py --region antarctica --variable isotopes
    python noaa_collector.py --list-datasets
    python noaa_collector.py --download-all --output ../../data/raw/noaa/
"""

import requests
import pandas as pd
import os
import time
import argparse
from pathlib import Path
from tqdm import tqdm

BASE_URL = "https://www.ncei.noaa.gov/pub/data/paleo/icecore"
SEARCH_URL = "https://www.ncei.noaa.gov/paleo-search/data/search"

# Regiões e subdiretórios conhecidos no NOAA
REGIONS = {
    "antarctica": "antarctica",
    "greenland": "greenland",
    "arctic": "arctic",
    "andes": "southamerica",
    "alps": "europe",
    "himalaya": "asia",
    "africa": "africa",
}

# Variáveis comuns em ice cores
VARIABLES = [
    "temperature", "isotopes", "chemistry", "dust",
    "gas", "methane", "co2", "accumulation",
    "conductivity", "melt", "sea_level",
]


def search_datasets(region=None, variable=None, limit=100):
    """Busca datasets no NOAA NCEI via API de paleoclimatologia."""
    params = {"output": "json", "limit": limit}
    if region:
        params["location"] = region
    if variable:
        params["proxy"] = variable

    print(f"Buscando datasets: região={region}, variável={variable}")
    try:
        resp = requests.get(SEARCH_URL, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        datasets = data if isinstance(data, list) else data.get("results", [])
        print(f"Encontrados {len(datasets)} datasets")
        return datasets
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []


def list_noaa_icecore_files(region="antarctica"):
    """Lista arquivos disponíveis no diretório FTP/HTTP do NOAA para uma região."""
    region_path = REGIONS.get(region, region)
    url = f"{BASE_URL}/{region_path}/"
    print(f"Listando arquivos em: {url}")

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        # Parse simples do listing HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "lxml")
        links = soup.find_all("a")
        files = []
        for link in links:
            href = link.get("href", "")
            if href.endswith(".txt") or href.endswith(".csv") or href.endswith(".dat"):
                files.append(href)
        print(f"Encontrados {len(files)} arquivos de dados")
        return files
    except Exception as e:
        print(f"Erro ao listar: {e}")
        return []


def download_file(url, output_dir, filename=None):
    """Baixa um arquivo de dados do NOAA."""
    if filename is None:
        filename = url.split("/")[-1]
    output_path = Path(output_dir) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if output_path.exists():
        print(f"Já existe: {filename}")
        return output_path

    try:
        resp = requests.get(url, timeout=60, stream=True)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        with open(output_path, "wb") as f:
            for chunk in tqdm(resp.iter_content(8192), total=total//8192, desc=filename):
                f.write(chunk)
        print(f"Baixado: {filename} ({output_path.stat().st_size / 1024:.1f} KB)")
        return output_path
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")
        return None


def download_region(region="antarctica", output_dir="data/raw/noaa"):
    """Baixa todos os arquivos de dados de uma região."""
    output_path = Path(output_dir) / region
    output_path.mkdir(parents=True, exist_ok=True)

    files = list_noaa_icecore_files(region)
    downloaded = []
    for fname in files:
        url = f"{BASE_URL}/{REGIONS.get(region, region)}/{fname}"
        result = download_file(url, output_path, fname)
        if result:
            downloaded.append(result)
        time.sleep(0.5)  # rate limiting

    print(f"\nTotal baixado: {len(downloaded)}/{len(files)} arquivos")
    return downloaded


def parse_noaa_file(filepath):
    """
    Tenta ler um arquivo de dados do NOAA.
    Arquivos NOAA geralmente têm metadados em linhas com '#' seguidos de dados tabulares.
    """
    filepath = Path(filepath)
    metadata = {}
    header_line = None
    data_start = 0

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            # Metadados
            content = stripped.lstrip("#").strip()
            if ":" in content:
                key, _, val = content.partition(":")
                metadata[key.strip()] = val.strip()
        elif stripped == "" or stripped.startswith("-"):
            continue
        else:
            # Primeira linha de dados ou cabeçalho
            header_line = stripped
            data_start = i + 1
            break

    if header_line is None:
        return None, metadata

    # Parse das colunas
    separators = ["\t", ",", "  "]
    for sep in separators:
        cols = header_line.split(sep)
        if len(cols) > 1:
            break

    cols = [c.strip() for c in cols if c.strip()]

    # Parse dos dados
    rows = []
    for line in lines[data_start:]:
        stripped = line.strip()
        if stripped.startswith("#") or stripped == "":
            continue
        values = stripped.split(sep)
        values = [v.strip() for v in values]
        if len(values) == len(cols):
            rows.append(values)

    if not rows:
        return None, metadata

    df = pd.DataFrame(rows, columns=cols)
    # Tenta converter para numérico
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df, metadata


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coletor NOAA Ice Core Data")
    parser.add_argument("--region", default="antarctica", choices=list(REGIONS.keys()))
    parser.add_argument("--variable", choices=VARIABLES)
    parser.add_argument("--list-datasets", action="store_true")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--output", default="data/raw/noaa")
    args = parser.parse_args()

    if args.list_datasets:
        datasets = search_datasets(region=args.region, variable=args.variable)
        for d in datasets[:20]:
            print(f"  - {d.get('name', 'N/A')}: {d.get('url', 'N/A')}")
    elif args.download:
        download_region(args.region, args.output)
    else:
        print("Use --list-datasets ou --download")
        print("Exemplo: python noaa_collector.py --region antarctica --download")
