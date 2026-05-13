# 🧊 Ice Core Data Lab

Pipeline de coleta, processamento e análise de dados de núcleos de gelo (ice cores) para Ciência de Dados Aplicada.

## Objetivo

Consolidar dados de múltiplos repositórios de ice cores em um único pipeline analisável, incluindo:

- Isótopos cosmogênicos (¹⁰Be, ³⁶Cl, ²⁶Al, ⁶⁰Fe)
- Isótopos estáveis (δ¹⁸O, δD)
- Gases atmosféricos (CO₂, CH₄, N₂O)
- Composição química iônica (SO₄²⁻, NO₃⁻, Cl⁻, Na⁺, Ca²⁺)
- Elementos traço e metais
- Propriedades físicas (poeira, acidez, condutividade)

## Fontes de Dados

| Repositório | Tipo | URL |
|---|---|---|
| NOAA NCEI | Paleoclima geral | ncei.noaa.gov/products/paleoclimatology/ice-core |
| PANGAEA | Dados brutos de pesquisas | pangaea.de |
| ICE-D | Isótopos cosmogênicos | ice-d.org |
| NSIDC | Propriedades físicas | nsidc.org |

## Estrutura

```
ice-core-data-lab/
├── data/
│   ├── raw/          # Dados brutos baixados
│   ├── processed/    # Dados limpos e padronizados
│   └── external/     # Dados de referência
├── notebooks/        # Análises exploratórias
├── src/
│   ├── collectors/   # Scripts de coleta por repositório
│   ├── processors/   # Limpeza e padronização
│   └── analysis/     # Análises estatísticas e ML
├── docs/             # Documentação
└── output/           # Resultados e figuras
```

## Setup

```bash
pip install -r requirements.txt
python src/collectors/noaa_collector.py
```

## Roadmap

- [ ] Coletor NOAA NCEI
- [ ] Coletor PANGAEA
- [ ] Coletor ICE-D
- [ ] Padronização de schemas
- [ ] Análise exploratória (notebooks)
- [ ] Modelagem preditiva
