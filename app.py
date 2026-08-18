"""
COVID-19 Worldwide Dashboard
-----------------------------
Dashboard interativo em Streamlit para explorar dados globais de casos,
mortes, recuperações e testes de COVID-19 por país.

Autor: Karolyne Muniz
Fonte dos dados: Worldwide COVID-19 dataset (snapshot agregado, 221 países/territórios)
"""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ----------------------------------------------------------------------------
# Configuração da página
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="COVID-19 Worldwide Dashboard",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent


def _resolve_existing_path(*candidates: Path) -> Path:
    for candidate in candidates:
        if candidate.exists():
            return candidate
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Arquivo de dados não encontrado. Procurei em: {searched}")


DATA_PATH = _resolve_existing_path(
    BASE_DIR / "data" / "worldwide_covid_data.csv",
    BASE_DIR / "worldwide_covid_data.csv",
    BASE_DIR / "dataset" / "worldwide covid data.csv",
)
CONTINENT_PATH = _resolve_existing_path(
    BASE_DIR / "data" / "continent_mapping.json",
    BASE_DIR / "continent_mapping.json",
)


# ----------------------------------------------------------------------------
# Carregamento e preparação dos dados
# ----------------------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df = df.rename(columns={
        "Country/Other": "Country",
        "Tot Cases/ 1M pop": "Cases per 1M",
        "Deaths/ 1M pop": "Deaths per 1M",
        "Tests/ 1M pop": "Tests per 1M",
    })

    with open(CONTINENT_PATH, "r", encoding="utf-8") as f:
        geo_map = json.load(f)
    df["Continent"] = df["Country"].map(lambda c: geo_map.get(c, {}).get("continent", "Não classificado"))
    df["ISO3"] = df["Country"].map(lambda c: geo_map.get(c, {}).get("iso3"))

    # Métricas derivadas
    df["Mortality Rate (%)"] = (df["Total Deaths"] / df["Total Cases"] * 100).round(2)
    df["Recovery Rate (%)"] = (df["Total Recovered"] / df["Total Cases"] * 100).round(2)
    df["Tests per Case"] = (df["Total Tests"] / df["Total Cases"]).round(2)

    return df


df = load_data()

# ----------------------------------------------------------------------------
# Sidebar — filtros
# ----------------------------------------------------------------------------
st.sidebar.title("🦠 Filtros")

continents = sorted(df["Continent"].unique())
selected_continents = st.sidebar.multiselect(
    "Continente", options=continents, default=continents
)

min_pop = int(df["Population"].min())
max_pop = int(df["Population"].max())
pop_threshold = st.sidebar.number_input(
    "População mínima (filtra países muito pequenos)",
    min_value=0, max_value=max_pop, value=1_000_000, step=100_000,
    help="Recomendado manter >0 para evitar que microestados distorçam as taxas per capita.",
)

metric_options = {
    "Total de Casos": "Total Cases",
    "Total de Mortes": "Total Deaths",
    "Casos por 1M hab.": "Cases per 1M",
    "Mortes por 1M hab.": "Deaths per 1M",
    "Taxa de Mortalidade (%)": "Mortality Rate (%)",
    "Taxa de Recuperação (%)": "Recovery Rate (%)",
    "Testes por 1M hab.": "Tests per 1M",
}
ranking_label = st.sidebar.selectbox("Métrica para os rankings", list(metric_options.keys()), index=0)
ranking_metric = metric_options[ranking_label]

top_n = st.sidebar.slider("Quantos países mostrar nos rankings", 5, 30, 15)

st.sidebar.markdown("---")
st.sidebar.caption(
    "Dados agregados (snapshot). Países com população abaixo do limiar definido "
    "são incluídos nos totais gerais, mas podem ser excluídos dos rankings per capita "
    "para evitar distorções estatísticas."
)

filtered = df[df["Continent"].isin(selected_continents)].copy()
filtered_percapita = filtered[filtered["Population"] >= pop_threshold].copy()

# ----------------------------------------------------------------------------
# Cabeçalho e KPIs
# ----------------------------------------------------------------------------
st.title("🦠 COVID-19 Worldwide Dashboard")
st.caption(
    "Análise exploratória de casos, mortes, recuperações e testes de COVID-19 "
    "em 221 países e territórios."
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Países/territórios", f"{filtered['Country'].nunique()}")
k2.metric("Total de Casos", f"{filtered['Total Cases'].sum():,.0f}")
k3.metric("Total de Mortes", f"{filtered['Total Deaths'].sum():,.0f}")
k4.metric(
    "Mortalidade Global",
    f"{(filtered['Total Deaths'].sum() / filtered['Total Cases'].sum() * 100):.2f}%",
)
k5.metric("Total de Testes", f"{filtered['Total Tests'].sum():,.0f}")

st.markdown("---")

# ----------------------------------------------------------------------------
# Abas
# ----------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["🌍 Visão Geral", "🏆 Rankings", "🔗 Correlações", "🔍 Explorar por País"]
)

