<div align="center">

# 🗺️ Dino Fossil Dashboard

### Visualização interativa de fósseis de dinossauros ao redor do mundo

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Plotly](https://img.shields.io/badge/Plotly-5.0%2B-3F4F75?logo=plotly&logoColor=white)](https://plotly.com)
[![PBDB](https://img.shields.io/badge/Dados-PBDB%20API-4B9CD3)](https://paleobiodb.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E.svg)](LICENSE)

**[🔴 Demo ao vivo](#) · [📊 Visualizações](#visualizações) · [⚡ Instalação](#instalação) · [📁 Estrutura](#estrutura-do-projeto)**

</div>

---

## Sobre o projeto

App interativo desenvolvido com **Streamlit** e alimentado por dados reais da **Paleobiology Database (PBDB)** — API pública e gratuita, sem necessidade de autenticação. Exibe onde fósseis de dinossauros foram encontrados ao redor do mundo, com filtros por era geológica, espécie, família taxonômica e país.

Todos os dados são obtidos diretamente da PBDB e processados localmente. Não há dependência de banco de dados externo ou credenciais adicionais.

---

## Visualizações

| Aba | Visualização | Tecnologia |
|-----|-------------|-----------|
| 🌍 Mapa | Mapa de calor global de ocorrências de fósseis | Folium · HeatMap |
| ⏳ Timeline | Diversidade de espécies por período geológico | Plotly · Barras empilhadas |
| 🏆 Países | Ranking dos países com mais descobertas | Plotly · Barras horizontais |
| 🌿 Clados | Distribuição de espécies por família taxonômica | Plotly · Treemap |
| 📅 Gêneros | Surgimento e extinção de gêneros ao longo do tempo | Plotly · Gantt |

### Filtros disponíveis na sidebar

- Era Geológica (Triassic · Jurassic · Cretaceous)
- Continente
- Família taxonômica
- País

---

## Fontes de dados

Todos os dados vêm da **Paleobiology Database (PBDB)**, uma base de dados paleontológica colaborativa e de acesso público.

| Endpoint | Dados | Link |
|----------|-------|------|
| `/occs/list.json` | Ocorrências de fósseis com coordenadas e época | [PBDB Ocorrências](https://paleobiodb.org/data1.2/occs/list.json) |
| `/taxa/list.json` | Hierarquia taxonômica de Dinosauria | [PBDB Taxonomia](https://paleobiodb.org/data1.2/taxa/list.json) |
| `/colls/list.json` | Sítios de escavação por período | [PBDB Sítios](https://paleobiodb.org/data1.2/colls/list.json) |

> A API não requer autenticação. A coleta é paginada por período geológico para contornar o limite de 5 000 registros por requisição.

---

## Estrutura do projeto

```
dino-dashboard/
├── data/
│   ├── raw/                    # JSONs brutos da API (não versionados)
│   │   ├── ocorrencias_triassic.json
│   │   ├── ocorrencias_jurassic.json
│   │   ├── ocorrencias_cretaceous.json
│   │   ├── taxonomia.json
│   │   └── sitios.json
│   └── processed/
│       └── ocorrencias_final.csv   # dataset limpo e enriquecido
├── docs/
│   ├── api_pbdb.md             # endpoints e parâmetros documentados
│   └── qualidade_dados.md      # estatísticas de completude do dataset
├── notebooks/
│   ├── 01_exploracao_api.ipynb
│   ├── 02_limpeza_dados.ipynb
│   └── 03_visualizacoes.ipynb
├── src/
│   ├── fetch_pbdb.py           # coleta com paginação e cache local
│   ├── process.py              # limpeza e enriquecimento dos dados
│   └── charts.py               # funções de criação de cada visualização
├── .streamlit/
│   └── config.toml             # configurações visuais do app
├── app.py                      # app principal Streamlit
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Instalação

### Pré-requisitos

- Python 3.10 ou superior
- Conexão com internet (para a coleta inicial de dados via PBDB)

### Passos

```bash
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/dino-dashboard.git
cd dino-dashboard

# 2. Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
# .venv\Scripts\activate         # Windows

# 3. Instalar dependências
pip install -r requirements.txt
```

---

## Como usar

### Coletar os dados (primeira vez)

```bash
python src/fetch_pbdb.py
```

Isso irá consultar a API do PBDB, coletar as ocorrências de Dinosauria paginadas por período geológico e salvar o resultado processado em `data/processed/ocorrencias_final.csv`. A coleta completa leva aproximadamente 2–3 minutos.

### Rodar o app

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador. Use a sidebar para aplicar filtros e explore as abas para alternar entre as visualizações.

### Consultar a API diretamente

```python
import requests
import pandas as pd

def buscar_fosseis(taxon="Dinosauria", intervalo="Jurassic", limite=5000):
    r = requests.get(
        "https://paleobiodb.org/data1.2/occs/list.json",
        params={
            "base_name": taxon,
            "show":      "coords,coll,time",
            "interval":  intervalo,
            "limit":     limite,
        },
        timeout=30,
    )
    df = pd.DataFrame(r.json()["records"])
    return df.dropna(subset=["lat", "lng"])

# Exemplo: fósseis do período Jurássico
df = buscar_fosseis(intervalo="Jurassic")
print(df[["accepted_name", "lat", "lng", "early_interval"]].head(10))
```

---

## Dataset processado

O arquivo `data/processed/ocorrencias_final.csv` contém as seguintes colunas:

| Coluna | Descrição |
|--------|-----------|
| `accepted_name` | Nome científico aceito da espécie |
| `lat` | Latitude do sítio de escavação |
| `lng` | Longitude do sítio de escavação |
| `early_interval` | Período geológico (valor original da API) |
| `era` | Era normalizada: Triassic, Jurassic ou Cretaceous |
| `cc` | Código ISO 3166 do país |
| `pais` | Nome completo do país |
| `continente` | Continente derivado do código de país |
| `familia` | Família taxonômica (via merge com endpoint de taxonomia) |
| `formation` | Formação geológica do sítio |
| `environment` | Ambiente de deposição (fluvial, lacustre, etc.) |

---

## Stack

| Categoria | Tecnologia |
|-----------|-----------|
| App web | [Streamlit](https://streamlit.io) |
| Manipulação de dados | [pandas](https://pandas.pydata.org) |
| Análise geoespacial | [GeoPandas](https://geopandas.org) |
| Mapas interativos | [Folium](https://python-visualization.github.io/folium/) + [streamlit-folium](https://pypi.org/project/streamlit-folium/) |
| Gráficos | [Plotly Express](https://plotly.com/python/plotly-express/) |
| Fonte de dados | [Paleobiology Database API](https://paleobiodb.org/data1.2/) |
| Hospedagem | [Streamlit Cloud](https://share.streamlit.io) |

---

## Deploy

O app está hospedado gratuitamente no **Streamlit Cloud**, conectado diretamente a este repositório GitHub. Qualquer push na branch `main` atualiza automaticamente a versão publicada.

Para fazer seu próprio deploy:
1. Faça fork deste repositório
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub e selecione o repositório
4. Defina `app.py` como arquivo de entrada e clique em "Deploy"

---

## Licença

Distribuído sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais informações.

Os dados utilizados são provenientes da [Paleobiology Database](https://paleobiodb.org), disponibilizados sob licença [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

<div align="center">
Feito com Python · Streamlit · e dados de 230 milhões de anos atrás 🦖
</div>
