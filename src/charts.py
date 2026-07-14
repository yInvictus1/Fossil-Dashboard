"""
src/charts.py
=============
Funcoes de visualizacao para o Fossil Dashboard.

Cada funcao recebe um DataFrame (ja filtrado) e retorna
um objeto de visualizacao (folium.Map ou plotly Figure).

Tarefas:
  4.1  criar_mapa_calor        — HeatMap + MarkerCluster  (Folium)
  4.2  criar_timeline_diversidade — barras empilhadas      (Plotly)
  4.3  criar_ranking_paises     — barras horizontais       (Plotly)
       criar_treemap_clados     — treemap hierarquico      (Plotly)
  4.4  criar_timeline_generos   — Gantt de generos         (Plotly)
"""

import folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# ── Paleta de cores ─────────────────────────────────────────────────
ERA_COLORS = {
    "Triassic": "#E07A5F",     # terracotta
    "Jurassic": "#3D405B",     # dark blue-grey
    "Cretaceous": "#81B29A",   # sage green
    "Desconhecido": "#999999",
}

ERA_ORDER = ["Triassic", "Jurassic", "Cretaceous", "Desconhecido"]

_PLOTLY_TEMPLATE = "plotly_dark"


# =====================================================================
# 4.1 — Mapa de calor de ocorrencias
# =====================================================================

def criar_mapa_calor(df: pd.DataFrame) -> folium.Map:
    """
    Mapa de calor global + MarkerCluster com popups.

    Parametros
    ----------
    df : DataFrame filtrado com colunas lat, lng, tna, oei.

    Retorna
    -------
    folium.Map
    """
    mapa = folium.Map(
        location=[20, 0],
        zoom_start=2,
        tiles="CartoDB dark_matter",
        control_scale=True,
    )

    # HeatMap
    heat_data = df[["lat", "lng"]].values.tolist()
    HeatMap(
        heat_data,
        radius=8,
        blur=12,
        max_zoom=6,
        gradient={
            0.2: "#ffffb2",
            0.4: "#fecc5c",
            0.6: "#fd8d3c",
            0.8: "#f03b20",
            1.0: "#bd0026",
        },
    ).add_to(mapa)

    # MarkerCluster (limitar a 5000 para performance)
    amostra = df.sample(n=min(5000, len(df)), random_state=42)
    cluster = MarkerCluster(name="Fosseis").add_to(mapa)

    for _, row in amostra.iterrows():
        popup_html = (
            f"<b>{row.get('tna', '?')}</b><br>"
            f"Periodo: {row.get('oei', '?')}<br>"
            f"Local: {row.get('cnm', '?')}"
        )
        folium.CircleMarker(
            location=[row["lat"], row["lng"]],
            radius=4,
            popup=folium.Popup(popup_html, max_width=250),
            color="#fd8d3c",
            fill=True,
            fill_opacity=0.7,
        ).add_to(cluster)

    folium.LayerControl().add_to(mapa)
    return mapa


# =====================================================================
# 4.2 — Timeline de diversidade por periodo geologico
# =====================================================================

def criar_timeline_diversidade(df: pd.DataFrame) -> go.Figure:
    """
    Barras empilhadas: contagem de especies unicas por era e familia.
    Inclui anotacao do evento K-Pg.
    """
    # Agrupar por era + familia, contar especies unicas
    agrupado = (
        df.groupby(["era", "familia"])["tna"]
        .nunique()
        .reset_index(name="especies")
    )

    # Top 10 familias para legibilidade
    top_familias = (
        agrupado.groupby("familia")["especies"]
        .sum()
        .nlargest(10)
        .index.tolist()
    )
    agrupado["familia_plot"] = agrupado["familia"].where(
        agrupado["familia"].isin(top_familias), "Outras"
    )

    # Ordem das eras
    agrupado["era"] = pd.Categorical(
        agrupado["era"], categories=ERA_ORDER, ordered=True
    )
    agrupado = agrupado.sort_values("era")

    fig = px.bar(
        agrupado,
        x="era",
        y="especies",
        color="familia_plot",
        template=_PLOTLY_TEMPLATE,
        labels={
            "era": "Era Geologica",
            "especies": "Especies Unicas",
            "familia_plot": "Familia",
        },
        title="Diversidade de Especies por Era Geologica",
        color_discrete_sequence=px.colors.qualitative.Set3,
    )

    fig.update_layout(
        barmode="stack",
        legend_title_text="Familia",
        xaxis_title="",
        yaxis_title="Especies Unicas",
        margin=dict(t=60, b=40),
    )

    # Anotacao K-Pg
    fig.add_annotation(
        x="Cretaceous",
        y=0,
        yref="y",
        text="K-Pg (66 Ma) - Extincao em massa",
        showarrow=True,
        arrowhead=2,
        arrowcolor="#ff6b6b",
        font=dict(color="#ff6b6b", size=11),
        ax=0,
        ay=-50,
    )

    return fig


# =====================================================================
# 4.3 — Ranking de paises e treemap de clados
# =====================================================================

