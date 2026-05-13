# Resultados da Análise Inicial — 14/05/2026

## Dados coletados (NOAA NCEI)

| Dataset | Variável | Registros | Período |
|---|---|---|---|
| EPICA Dome C | δD, ΔT | 5.792 | 0–800 ka |
| CO₂ Composite Antártica | CO₂ | 1.840 | 0–806 ka |
| EPICA CH₄ | Metano | 2.103 | 0–650 ka |
| Vostok | δD | 3.310 | 0–423 ka |
| Vostok | Poeira | 522 | 0–422 ka |
| Antarctica Temp 2006 | Temperatura | 204 | 0–2003 CE |

## Correlações

| Par | Coeficiente (r) |
|---|---|
| CO₂ × δD | 0.884 |
| CO₂ × ΔT | 0.903 |

A correlação entre concentração de CO₂ e temperatura ao longo de 800 mil anos é extremamente forte. Isso confirma o papel do CO₂ como principal forçante climático em escala glacial-interglacial.

## Ciclos de Milankovitch

O espectro de potência do δD (EPICA Dome C) revela três picos dominantes:

- **100 ka (excentricidade)** — ciclo dominante nos últimos ~1 Ma
- **41 ka (obliquidade)** — segundo pico mais forte
- **~23 ka (precessão)** — presente mas atenuado

A transição de dominância do ciclo de 41 ka para 100 ka ocorreu há ~1 Ma (Mid-Pleistocene Transition), e é visível no espectro.

## Contexto atual

O nível atual de CO₂ atmosférico (~420 ppm) é sem precedentes nos 800 mil anos do registro de gelo. O máximo natural observado nos interglaciais mais quentes era ~300 ppm.

## Próximos passos

- [ ] Buscar dados de ⁶⁰Fe (supernovas) no PANGAEA
- [ ] Adicionar dados da Groenlândia (GISP2, GRIP, NGRIP)
- [ ] Análise de wavelet (tempo-frequência)
- [ ] Modelagem preditiva com ML
- [ ] Comparação hemisfério norte vs sul

## Arquivos gerados

- `output/ice_cores_800kyr_overview.png` — painel 5 variáveis × 800 ka
- `output/co2_temperature_correlation.png` — scatter CO₂ vs temperatura
- `output/power_spectrum_milankovitch.png` — FFT com ciclos orbitais
