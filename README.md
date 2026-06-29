<h1 align="center">🦕 Fossil Dashboard</h1>
<p align="center">
  Dashboard interativo de fósseis ao redor do mundo, alimentado pela API pública da Paleobiology Database (PBDB)
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Dash-Plotly-00b4d8?style=for-the-badge&logo=plotly&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-2.0+-green?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/API-PBDB-orange?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow?style=for-the-badge"/>
</p>

---

## 📋 Sobre o Projeto

O **Fossil Dashboard** é uma aplicação web interativa que consome a [API pública da Paleobiology Database (PBDB)](https://paleobiodb.org/data1.2/) para visualizar no mapa mundial onde fósseis de dinossauros e outros organismos pré-históricos foram encontrados.

O projeto foi desenvolvido como parte do portfólio pessoal na área de **Data Science e Visualização de Dados**, sem necessidade de autenticação para consumir a API.

---

## ✨ Funcionalidades

- 🗺️ **Mapa interativo** com a distribuição geográfica de fósseis ao redor do mundo
- 🕰️ **Filtro por Era Geológica** — Triássico, Jurássico, Cretáceo e mais
- 🦖 **Filtro por Táxon** — busca por espécie ou gênero (ex: *Tyrannosaurus*, *Diplodocus*)
- 🌎 **Filtro por País** — usando códigos ISO-3166
- 📊 **Gráficos de apoio** — distribuição por era e top países com mais registros
- ⚡ **Dados em tempo real** direto da API PBDB, sem banco de dados local

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.11+ | Linguagem principal |
| Dash (Plotly) | Framework do dashboard |
| Plotly Express | Mapas e gráficos interativos |
| Pandas | Processamento dos dados da API |
| Requests | Consumo da API PBDB |
| Render / HuggingFace Spaces | Deploy gratuito |

---

## 🏗️ Estrutura do Projeto

```
fossil-dashboard/
├── app.py                  # App principal Dash
├── data/
│   └── fetch_pbdb.py       # Módulo de consumo da API PBDB
├── components/
│   ├── map.py              # Componente do mapa interativo
│   └── filters.py          # Filtros (era, táxon, país)
├── assets/
│   └── style.css           # Estilização customizada
├── requirements.txt
└── README.md
```

---

## 🌐 API Utilizada

Este projeto utiliza a **Paleobiology Database API v1.2** — pública e sem autenticação.

```
# Endpoint principal de ocorrências
GET https://paleobiodb.org/data1.2/occs/list.json
    ?base_name=Dinosauria
    &show=coords,classext
    &interval=Cretaceous
    &cc=BR
    &limit=5000
```

Documentação oficial: [paleobiodb.org/data1.2](https://paleobiodb.org/data1.2/)

---

## 🚀 Como Executar Localmente

**Pré-requisitos:** Python 3.11+

```bash
# 1. Clone o repositório
git clone https://github.com/SEU_USUARIO/fossil-dashboard.git
cd fossil-dashboard

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute a aplicação
python app.py
```

Acesse em: `http://localhost:8050`

---

## 📦 requirements.txt

```
dash>=2.14.0
plotly>=5.18.0
pandas>=2.0.0
requests>=2.31.0
```

---

## 🗺️ Roadmap

- [x] Estrutura base do projeto
- [x] Consumo da API PBDB
- [ ] Mapa interativo com scatter_mapbox
- [ ] Filtros reativos (era, táxon, país)
- [ ] Gráficos de distribuição por era geológica
- [ ] Slider de período em Ma (Milhões de anos)
- [ ] Deploy no Render / HuggingFace Spaces


---

<p align="center">
  ⭐ Se este projeto foi útil, considere deixar uma estrela!
</p>
