import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ----------------------------------------------------------------------------
# CONFIGURATION GENERALE
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Dégradation des Terres & Sécheresse — Maroc",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_DIR = Path(__file__).parent / "data"

# Palette neutre, sobre, adaptée à un comité (pas de couleurs criardes)
PALETTE = {
    "bg": "#F7F6F3",
    "card": "#FFFFFF",
    "ink": "#2B2B2B",
    "muted": "#6B6B6B",
    "accent": "#4C6B58",       # vert olive sourdine
    "accent2": "#8C7851",      # sable/bronze
    "line": "#E3E1DC",
    "degraded": "#B5654A",     # terracotta
    "stable": "#B8A98A",       # sable
    "improved": "#4C6B58",     # vert olive
}


def icon_svg(name: str, color: str | None = None, size: int = 20) -> str:
    color = color or PALETTE["accent"]
    icons = {
        "earth": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <circle cx="12" cy="12" r="9" stroke="{color}" stroke-width="1.8"/>
          <path d="M3 12H21M12 3C14.5 5.7 15.8 8.8 15.8 12C15.8 15.2 14.5 18.3 12 21C9.5 18.3 8.2 15.2 8.2 12C8.2 8.8 9.5 5.7 12 3Z" stroke="{color}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        """,
        "filter": """
        <svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path d="M4 6H20L14 12.8V18L10 20V12.8L4 6Z" stroke="{color}" stroke-width="1.8" stroke-linejoin="round"/>
        </svg>
        """,
    }
    return icons.get(name, icons["earth"]).format(size=size, color=color)