def criar_ranking_paises(df: pd.DataFrame) -> go.Figure:
    """Top 15 paises com mais registros de fosseis."""
    contagem = (
        df.groupby("pais")
        .size()
        .reset_index(name="registros")
        .nlargest(15, "registros")
        .sort_values("registros")
    )

    fig = px.bar(
        contagem,
        x="registros",
        y="pais",
        orientation="h",
        template=_PLOTLY_TEMPLATE,
        title="Top 15 Paises com Mais Fosseis de Dinossauros",
        labels={"registros": "Registros", "pais": ""},
        color="registros",
        color_continuous_scale="YlOrRd",
    )

    fig.update_layout(
        showlegend=False,
        coloraxis_showscale=False,
        margin=dict(t=60, b=40, l=120),
        yaxis=dict(tickfont=dict(size=12)),
    )

    return fig


def criar_treemap_clados(df: pd.DataFrame) -> go.Figure:
    """Treemap hierarquico: familia -> especie com contagem de ocorrencias."""
    agrupado = (
        df.groupby(["familia", "tna"])
        .size()
        .reset_index(name="ocorrencias")
    )

    # Filtrar para familias com pelo menos 5 ocorrencias para legibilidade
    familias_relevantes = (
        agrupado.groupby("familia")["ocorrencias"]
        .sum()
        .loc[lambda s: s >= 5]
        .index
    )
    agrupado = agrupado[agrupado["familia"].isin(familias_relevantes)]

    fig = px.treemap(
        agrupado,
        path=["familia", "tna"],
        values="ocorrencias",
        template=_PLOTLY_TEMPLATE,
        title="Distribuicao Taxonomica — Familia / Especie",
        color="ocorrencias",
        color_continuous_scale="Viridis",
    )

    fig.update_layout(
        margin=dict(t=60, b=20, l=10, r=10),
        coloraxis_showscale=False,
    )

    return fig


# =====================================================================
# 4.4 — Linha do tempo de surgimento e extincao de generos
# =====================================================================

def criar_timeline_generos(df: pd.DataFrame) -> go.Figure:
    """
    Gantt horizontal mostrando a duracao de cada genero no registro fossil.
    Limitado aos 30 generos com mais ocorrencias.

    Usa eag (early_age, Ma) como inicio e lag (late_age, Ma) como fim.
    """
    # Extrair genero (primeiro nome do tna)
    df = df.copy()
    df["genero"] = df["tna"].str.split().str[0]

    # Top 30 generos por contagem de ocorrencias
    top_generos = (
        df["genero"]
        .value_counts()
        .head(30)
        .index.tolist()
    )
    df_top = df[df["genero"].isin(top_generos)]

    # Para cada genero: eag max (mais antigo) e lag min (mais recente)
    resumo = (
        df_top.groupby("genero")
        .agg(
            inicio=("eag", "max"),
            fim=("lag", "min"),
            ocorrencias=("oid", "count"),
        )
        .reset_index()
        .sort_values("inicio", ascending=True)
    )

    # Converter Ma para datas ficticias para o timeline do Plotly
    # Plotly timeline precisa de datetime, entao usamos uma escala linear
    # Alternativa: usar barras horizontais com go.Bar

    fig = go.Figure()

    colors = px.colors.qualitative.Alphabet
    for i, row in resumo.iterrows():
        idx = i % len(colors)
        fig.add_trace(go.Bar(
            y=[row["genero"]],
            x=[row["inicio"] - row["fim"]],
            base=[row["fim"]],
            orientation="h",
            marker=dict(color=colors[idx], opacity=0.85),
            hovertemplate=(
                f"<b>{row['genero']}</b><br>"
                f"Surgimento: {row['inicio']:.1f} Ma<br>"
                f"Ultimo registro: {row['fim']:.1f} Ma<br>"
                f"Ocorrencias: {row['ocorrencias']}<br>"
                "<extra></extra>"
            ),
            showlegend=False,
        ))

    fig.update_layout(
        template=_PLOTLY_TEMPLATE,
        title="Surgimento e Extincao dos 30 Generos Mais Registrados",
        xaxis=dict(
            title="Milhoes de anos atras (Ma)",
            autorange="reversed",
            showgrid=True,
            gridcolor="rgba(255,255,255,0.1)",
        ),
        yaxis=dict(
            title="",
            tickfont=dict(size=11),
            autorange="reversed",
        ),
        margin=dict(t=60, b=40, l=150),
        height=700,
        barmode="overlay",
    )

    # Linhas verticais para limites de eras
    era_limits = [
        (252, "Inicio Triassico", "#E07A5F"),
        (201, "Inicio Jurassico", "#3D405B"),
        (145, "Inicio Cretaceo", "#81B29A"),
        (66, "Extincao K-Pg", "#ff6b6b"),
    ]

    for ma, label, color in era_limits:
        fig.add_vline(
            x=ma,
            line=dict(color=color, width=1.5, dash="dash"),
            annotation_text=label,
            annotation_position="top",
            annotation_font_color=color,
            annotation_font_size=10,
        )

    return fig
