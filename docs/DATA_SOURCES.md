# Fontes de Dados de Ice Cores

## Repositórios Principais

### 1. NOAA NCEI Paleoclimatology
- **URL:** https://www.ncei.noaa.gov/products/paleoclimatology/ice-core
- **Tipo:** Dados processados e publicados
- **Formato:** TXT (tab-delimited com metadados em comentários `#`)
- **Cobertura:** Global (Antártica, Groenlândia, Andes, Alpes, Himalaia, África)
- **Variáveis:** δ¹⁸O, δD, CO₂, CH₄, poeira, acidez, química iônica, isótopos cosmogênicos
- **Acesso:** Livre, sem autenticação

### 2. PANGAEA
- **URL:** https://www.pangaea.de
- **Tipo:** Dados brutos de pesquisas publicadas
- **Formato:** TXT (tab-delimited com metadados `/* */`)
- **Cobertura:** Global, forte presença europeia
- **Variáveis:** Todas, incluindo dados brutos de espectrometria
- **Acesso:** Livre via DOI, alguns datasets restritos

### 3. ICE-D: Ice Cores
- **URL:** http://www.ice-d.org
- **Tipo:** Especializado em isótopos cosmogênicos
- **Formato:** Varia por dataset
- **Cobertura:** Antártica e Groenlândia
- **Variáveis:** ¹⁰Be, ²⁶Al, ³⁶Cl, ⁴¹Ca
- **Acesso:** Livre via navegador

### 4. NSIDC
- **URL:** https://nsidc.org
- **Tipo:** Propriedades físicas do gelo
- **Formato:** Varia
- **Cobertura:** Polar
- **Variáveis:** Temperatura, espessura, velocidade de fluxo

## Projetos de Ice Cores com Dados Abertos

| Projeto | Localização | Profundidade (m) | Idade máx (anos) | Repositório |
|---|---|---|---|---|
| EPICA Dome C | Antártica | 3,270 | 800,000 | NOAA/PANGAEA |
| EPICA EDML | Antártica | 2,560 | 150,000 | PANGAEA |
| GISP2 | Groenlândia | 3,053 | 110,000 | NOAA |
| GRIP | Groenlândia | 3,029 | 123,000 | NOAA/PANGAEA |
| NGRIP | Groenlândia | 3,085 | 123,000 | PANGAEA |
| NEEM | Groenlândia | 2,540 | 128,000 | PANGAEA |
| Vostok | Antártica | 3,769 | 420,000 | NOAA |
| WAIS Divide | Antártica | 3,405 | 68,000 | NOAA |
| Dome Fuji | Antártica | 3,035 | 720,000 | NOAA/PANGAEA |
| TALDICE | Antártica | 1,620 | 340,000 | PANGAEA |

## Variáveis e Espectros

### Isótopos estáveis (IRMS)
- **δ¹⁸O:** Razão ¹⁸O/¹⁶O, proxy de temperatura. Medido por espectrometria de massas de razão isotópica (IRMS).
- **δD:** Razão ²H/¹H, proxy de temperatura.
- **d-excess:** dD - 8 × δ¹⁸O, indicador de umidade de origem.

### Isótopos cosmogênicos (AMS)
- **¹⁰Be:** Produzido por raios cósmicos na atmosfera. Meia-vida: 1.387 Ma. Indica atividade solar e cósmica.
- **³⁶Cl:** Produzido por interação de raios cósmicas com argônio. Meia-vida: 301 ka.
- **²⁶Al:** Produzido por espalação cósmica. Meia-vida: 717 ka.
- **⁶⁰Fe:** Produzido exclusivamente em supernovas. Meia-vida: 2.6 Ma. Evidência direta de supernovas próximas.

### Gases atmosféricos (GC/MS)
- **CO₂:** Extraído de bolhas de ar no gelo. Medido por cromatografia gasosa.
- **CH₄:** Metano atmosférico preservado em bolhas.
- **N₂O:** Óxido nitroso.

### Química iônica (IC)
- **Cátions:** Na⁺, Ca²⁺, Mg²⁺, K⁺, NH₄⁺
- **Ânions:** Cl⁻, SO₄²⁻, NO₃⁻, F⁻, CH₃SO₃⁻ (MSA)
- **Origem:** Poeira marinha, continental, vulcânica, biogênica

### Elementos traço (ICP-MS)
- Metais: Fe, Al, Ti, Mn, Ba, Sr, etc.
- Razões isotópicas de Pb (fonte de poeira)
- Elementos terras raras (assinatura de fonte)

### Propriedades físicas
- **Poeira insolúvel:** Contagem de partículas, concentração em ppm
- **Condutividade elétrica (ECM):** Indicador de acidez/vulcanismo
- **Luminosidade:** Reflectância, indicador de poeira
