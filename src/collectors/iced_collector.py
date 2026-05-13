"""
Coletor de dados do ICE-D: Ice Cores.

ICE-D é um banco de dados especializado em química de gelo e isótopos
cosmogênicos (¹⁰Be, ²⁶Al, ³⁶Cl, ⁴¹Ca) em múltiplos projetos de ice cores.

Site: http://www.ice-d.org

Uso:
    python iced_collector.py --list-projects
    python iced_collector.py --project EPICA --download
"""

import requests
import pandas as pd
from pathlib import Path

ICED_BASE = "http://www.ice-d.org"


def get_projects():
    """Lista projetos disponíveis no ICE-D."""
    # ICE-D não tem API REST formal, acessamos as páginas conhecidas
    known_projects = {
        "EPICA": {
            "full_name": "European Project for Ice Coring in Antarctica",
            "location": "Antarctica (Dome C, Dronning Maud Land)",
            "sites": ["EDC", "EDML"],
            "depth_m": 3270,
            "age_years": 800000,
        },
        "GISP2": {
            "full_name": "Greenland Ice Sheet Project 2",
            "location": "Greenland (Summit)",
            "sites": ["GISP2"],
            "depth_m": 3053,
            "age_years": 110000,
        },
        "GRIP": {
            "full_name": "Greenland Ice Core Project",
            "location": "Greenland (Summit)",
            "sites": ["GRIP"],
            "depth_m": 3029,
            "age_years": 123000,
        },
        "NGRIP": {
            "full_name": "North Greenland Ice Core Project",
            "location": "Greenland (North)",
            "sites": ["NGRIP"],
            "depth_m": 3085,
            "age_years": 123000,
        },
        "NEEM": {
            "full_name": "North Greenland Eemian Ice Drilling",
            "location": "Greenland (Northwest)",
            "sites": ["NEEM"],
            "depth_m": 2540,
            "age_years": 128000,
        },
        "Vostok": {
            "full_name": "Vostok Ice Core",
            "location": "Antarctica (Vostok Station)",
            "sites": ["Vostok"],
            "depth_m": 3769,
            "age_years": 420000,
        },
        "WAIS": {
            "full_name": "West Antarctic Ice Sheet Divide",
            "location": "Antarctica (West)",
            "sites": ["WAIS Divide"],
            "depth_m": 3405,
            "age_years": 68000,
        },
        "Dome_F": {
            "full_name": "Dome Fuji Ice Core",
            "location": "Antarctica (Dome Fuji)",
            "sites": ["Dome F"],
            "depth_m": 3035,
            "age_years": 720000,
        },
        "TALDICE": {
            "full_name": "Talos Dome Ice Core",
            "location": "Antarctica (Talos Dome)",
            "sites": ["TALDICE"],
            "depth_m": 1620,
            "age_years": 340000,
        },
        "Berkner": {
            "full_name": "Berkner Island Ice Core",
            "location": "Antarctica (Berkner Island)",
            "sites": ["Berkner"],
            "depth_m": 181,
            "age_years": 10000,
        },
    }
    return known_projects


def list_projects():
    """Imprime informações sobre os projetos disponíveis."""
    projects = get_projects()
    print(f"{'Projeto':<15} {'Localização':<35} {'Profundidade':<15} {'Idade máx (anos)'}")
    print("=" * 90)
    for name, info in projects.items():
        print(f"{name:<15} {info['location']:<35} {info['depth_m']:<15} {info['age_years']}")
    return projects


def get_iced_data_url(project, site=None, data_type="10Be"):
    """
    Constrói URL para download de dados do ICE-D.
    Nota: ICE-D pode exigir acesso via navegador para alguns datasets.
    """
    # URLs baseadas na estrutura conhecida do ICE-D
    if site is None:
        site = project

    base_urls = {
        "10Be": f"{ICED_BASE}/10Be/{site}",
        "26Al": f"{ICED_BASE}/26Al/{site}",
        "36Cl": f"{ICED_BASE}/36Cl/{site}",
        "14C": f"{ICED_BASE}/14C/{site}",
        "chemistry": f"{ICED_BASE}/chemistry/{site}",
    }
    return base_urls.get(data_type, f"{ICED_BASE}/{data_type}/{site}")


# Dados de referência: concentrações típicas de isótopos cosmogênicos em ice cores
REFERENCE_DATA = {
    "cosmogenic_isotopes": {
        "10Be": {
            "description": "Berílio-10, produzido por raios cósmicos na atmosfera",
            "half_life_years": 1.387e6,
            "measurement": "Átomos/g de gelo ou átomos/cm²/ano",
            "typical_range_antarctica": "1e4 - 1e6 atoms/g",
            "typical_range_greenland": "1e4 - 1e7 atoms/g",
        },
        "36Cl": {
            "description": "Cloro-36, produzido por interação de raios cósmicos com argônio",
            "half_life_years": 3.01e5,
            "measurement": "Átomos/g de gelo",
            "typical_range": "1e3 - 1e5 atoms/g",
        },
        "26Al": {
            "description": "Alumínio-26, produzido por espalação cósmica",
            "half_life_years": 7.17e5,
            "measurement": "Átomos/g de gelo",
        },
        "60Fe": {
            "description": "Ferro-60, produzido exclusivamente em supernovas",
            "half_life_years": 2.6e6,
            "measurement": "Átomos/g de gelo (extremamente raro)",
            "note": "Detectado em gelo antártico, evidência de supernova próxima (~2-3 milhões de anos atrás e ~40-80 mil anos atrás)",
        },
    },
    "stable_isotopes": {
        "d18O": {
            "description": "Razão ¹⁸O/¹⁶O, proxy de temperatura",
            "measurement": "‰ (permil) vs VSMOW",
            "typical_range_antarctica": "-60 a -30 ‰",
            "typical_range_greenland": "-45 a -20 ‰",
        },
        "dD": {
            "description": "Razão ²H/¹H, proxy de temperatura",
            "measurement": "‰ (permil) vs VSMOW",
        },
        "d_excess": {
            "description": "Excesso de deutério = dD - 8 * d18O",
            "measurement": "‰",
        },
    },
}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Coletor ICE-D Ice Core Data")
    parser.add_argument("--list-projects", action="store_true")
    parser.add_argument("--project", type=str)
    parser.add_argument("--data-type", default="10Be",
                        choices=["10Be", "26Al", "36Cl", "14C", "chemistry"])
    parser.add_argument("--reference", action="store_true",
                        help="Mostra dados de referência sobre isótopos cosmogênicos")
    args = parser.parse_args()

    if args.list_projects:
        list_projects()
    elif args.reference:
        import json
        print(json.dumps(REFERENCE_DATA, indent=2))
    elif args.project:
        projects = get_projects()
        if args.project not in projects:
            print(f"Projeto '{args.project}' não encontrado. Use --list-projects.")
        else:
            info = projects[args.project]
            print(f"\nProjeto: {args.project}")
            print(f"Nome completo: {info['full_name']}")
            print(f"Localização: {info['location']}")
            print(f"Profundidade: {info['depth_m']} m")
            print(f"Idade máxima: {info['age_years']} anos")
            url = get_iced_data_url(args.project, data_type=args.data_type)
            print(f"URL de dados ({args.data_type}): {url}")
            print("\nNota: alguns datasets do ICE-D podem exigir acesso via navegador.")
    else:
        print("Use --list-projects, --reference ou --project <nome>")