CUSTOM_CSS = f"""
<style>
    .stApp {{
        background: radial-gradient(circle at top left, rgba(76, 107, 88, 0.08), transparent 28%), linear-gradient(180deg, #faf8f4 0%, {PALETTE['bg']} 22%, #f3f0ea 100%);
    }}
    .block-container {{
        padding-top: 1.4rem;
        padding-bottom: 2rem;
    }}
    h1, h2, h3, h4 {{
        color: {PALETTE['ink']};
        font-family: 'Aptos', 'Segoe UI', sans-serif;
    }}
    div[data-testid="stMetric"] {{
        background-color: {PALETTE['card']};
        border: 1px solid {PALETTE['line']};
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 12px 30px rgba(43, 43, 43, 0.05);
    }}
    div[data-testid="stMetricLabel"] {{
        color: {PALETTE['muted']};
        font-size: 0.86rem;
    }}
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #efe9dd 0%, #f7f4ed 100%);
        border-right: 1px solid {PALETTE['line']};
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 1rem;
    }}
    .hero-shell {{
        background: linear-gradient(135deg, rgba(43, 43, 43, 0.97), rgba(76, 107, 88, 0.96));
        color: white;
        border-radius: 28px;
        padding: 1.6rem 1.7rem 1.4rem 1.7rem;
        margin-bottom: 1rem;
        box-shadow: 0 20px 40px rgba(43, 43, 43, 0.18);
    }}
    .hero-kicker {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.12);
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}
    .hero-title {{
        margin: 0.55rem 0 0.35rem 0;
        font-size: 2.2rem;
        line-height: 1.08;
        font-weight: 800;
        letter-spacing: -0.03em;
        color: white;
    }}
    .hero-subtitle {{
        margin: 0;
        max-width: 68rem;
        color: rgba(255, 255, 255, 0.84);
        font-size: 1rem;
    }}
    .hero-meta {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 1rem;
    }}
    .hero-meta span {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.38rem 0.7rem;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.13);
        color: rgba(255, 255, 255, 0.92);
        font-size: 0.84rem;
        border: 1px solid rgba(255, 255, 255, 0.12);
    }}
    .section-eyebrow {{
        display: inline-block;
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {PALETTE['accent']};
        margin-bottom: 0.4rem;
    }}
    .card-note {{
        background-color: {PALETTE['card']};
        border: 1px solid {PALETTE['line']};
        border-radius: 16px;
        padding: 10px 14px;
        color: {PALETTE['muted']};
        font-size: 0.85rem;
    }}
    .insight-grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.85rem;
        margin: 0.9rem 0 1.1rem 0;
    }}
    .insight-card {{
        background: {PALETTE['card']};
        border: 1px solid {PALETTE['line']};
        border-radius: 20px;
        padding: 1rem 1rem 0.95rem 1rem;
        box-shadow: 0 12px 26px rgba(43, 43, 43, 0.04);
    }}
    .insight-card .label {{
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: {PALETTE['muted']};
        margin-bottom: 0.35rem;
    }}
    .insight-card h3 {{
        margin: 0;
        font-size: 1.15rem;
        line-height: 1.2;
    }}
    .insight-card p {{
        margin: 0.45rem 0 0 0;
        color: {PALETTE['muted']};
        font-size: 0.92rem;
        line-height: 1.5;
    }}
    .page-title {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.15rem;
        font-weight: 700;
        color: {PALETTE['ink']};
    }}
    .section-title {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0.4rem 0 0.6rem 0;
        font-weight: 600;
        color: {PALETTE['ink']};
    }}
    .icon-inline {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        vertical-align: middle;
    }}
    .summary-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.35rem 0.7rem;
        border-radius: 999px;
        border: 1px solid {PALETTE['line']};
        background: rgba(255, 255, 255, 0.74);
        color: {PALETTE['muted']};
        font-size: 0.83rem;
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

DROUGHT_COLORS = {
    "No drought": "#A9BFAE",
    "Mild": "#D8C79A",
    "Moderate": "#CE9B5C",
    "Severe": "#B5654A",
    "Extreme": "#7A3B2E",
}

STATUS_EXP_COLORS = {
    "Persistent degradation": "#7A3B2E",
    "Recent degradation": "#B5654A",
    "Baseline degradation": "#D9A28A",
    "Stability": "#B8A98A",
    "Baseline improvement": "#B7C9AE",
    "Recent improvement": "#7FA189",
    "Persistent improvement": "#4C6B58",
}

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=PALETTE["card"],
        plot_bgcolor=PALETTE["card"],
        font=dict(color=PALETTE["ink"], family="Aptos, Segoe UI, sans-serif"),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
)


def format_int(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def format_pct(value: float) -> str:
    return f"{value:.1f}%"


def build_region_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.pivot_table(index="region", columns="class", values="pct", aggfunc="sum", fill_value=0)
        .reset_index()
        .rename_axis(None, axis=1)
    )
    for column in ["Degraded", "Stable", "Improved"]:
        if column not in summary:
            summary[column] = 0.0
    summary["net_balance"] = summary["Improved"] - summary["Degraded"]
    return summary.sort_values("Degraded", ascending=False).reset_index(drop=True)


def build_drought_risk(df: pd.DataFrame, year: int) -> pd.DataFrame:
    current_year = df[df["year"] == year].copy()
    current_year["severe_extreme"] = current_year["pct"].where(
        current_year["class"].isin(["Severe", "Extreme"]), 0
    )
    grouped = current_year.groupby("region", as_index=False).agg(
        severe_extreme=("severe_extreme", "sum")
    )
    return grouped.sort_values(by="severe_extreme", ascending=False).reset_index(
        drop=True
    )


# ----------------------------------------------------------------------------
# CHARGEMENT DES DONNEES
# ----------------------------------------------------------------------------
@st.cache_data
def load_data():
    status = pd.read_csv(DATA_DIR / "status_by_region.csv")
    status_exp = pd.read_csv(DATA_DIR / "status_expanded_by_region.csv")
    subind = pd.read_csv(DATA_DIR / "sdg1531_subindicators_by_region.csv")
    pop_deg = pd.read_csv(DATA_DIR / "so2_3_population_exposure.csv")
    drought_land = pd.read_csv(DATA_DIR / "so3_1_drought_land_proportion.csv")
    drought_pop = pd.read_csv(DATA_DIR / "so3_2_drought_population_exposure.csv")
    dvi = pd.read_csv(DATA_DIR / "so3_3_dvi_rebuilt.csv")
    with open(DATA_DIR / "morocco_regions_12.geojson", encoding="utf-8") as f:
        geo = json.load(f)
    return status, status_exp, subind, pop_deg, drought_land, drought_pop, dvi, geo


status, status_exp, subind, pop_deg, drought_land, drought_pop, dvi, geo = load_data()

REGIONS = sorted(status["region"].unique())
YEARS = sorted(drought_land["year"].unique())

# ----------------------------------------------------------------------------
# PARAMETRES ET SYNTHESE
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="section-eyebrow">Comité de pilotage</div>
        <h3 style="margin: 0.1rem 0 0.35rem 0;">Périmètre d'analyse</h3>
        <p style="margin: 0 0 0.9rem 0; color: #6b6b6b; font-size: 0.92rem; line-height: 1.45;">
        Ciblez les régions et l'année pour aligner la lecture avec le dossier soumis au comité.
        </p>
        """,
        unsafe_allow_html=True,
    )
    selected_regions = st.multiselect(
        "Régions", options=REGIONS, default=REGIONS, key="region_filter"
    )
    selected_year = int(
        st.slider(
            "Année (sécheresse)",
            min_value=int(min(YEARS)),
            max_value=int(max(YEARS)),
            value=int(YEARS[-1]),
            step=1,
            key="year_filter",
        )
    )
    if not selected_regions:
        selected_regions = REGIONS

    st.markdown("---")
    st.markdown("##### Périmètre actif")
    st.markdown(
        f'<div class="summary-pill">Régions sélectionnées: {len(selected_regions)} / {len(REGIONS)}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="summary-pill" style="margin-top:0.45rem;">Année sécheresse: {selected_year}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown("##### Lecture rapide")
    st.caption("Le tableau de bord commence par une synthèse exécutive, puis ouvre les détails par thème.")

# Filtrage
status_f = status[status["region"].isin(selected_regions)]
status_exp_f = status_exp[status_exp["region"].isin(selected_regions)]
pop_deg_f = pop_deg[pop_deg["region"].isin(selected_regions)]
drought_land_selected = drought_land[drought_land["region"].isin(selected_regions)]
drought_land_f = drought_land_selected[drought_land_selected["year"] == selected_year]
drought_pop_f = drought_pop[drought_pop["region"].isin(selected_regions)]

region_summary = build_region_summary(status_f)
drought_risk = build_drought_risk(drought_land_selected, selected_year)

degraded_area = status_f.loc[status_f["class"] == "Degraded", "area_ha"].sum()
total_area = status_f["area_ha"].sum()
pct_degraded = (degraded_area / total_area * 100) if total_area else 0

improved_area = status_f.loc[status_f["class"] == "Improved", "area_ha"].sum()
pct_improved = (improved_area / total_area * 100) if total_area else 0

pop_exposed = pop_deg_f.loc[pop_deg_f["class"] == "Degraded", "total"].sum()

severe_extreme = drought_land_f[drought_land_f["class"].isin(["Severe", "Extreme"])]
pct_severe_drought = (
    severe_extreme["pct"].sum() / len(selected_regions) if selected_regions else 0
)

top_degraded_region = region_summary.iloc[0]
top_resilience_region = region_summary.sort_values("net_balance", ascending=False).iloc[0]
top_drought_region = drought_risk.iloc[0]

st.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-kicker">Maroc | SDG 15.3.1 | usage comité</div>
        <div class="hero-title">Dégradation des terres & vulnérabilité à la sécheresse</div>
        <p class="hero-subtitle">
        Lecture synthétique des pressions territoriales, de l'exposition climatique et de la vulnérabilité humaine,
        pensée pour une présentation devant les décideurs.
        </p>
        <div class="hero-meta">
            <span>Régions actives: {len(selected_regions)} / {len(REGIONS)}</span>
            <span>Année sécheresse: {selected_year}</span>
            <span>Référentiel: HCP / Trends.Earth / SDG 15.3.1</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

summary_col_1, summary_col_2, summary_col_3, summary_col_4 = st.columns(4)
summary_col_1.metric(
    "Terres dégradées",
    f"{pct_degraded:.1f}%",
    help="Part de la superficie totale classée « Dégradée »",
)
summary_col_2.metric(
    "Terres améliorées",
    f"{pct_improved:.1f}%",
    help="Part de la superficie totale classée « Améliorée »",
)
summary_col_3.metric(
    "Population exposée",
    format_int(pop_exposed),
    help="Population exposée sur les terres dégradées",
)
summary_col_4.metric(
    "Sécheresse sévère/extrême",
    f"{pct_severe_drought:.1f}%",
    help=f"Moyenne régionale pour l'année {selected_year}",
)

st.markdown(
    f"""
    <div class="insight-grid">
        <div class="insight-card">
            <div class="label">Signal territorial</div>
            <h3>{top_degraded_region['region']}</h3>
            <p>{format_pct(float(top_degraded_region['Degraded']))} des terres y sont classées dégradées, ce qui en fait la priorité principale du périmètre sélectionné.</p>
        </div>
        <div class="insight-card">
            <div class="label">Marge de redressement</div>
            <h3>{top_resilience_region['region']}</h3>
            <p>Le solde amélioration - dégradation est le plus favorable dans cette région: {format_pct(float(top_resilience_region['net_balance']))}.</p>
        </div>
        <div class="insight-card">
            <div class="label">Pression climatique</div>
            <h3>{top_drought_region['region']}</h3>
            <p>La sécheresse sévère et extrême y atteint {format_pct(float(top_drought_region['severe_extreme']))} pour l'année {selected_year}.</p>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# ONGLET NAVIGATION
# ----------------------------------------------------------------------------
tab_synthese, tab_carte, tab_degradation, tab_secheresse, tab_population, tab_dvi = st.tabs(
    ["Synthèse exécutive", "Carte régionale", "Dégradation", "Sécheresse", "Population", "Vulnérabilité (DVI)"]
)

with tab_synthese:
    st.markdown("### Synthèse exécutive")
    st.caption("Vue de haut niveau pour une lecture rapide avant de passer aux détails techniques.")

    synth_col_1, synth_col_2 = st.columns([1, 1.2])

    with synth_col_1:
        status_totals = status_f.groupby("class", as_index=False)["pct"].sum()
        fig_status_mix = px.pie(
            status_totals,
            names="class",
            values="pct",
            hole=0.6,
            color="class",
            color_discrete_map={"Degraded": PALETTE["degraded"], "Stable": PALETTE["stable"], "Improved": PALETTE["improved"]},
        )
        fig_status_mix.update_traces(textinfo="percent+label", sort=False, marker=dict(line=dict(color="white", width=1)))
        fig_status_mix.update_layout(template=PLOTLY_TEMPLATE, height=390, legend_title="")
        st.plotly_chart(fig_status_mix, use_container_width=True)

    with synth_col_2:
        st.markdown("##### Régions prioritaires")
        priority = region_summary.sort_values("Degraded", ascending=False).head(5).copy()
        priority = priority.rename(
            columns={
                "region": "Région",
                "Degraded": "Dégradé",
                "Stable": "Stable",
                "Improved": "Amélioré",
                "net_balance": "Solde",
            }
        )
        for column in ["Dégradé", "Stable", "Amélioré", "Solde"]:
            priority[column] = priority[column].map(format_pct)
        st.dataframe(priority, use_container_width=True, hide_index=True)
        st.markdown(
            '<div class="card-note">Le classement combine la pression en terres dégradées, la stabilité et le potentiel d’amélioration pour orienter les priorités d’action.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("##### Pression sévère et extrême par région")
    drought_priority = drought_risk.sort_values("severe_extreme", ascending=True).tail(min(8, len(drought_risk)))
    fig_drought_priority = px.bar(
        drought_priority,
        x="severe_extreme",
        y="region",
        orientation="h",
        color="severe_extreme",
        color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
        labels={"severe_extreme": "% sévère/extrême", "region": ""},
    )
    fig_drought_priority.update_layout(template=PLOTLY_TEMPLATE, height=360, coloraxis_showscale=False, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_drought_priority, use_container_width=True)

# ----------------------------------------------------------------------------
# ONGLET 1 — CARTE
# ----------------------------------------------------------------------------
with tab_carte:
    st.markdown("### Répartition régionale des terres dégradées")
    col_map, col_side = st.columns([2, 1])

    map_df = status_f[status_f["class"] == "Degraded"][["region", "pct", "area_ha"]]

    with col_map:
        fig_map = px.choropleth_map(
            map_df,
            geojson=geo,
            locations="region",
            featureidkey="properties.region",
            color="pct",
            color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
            map_style="carto-positron",
            zoom=4,
            center={"lat": 29.5, "lon": -8.5},
            opacity=0.85,
            labels={"pct": "% dégradé"},
            hover_data={"area_ha": ":.0f"},
        )
        fig_map.update_layout(template=PLOTLY_TEMPLATE, height=520, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_map, use_container_width=True)

    with col_side:
        st.markdown("##### Classement des régions")
        rank = map_df.sort_values("pct", ascending=False).reset_index(drop=True)
        fig_rank = px.bar(
            rank,
            x="pct",
            y="region",
            orientation="h",
            color="pct",
            color_continuous_scale=[PALETTE["stable"], PALETTE["degraded"]],
            labels={"pct": "% dégradé", "region": ""},
        )
        fig_rank.update_layout(
            template=PLOTLY_TEMPLATE,
            height=520,
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_rank, use_container_width=True)

# ----------------------------------------------------------------------------
# ONGLET 2 — DEGRADATION
# ----------------------------------------------------------------------------
with tab_degradation:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### État détaillé par région (statut étendu)")
        fig_stack = px.bar(
            status_exp_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map=STATUS_EXP_COLORS,
            labels={"pct": "% de la superficie", "region": "", "class": "Statut"},
        )
        fig_stack.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_stack, use_container_width=True)

    with c2:
        st.markdown("##### Sous-indicateurs SDG 15.3.1 (productivité, couverture, carbone)")
        indicators = sorted(subind["indicator"].unique())
        sel_ind = st.selectbox("Choisir un sous-indicateur", indicators)
        sub_f = subind[
            (subind["indicator"] == sel_ind) & (subind["region"].isin(selected_regions))
        ]
        fig_sub = px.bar(
            sub_f,
            x="region",
            y="pct",
            color="class",
            color_discrete_map={"Degraded": PALETTE["degraded"], "Stable": PALETTE["stable"], "Improved": PALETTE["improved"]},
            labels={"pct": "% de la superficie", "region": "", "class": "Classe"},
        )
        fig_sub.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_sub, use_container_width=True)

    st.markdown("##### Vue synthétique (Statut global)")
    fig_status = px.bar(
        status_f,
        x="region",
        y="pct",
        color="class",
        color_discrete_map={"Degraded": PALETTE["degraded"], "Stable": PALETTE["stable"], "Improved": PALETTE["improved"]},
        barmode="group",
        labels={"pct": "% de la superficie", "region": "", "class": "Classe"},
    )
    fig_status.update_layout(template=PLOTLY_TEMPLATE, height=420, xaxis_tickangle=-35, legend_title="")
    st.plotly_chart(fig_status, use_container_width=True)

# ----------------------------------------------------------------------------
# ONGLET 3 — SECHERESSE
# ----------------------------------------------------------------------------
with tab_secheresse:
    st.markdown(f"##### Exposition à la sécheresse par région — {selected_year}")
    fig_drought = px.bar(
        drought_land_f,
        x="region",
        y="pct",
        color="class",
        color_discrete_map=DROUGHT_COLORS,
        category_orders={"class": ["No drought", "Mild", "Moderate", "Severe", "Extreme"]},
        labels={"pct": "% de la superficie", "region": "", "class": "Niveau"},
    )
    fig_drought.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_tickangle=-35, legend_title="")
    st.plotly_chart(fig_drought, use_container_width=True)

    st.markdown("##### Évolution temporelle (2020–2024)")
    dl_evol = drought_land[drought_land["region"].isin(selected_regions)]
    evol = dl_evol.groupby(["year", "class"], as_index=False)["pct"].mean()
    fig_evol = px.area(
        evol,
        x="year",
        y="pct",
        color="class",
        color_discrete_map=DROUGHT_COLORS,
        category_orders={"class": ["No drought", "Mild", "Moderate", "Severe", "Extreme"]},
        labels={"pct": "% moyen de la superficie", "year": "Année", "class": "Niveau"},
    )
    fig_evol.update_layout(template=PLOTLY_TEMPLATE, height=420, legend_title="")
    st.plotly_chart(fig_evol, use_container_width=True)

# ----------------------------------------------------------------------------
# ONGLET 4 — POPULATION
# ----------------------------------------------------------------------------
with tab_population:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("##### Population exposée aux terres dégradées")
        pop_plot = pop_deg_f[pop_deg_f["class"] == "Degraded"].sort_values("total", ascending=True)
        fig_pop = px.bar(
            pop_plot,
            x="total",
            y="region",
            orientation="h",
            color_discrete_sequence=[PALETTE["degraded"]],
            labels={"total": "Population (milliers)", "region": ""},
        )
        fig_pop.update_layout(template=PLOTLY_TEMPLATE, height=460)
        st.plotly_chart(fig_pop, use_container_width=True)

    with c2:
        st.markdown("##### Répartition Hommes / Femmes (terres dégradées)")
        gender = pop_deg_f[pop_deg_f["class"] == "Degraded"][["region", "pct_male", "pct_female"]].melt(
            id_vars="region", var_name="genre", value_name="pct"
        )
        gender["genre"] = gender["genre"].map({"pct_male": "Hommes", "pct_female": "Femmes"})
        fig_gender = px.bar(
            gender,
            x="region",
            y="pct",
            color="genre",
            barmode="group",
            color_discrete_map={"Hommes": PALETTE["accent2"], "Femmes": PALETTE["accent"]},
            labels={"pct": "% de la population exposée", "region": "", "genre": ""},
        )
        fig_gender.update_layout(template=PLOTLY_TEMPLATE, height=460, xaxis_tickangle=-35, legend_title="")
        st.plotly_chart(fig_gender, use_container_width=True)

    st.markdown("##### Population exposée à la sécheresse par région")
    fig_pop_drought = px.bar(
        drought_pop_f,
        x="region",
        y="total",
        color="class",
        color_discrete_map=DROUGHT_COLORS,
        category_orders={"class": ["No drought", "Mild", "Moderate", "Severe", "Extreme"]},
        labels={"total": "Population (milliers)", "region": "", "class": "Niveau"},
    )
    fig_pop_drought.update_layout(template=PLOTLY_TEMPLATE, height=440, xaxis_tickangle=-35, legend_title="")
    st.plotly_chart(fig_pop_drought, use_container_width=True)

# ----------------------------------------------------------------------------
# ONGLET 5 — DVI (comparaison internationale)
# ----------------------------------------------------------------------------
with tab_dvi:
    st.markdown("##### Indice de Vulnérabilité à la Sécheresse (DVI) — comparaison régionale (pays)")
    st.caption("Composite reconstruit (social, économique, infrastructurel) — indicateur SO3-3")

    dvi_sorted = dvi.sort_values("DVI", ascending=True)
    fig_dvi = px.bar(
        dvi_sorted,
        x="DVI",
        y="iso3",
        orientation="h",
        color="DVI",
        color_continuous_scale=[PALETTE["stable"], PALETTE["accent2"], PALETTE["degraded"]],
        labels={"DVI": "Indice DVI (0–1)", "iso3": "Pays"},
    )
    fig_dvi.update_layout(template=PLOTLY_TEMPLATE, height=380, coloraxis_showscale=False)
    st.plotly_chart(fig_dvi, use_container_width=True)

    st.markdown("##### Composantes du DVI")
    dvi_components = dvi.melt(
        id_vars=["iso3", "DVI"], value_vars=["social", "economic", "infrastructural"],
        var_name="composante", value_name="valeur"
    )
    dvi_components["composante"] = dvi_components["composante"].map(
        {"social": "Social", "economic": "Économique", "infrastructural": "Infrastructurel"}
    )
    fig_radar = px.line_polar(
        dvi_components,
        r="valeur",
        theta="composante",
        color="iso3",
        line_close=True,
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    fig_radar.update_layout(template=PLOTLY_TEMPLATE, height=460, legend_title="Pays")
    st.plotly_chart(fig_radar, use_container_width=True)

# ----------------------------------------------------------------------------
# PIED DE PAGE
# ----------------------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center; color:{PALETTE['muted']}; font-size:0.8rem;">
    <b>📚 Source</b><br>
    Indicateur SDG 15.3.1 / UNCCD SO2-SO3<br>
    Méthodologie Trends.Earth v2.2.6<br>
    Période de référence : 2001–2015<br>
    Période de suivi : 2016–2025<br><br>
    Dashboard généré pour usage interne — Comité de suivi SDG 15.3.1 · Données HCP / Trends.Earth<br>
    </div>
    """,
    unsafe_allow_html=True,
)