# --- Tab 1: Visão geral -----------------------------------------------------
with tab1:
    col1, col2 = st.columns([1.3, 1])

    with col1:
        st.subheader("Mapa Mundial")
        map_df = filtered.dropna(subset=["ISO3"]).copy()
        fig_map = px.choropleth(
            map_df,
            locations="ISO3",
            color=ranking_metric,
            hover_name="Country",
            color_continuous_scale="Reds",
            title=f"{ranking_label} por país",
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0), height=450)
        st.plotly_chart(fig_map, width='stretch')

    with col2:
        st.subheader("Distribuição por Continente")
        cont_agg = (
            filtered.groupby("Continent")[["Total Cases", "Total Deaths"]]
            .sum()
            .reset_index()
            .sort_values("Total Cases", ascending=False)
        )
        fig_pie = px.pie(
            cont_agg, names="Continent", values="Total Cases", hole=0.45,
            title="Participação nos casos globais",
        )
        fig_pie.update_layout(height=450)
        st.plotly_chart(fig_pie, width='stretch')

    st.subheader("Casos e Mortes totais por continente")
    fig_bar = px.bar(
        cont_agg.melt(id_vars="Continent", value_vars=["Total Cases", "Total Deaths"]),
        x="Continent", y="value", color="variable", barmode="group",
        labels={"value": "Total", "variable": "Métrica"},
    )
    st.plotly_chart(fig_bar, width='stretch')

# --- Tab 2: Rankings ---------------------------------------------------------
with tab2:
    st.subheader(f"Top {top_n} países — {ranking_label}")
    is_percapita = "1M" in ranking_metric or "%" in ranking_metric
    base = filtered_percapita if is_percapita else filtered
    if is_percapita:
        st.info(
            f"Ranking calculado apenas para países com população ≥ {pop_threshold:,.0f} "
            "habitantes, para evitar distorções de microestados.",
            icon="ℹ️",
        )

    ranked = base.nlargest(top_n, ranking_metric)[["Country", "Continent", ranking_metric]]
    fig_rank = px.bar(
        ranked.sort_values(ranking_metric),
        x=ranking_metric, y="Country", color="Continent", orientation="h",
        height=max(400, top_n * 28),
    )
    st.plotly_chart(fig_rank, width='stretch')

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Maiores valores**")
        st.dataframe(
            base.nlargest(top_n, ranking_metric)[["Country", ranking_metric]]
            .reset_index(drop=True),
            width='stretch',
        )
    with col_b:
        st.markdown("**Menores valores**")
        min_base = base[base["Total Cases"] > 1000] if "Mortality" in ranking_metric or "Recovery" in ranking_metric else base
        st.dataframe(
            min_base.nsmallest(top_n, ranking_metric)[["Country", ranking_metric]]
            .reset_index(drop=True),
            width='stretch',
        )

# --- Tab 3: Correlações -------------------------------------------------------
with tab3:
    st.subheader("Testes vs. Casos detectados por 1M habitantes")
    st.caption(
        "Cada ponto é um país. A relação sugere até que ponto o volume de testes "
        "influencia o número de casos oficialmente detectados."
    )
    scatter_df = filtered_percapita.dropna(subset=["Tests per 1M", "Cases per 1M"])
    fig_scatter = px.scatter(
        scatter_df, x="Tests per 1M", y="Cases per 1M", color="Continent",
        size="Population", hover_name="Country", log_x=True, log_y=True,
        trendline="ols",
    )
    st.plotly_chart(fig_scatter, width='stretch')

    corr_val = scatter_df[["Tests per 1M", "Cases per 1M"]].corr().iloc[0, 1]
    st.metric("Correlação (Testes/1M x Casos/1M)", f"{corr_val:.2f}")

    st.subheader("Matriz de correlação entre indicadores")
    corr_cols = [
        "Total Cases", "Total Deaths", "Cases per 1M", "Deaths per 1M",
        "Tests per 1M", "Population",
    ]
    corr_matrix = filtered[corr_cols].corr().round(2)
    fig_heat = px.imshow(
        corr_matrix, text_auto=True, color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
    )
    st.plotly_chart(fig_heat, width='stretch')

# --- Tab 4: Explorar por país --------------------------------------------------
with tab4:
    st.subheader("Detalhes por país")
    country_choice = st.selectbox("Selecione um país", sorted(filtered["Country"].unique()))
    row = filtered[filtered["Country"] == country_choice].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Casos totais", f"{row['Total Cases']:,.0f}")
    c2.metric("Mortes totais", f"{row['Total Deaths']:,.0f}")
    c3.metric("Taxa de mortalidade", f"{row['Mortality Rate (%)']:.2f}%")
    c4.metric("Taxa de recuperação", f"{row['Recovery Rate (%)']:.2f}%" if pd.notna(row['Recovery Rate (%)']) else "N/D")

    c5, c6, c7 = st.columns(3)
    c5.metric("Casos ativos", f"{row['Active Cases']:,.0f}" if pd.notna(row["Active Cases"]) else "N/D")
    c6.metric("Testes realizados", f"{row['Total Tests']:,.0f}" if pd.notna(row["Total Tests"]) else "N/D")
    c7.metric("Testes por 1M hab.", f"{row['Tests per 1M']:,.0f}" if pd.notna(row["Tests per 1M"]) else "N/D")

    st.markdown("**Composição dos casos (mortes, recuperados, ativos)**")
    comp = pd.DataFrame({
        "Categoria": ["Mortes", "Recuperados", "Ativos"],
        "Valor": [row["Total Deaths"], row["Total Recovered"], row["Active Cases"]],
    }).dropna()
    if not comp.empty:
        fig_comp = px.pie(comp, names="Categoria", values="Valor", hole=0.4)
        st.plotly_chart(fig_comp, width='stretch')

    st.markdown("**Tabela completa filtrada**")
    st.dataframe(filtered.reset_index(drop=True), width='stretch')

st.markdown("---")
st.caption(
    "Dashboard construído com Streamlit + Plotly · Dados agregados de COVID-19 (snapshot único, "
    "não representa série temporal) · Ver README.md para metodologia e limitações."
)
