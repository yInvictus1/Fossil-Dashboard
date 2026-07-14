"""
app.py
======
Dino Fossil Dashboard — App Streamlit

Integra filtros interativos + 4 abas de visualizacao:
  - Mapa de calor (Folium)
  - Timeline de diversidade (Plotly)
  - Ranking de paises + Treemap (Plotly)
  - Timeline de generos (Plotly)

Tarefas: 5.1 (estrutura), 5.2 (filtros), 5.3 (abas), 5.4 (cache).
"""

import pathlib

import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from src.charts import (
    criar_mapa_calor,
    criar_ranking_paises,
    criar_timeline_diversidade,
    criar_timeline_generos,
    criar_treemap_clados,
)

# ── Configuracao da pagina ──────────────────────────────────────────
st.set_page_config(
    page_title="Dino Fossil Dashboard",
    page_icon="\U0001F996",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Caminhos ────────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "processed" / "ocorrencias_final.csv"


# ── Carregamento de dados (cacheado) ────────────────────────────────
@st.cache_data(ttl=3600)
def carregar_dados() -> pd.DataFrame:
    """Carrega o dataset final processado. Cacheado por sessao."""
    df = pd.read_csv(DATA_FILE)
    df["lat"] = df["lat"].astype(float)
    df["lng"] = df["lng"].astype(float)
    return df


# ── CSS customizado ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Fundo geral */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 50%, #16213e 100%);
    }

    /* Cards de metricas */
    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px 20px;
        backdrop-filter: blur(10px);
    }
    div[data-testid="stMetric"] label {
        color: #a0a0b0 !important;
        font-size: 0.85rem;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #f0f0f0 !important;
        font-size: 1.8rem;
        font-weight: 700;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    /* Tabs */
    button[data-baseweb="tab"] {
        font-size: 0.95rem;
        font-weight: 600;
    }

    /* Titulo principal */
    .main-title {
        text-align: center;
        padding: 10px 0 5px 0;
    }
    .main-title h1 {
        background: linear-gradient(90deg, #E07A5F, #81B29A, #F2CC8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0;
    }
    .main-title p {
        color: #888;
        font-size: 1rem;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ── Carregar dados ──────────────────────────────────────────────────
df_completo = carregar_dados()

# ── Titulo ──────────────────────────────────────────────────────────
st.markdown("""
<div class="main-title">
    <h1>Dino Fossil Dashboard</h1>
    <p>Visualizacao interativa de fosseis de dinossauros ao redor do mundo</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# =====================================================================
# SIDEBAR — Filtros (Tarefa 5.2)
# =====================================================================
with st.sidebar:
    st.markdown("## :mag: Filtros")
    st.caption("Selecione os criterios para filtrar os dados.")

    # Era Geologica
    eras_disponiveis = sorted(df_completo["era"].unique().tolist())
    eras_selecionadas = st.multiselect(
        "Era Geologica",
        options=eras_disponiveis,
        default=[e for e in ["Triassic", "Jurassic", "Cretaceous"] if e in eras_disponiveis],
        help="Filtre por uma ou mais eras geologicas.",
    )

    # Continente
    continentes_disponiveis = sorted(df_completo["continente"].unique().tolist())
    continentes_selecionados = st.multiselect(
        "Continente",
        options=continentes_disponiveis,
        default=continentes_disponiveis,
        help="Filtre por continente.",
    )

    # Familia
    familias_disponiveis = sorted(df_completo["familia"].unique().tolist())
    familias_selecionadas = st.multiselect(
        "Familia Taxonomica",
        options=familias_disponiveis,
        default=[],
        help="Deixe vazio para incluir todas as familias.",
    )

    # Pais
    paises_disponiveis = ["Todos"] + sorted(df_completo["pais"].unique().tolist())
    pais_selecionado = st.selectbox(
        "Pais",
        options=paises_disponiveis,
        index=0,
        help="Filtre por um pais especifico.",
    )

    st.divider()

# ── Aplicar filtros ─────────────────────────────────────────────────
df_filtrado = df_completo.copy()

if eras_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["era"].isin(eras_selecionadas)]

if continentes_selecionados:
    df_filtrado = df_filtrado[df_filtrado["continente"].isin(continentes_selecionados)]

if familias_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["familia"].isin(familias_selecionadas)]

if pais_selecionado != "Todos":
    df_filtrado = df_filtrado[df_filtrado["pais"] == pais_selecionado]

# ── Metricas no topo ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### :bar_chart: Resumo")
    st.metric("Registros", f"{len(df_filtrado):,}")
    st.metric("Especies", f"{df_filtrado['tna'].nunique():,}")
    st.metric("Paises", f"{df_filtrado['pais'].nunique():,}")
    st.metric("Familias", f"{df_filtrado['familia'].nunique():,}")

# ── Verificar dados ─────────────────────────────────────────────────
if df_filtrado.empty:
    st.warning(
        "Nenhum registro encontrado com os filtros selecionados. "
        "Ajuste os filtros na sidebar."
    )
    st.stop()

# =====================================================================
# ABAS DE VISUALIZACAO (Tarefa 5.3)
# =====================================================================
tab_mapa, tab_timeline, tab_paises, tab_generos = st.tabs([
    ":earth_americas: Mapa",
    ":hourglass_flowing_sand: Timeline",
    ":trophy: Paises & Clados",
    ":calendar: Generos",
])

# ── Aba 1: Mapa de calor ────────────────────────────────────────────
with tab_mapa:
    st.markdown("### :world_map: Mapa de Calor de Ocorrencias Fosseis")
    st.caption(
        f"Exibindo {len(df_filtrado):,} registros. "
        "Clique nos clusters para explorar os pontos individuais."
    )
    mapa = criar_mapa_calor(df_filtrado)
    st_folium(mapa, width=None, height=550, returned_objects=[])

# ── Aba 2: Timeline de diversidade ──────────────────────────────────
with tab_timeline:
    st.markdown("### :chart_with_upwards_trend: Diversidade por Era Geologica")
    fig_timeline = criar_timeline_diversidade(df_filtrado)
    st.plotly_chart(fig_timeline, width="stretch", key="timeline")

# ── Aba 3: Paises + Treemap ─────────────────────────────────────────
with tab_paises:
    col_ranking, col_treemap = st.columns(2)

    with col_ranking:
        st.markdown("### :trophy: Ranking de Paises")
        fig_ranking = criar_ranking_paises(df_filtrado)
        st.plotly_chart(fig_ranking, width="stretch", key="ranking")

    with col_treemap:
        st.markdown("### :deciduous_tree: Treemap Taxonomico")
        fig_treemap = criar_treemap_clados(df_filtrado)
        st.plotly_chart(fig_treemap, width="stretch", key="treemap")

# ── Aba 4: Timeline de generos ──────────────────────────────────────
with tab_generos:
    st.markdown("### :dna: Surgimento e Extincao de Generos")
    st.caption(
        "Os 30 generos com mais ocorrencias no registro fossil. "
        "Linhas tracejadas indicam os limites de cada era."
    )
    fig_generos = criar_timeline_generos(df_filtrado)
    st.plotly_chart(fig_generos, width="stretch", key="generos")

# ── Footer ──────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<div style='text-align:center; color:#666; font-size:0.8rem;'>"
    "Dados: <a href='https://paleobiodb.org' style='color:#81B29A;'>"
    "Paleobiology Database</a> | "
    "Feito com Streamlit, Plotly e Folium"
    "</div>",
    unsafe_allow_html=True,
)
