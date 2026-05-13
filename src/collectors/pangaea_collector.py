"""
Coletor de dados de ice cores do PANGAEA.

PANGAEA é o principal repositório europeu de dados de ciências da Terra.
Muitos grupos de pesquisa (incluindo o instituto de Kiel que fez o estudo
do Fe-60 em supernovas) depositam dados aqui.

Uso:
    python pangaea_collector.py --search "ice core Antarctica"
    python pangaea_collector.py --search "iron-60 supernova"
    python pangaea_collector.py --download-dataset DOI
"""

import requests
import pandas as pd
import json
import time
from pathlib import Path
from tqdm import tqdm

PANGAEA_API = "https://www.pangaea.de/advanced/search.php"
PANGAEA_DATASET_API = "https://doi.pangaea.de"


def search_pangaea(query, count=50, env="Antarctica"):
    """
    Busca datasets no PANGAEA via API.
    
    Args:
        query: termo de busca (ex: "ice core", "iron-60", "cosmogenic nuclides")
        count: número máximo de resultados
        env: filtro ambiental
    """
    params = {
        "q": query,
        "count": count,
        "output": "json",
    }
    if env:
        params["env"] = env

    print(f"Buscando no PANGAEA: '{query}'")
    try:
        resp = requests.get(PANGAEA_API, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        datasets = data.get("results", [])
        print(f"Encontrados {len(datasets)} datasets")
        return datasets
    except Exception as e:
        print(f"Erro na busca: {e}")
        return []


def get_dataset_metadata(doi):
    """Recupera metadados de um dataset pelo DOI."""
    url = f"{PANGAEA_DATASET_API}/{doi}"
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Erro ao buscar metadados para {doi}: {e}")
        return None


def download_dataset(doi, output_dir="data/raw/pangaea"):
    """
    Baixa um dataset do PANGAEA pelo DOI.
    Tenta primeiro o formato tab-delimited (TSV), depois CSV.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # URLs possíveis para download
    base_doi = doi.replace("https://doi.pangaea.de/", "").replace("10.1594/PANGAEA.", "")
    urls = [
        f"https://doi.pangaea.de/10.1594/PANGAEA.{base_doi}?format=textfile",
        f"https://doi.pangaea.de/10.1594/PANGAEA.{base_doi}?format=csv",
    ]

    for url in urls:
        try:
            resp = requests.get(url, timeout=60, stream=True)
            resp.raise_for_status()
            ext = ".txt" if "textfile" in url else ".csv"
            filename = f"pangaea_{base_doi}{ext}"
            filepath = output_path / filename
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(8192):
                    f.write(chunk)
            print(f"Baixado: {filename} ({filepath.stat().st_size / 1024:.1f} KB)")
            return filepath
        except Exception:
            continue

    print(f"Não foi possível baixar dataset {doi}")
    return None


def parse_pangaea_file(filepath):
    """
    Lê um arquivo de dados do PANGAEA.
    Formato típico: metadados em linhas com '*/' ou '/', dados tab-delimited.
    """
    filepath = Path(filepath)
    metadata = {}
    header_cols = None
    data_rows = []
    in_data = False

    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            stripped = line.strip()

            if stripped.startswith("*/"):
                # Fim dos metadados, próxima linha é cabeçalho
                in_data = False
                continue
            elif stripped.startswith("/*") or stripped.startswith("//"):
                # Metadados
                content = stripped.lstrip("/*").lstrip("//").strip()
                if "\t" in content:
                    parts = content.split("\t", 1)
                    if len(parts) == 2:
                        metadata[parts[0].strip()] = parts[1].strip()
                continue
            elif not in_data and header_cols is None:
                # Linha de cabeçalho
                header_cols = [c.strip() for c in stripped.split("\t") if c.strip()]
                in_data = True
                continue
            elif in_data and stripped:
                # Dados
                values = [v.strip() for v in stripped.split("\t")]
                if len(values) == len(header_cols):
                    data_rows.append(values)

    if not header_cols or not data_rows:
        return None, metadata

    df = pd.DataFrame(data_rows, columns=header_cols)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df, metadata


# Buscas pré-definidas para ice cores
SEARCH_QUERIES = {
    "ice_core_general": "ice core",
    "ice_core_antarctica": "ice core Antarctica",
    "ice_core_greenland": "ice core Greenland",
    "cosmogenic_isotopes": "ice core cosmogenic nuclides",
    "iron_60": "iron-60 ice core supernova",
    "beryllium_10": "beryllium-10 ice core",
    "chlorine_36": "chlorine-36 ice core",
    "stable_isotopes": "ice core stable isotopes oxygen",
    "chemistry": "ice core chemistry ions",
    "dust": "ice core dust insoluble particles",
    "gas_co2": "ice core carbon dioxide",
    "gas_ch4": "ice core methane",
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Coletor PANGAEA Ice Core Data")
    parser.add_argument("--search", type=str, help="Termo de busca")
    parser.add_argument("--search-all", action="store_true", help="Busca predefinida abrangente")
    parser.add_argument("--download-doi", type=str, help="DOI do dataset para baixar")
    parser.add_argument("--output", default="data/raw/pangaea")
    args = parser.parse_args()

    if args.search:
        results = search_pangaea(args.search)
        for r in results[:20]:
            print(f"  - {r.get('title', 'N/A')}")
            print(f"    DOI: {r.get('DOI', 'N/A')}")
            print()
    elif args.search_all:
        all_results = {}
        for name, query in SEARCH_QUERIES.items():
            results = search_pangaea(query, count=20)
            all_results[name] = results
            time.sleep(1)  # rate limiting
            print(f"\n{'='*60}")
            print(f"  {name}: {len(results)} datasets")
            print(f"{'='*60}")

        # Salva índice
        output_path = Path(args.output)
        output_path.mkdir(parents=True, exist_ok=True)
        with open(output_path / "pangaea_index.json", "w") as f:
            json.dump(all_results, f, indent=2, default=str)
        print(f"\nÍndice salvo em {output_path / 'pangaea_index.json'}")
    elif args.download_doi:
        download_dataset(args.download_doi, args.output)
    else:
        print("Use --search, --search-all ou --download-doi")
        print("Exemplo: python pangaea_collector.py --search 'ice core Antarctica iron'")
