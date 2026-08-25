"""
Phase 3 - Dashboard Streamlit (Melissa)

Lancer avec : streamlit run src/dashboard/app.py

Pages :
- Overview : KPIs + graphique temporel des connexions/anomalies
- Anomalies : table filtrable + repartition par type + heatmap heure x jour
- Utilisateur : drill-down sur un utilisateur (timeline vs baseline)
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = "data/processed/logs_scored.csv"

st.set_page_config(
    page_title="Detection d'Acces Frauduleux",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Palette --------------------------------------------------------------
BG = "#0a0e1a"
CARD_BG = "rgba(255,255,255,0.035)"
CARD_BORDER = "rgba(255,255,255,0.08)"
TEXT_MAIN = "#f1f5f9"
TEXT_MUTED = "#8b93a7"
VIOLET = "#8b5cf6"
BLUE = "#3b82f6"
ROSE = "#f43f5e"
AMBER = "#f59e0b"
EMERALD = "#10b981"
GRID_COLOR = "rgba(255,255,255,0.06)"

CHART_PALETTE = [VIOLET, BLUE, "#06b6d4", AMBER, EMERALD]


def inject_custom_css():
    # IMPORTANT : aucune indentation dans ce bloc. Streamlit passe le contenu de
    # st.markdown par un parseur Markdown avant le rendu HTML, et Markdown traite
    # tout texte indente de 4 espaces ou plus comme un bloc de code -> si on indente
    # les lignes CSS ici, elles s'affichent en texte brut au lieu d'etre appliquees.
    css = (
"<link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">"
"<link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap\" rel=\"stylesheet\">"
"<style>"
"html, body, [class*=\"css\"] { font-family: 'Inter', -apple-system, sans-serif; }"
f".stApp {{ background: radial-gradient(circle at 15% 0%, #131a2e 0%, {BG} 45%) fixed; }}"
"[data-testid=\"stHeader\"] { background: transparent; }"
f"section[data-testid=\"stSidebar\"] {{ background: #0c1120; border-right: 1px solid {CARD_BORDER}; }}"
"section[data-testid=\"stSidebar\"] .stRadio label { font-size: 0.95rem; }"
f"h1, h2, h3, h4, p, span, label, div {{ color: {TEXT_MAIN}; }}"
f"hr {{ border-color: {CARD_BORDER} !important; margin: 1.1rem 0 1.6rem 0 !important; }}"
".brand { display: flex; align-items: center; gap: 10px; padding: 4px 0 18px 0; }"
f".brand-badge {{ width: 38px; height: 38px; border-radius: 11px; background: linear-gradient(135deg, {VIOLET}, {BLUE}); display: flex; align-items: center; justify-content: center; font-size: 13px; font-weight: 800; letter-spacing: 0.02em; color: white; box-shadow: 0 4px 14px rgba(139,92,246,0.35); }}"
".brand-text { font-weight: 700; font-size: 1.02rem; line-height: 1.1; }"
f".brand-sub {{ color: {TEXT_MUTED}; font-size: 0.72rem; letter-spacing: 0.04em; text-transform: uppercase; }}"
f".page-eyebrow {{ color: {VIOLET}; font-size: 0.78rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2px; }}"
".page-title { font-size: 2.1rem; font-weight: 800; letter-spacing: -0.02em; margin: 0 0 2px 0; background: linear-gradient(90deg, #ffffff, #c7cdea 120%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }"
f".page-subtitle {{ color: {TEXT_MUTED}; font-size: 0.98rem; margin-top: 0; }}"
f".kpi-card {{ background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-top: 3px solid transparent; border-radius: 14px; padding: 20px 22px; backdrop-filter: blur(6px); transition: all 0.18s ease; height: 100%; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }}"
".kpi-card:hover { transform: translateY(-2px); box-shadow: 0 12px 28px rgba(0,0,0,0.35); }"
f".kpi-label {{ color: {TEXT_MUTED}; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 6px; }}"
".kpi-value { font-size: 2rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1; }"
".kpi-delta { font-size: 0.82rem; font-weight: 600; margin-top: 8px; }"
f".kpi-delta.up {{ color: {ROSE}; }}"
f".kpi-delta.neutral {{ color: {TEXT_MUTED}; }}"
f".section-card {{ background: {CARD_BG}; border: 1px solid {CARD_BORDER}; border-radius: 16px; padding: 20px 22px 6px 22px; backdrop-filter: blur(6px); margin-bottom: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.2); }}"
f".section-title {{ font-weight: 700; font-size: 1.02rem; margin-bottom: 14px; padding-left: 12px; border-left: 3px solid {VIOLET}; }}"
f"[data-testid=\"stDataFrame\"] {{ border-radius: 12px; overflow: hidden; border: 1px solid {CARD_BORDER}; }}"
f".stButton button, .stDownloadButton button {{ background: linear-gradient(135deg, {VIOLET}, {BLUE}); color: white; border: none; border-radius: 10px; font-weight: 600; padding: 0.5rem 1.1rem; transition: all 0.15s ease; box-shadow: 0 4px 14px rgba(139,92,246,0.25); }}"
".stButton button:hover, .stDownloadButton button:hover { transform: translateY(-1px); box-shadow: 0 6px 18px rgba(139,92,246,0.4); }"
f".stMultiSelect [data-baseweb=\"tag\"] {{ background: linear-gradient(135deg, {VIOLET}, {BLUE}); }}"
"[data-testid=\"stMainBlockContainer\"] { padding-top: 2.2rem; padding-bottom: 3rem; }"
"section[data-testid=\"stSidebar\"] .stRadio > div { gap: 4px; }"
"section[data-testid=\"stSidebar\"] .stRadio > div > label { padding: 8px 10px; border-radius: 10px; transition: background 0.15s ease; }"
"section[data-testid=\"stSidebar\"] .stRadio > div > label:hover { background: rgba(255,255,255,0.05); }"
"::-webkit-scrollbar { width: 8px; height: 8px; }"
"::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.15); border-radius: 8px; }"
"</style>"
    )
    st.markdown(css, unsafe_allow_html=True)


@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df["date"] = df["timestamp"].dt.date
    return df


def page_header(eyebrow: str, title: str, subtitle: str = ""):
    # pas d'indentation dans le HTML (voir commentaire dans inject_custom_css)
    html = (
        f'<div class="page-eyebrow">{eyebrow}</div>'
        f'<div class="page-title">{title}</div>'
        f'<div class="page-subtitle">{subtitle}</div>'
        f'<div style="height:22px"></div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str = "", delta_kind: str = "neutral", accent: str = BLUE):
    delta_html = f'<div class="kpi-delta {delta_kind}">{delta}</div>' if delta else ""
    html = (
        f'<div class="kpi-card" style="border-top-color:{accent}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'{delta_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_start(title: str):
    st.markdown(f'<div class="section-card"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_end():
    st.markdown("</div>", unsafe_allow_html=True)


def style_fig(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT_MUTED, size=12),
        margin=dict(t=10, b=10, l=10, r=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False)
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False)
    return fig


def page_overview(df: pd.DataFrame):
    page_header("Systeme de detection", "Vue d'ensemble", "Synthese globale de l'activite et des anomalies detectees")

    total_connexions = len(df)
    total_anomalies = int(df["is_anomaly"].sum())
    taux_anomalies = total_anomalies / total_connexions if total_connexions else 0
    nb_users = df["user_id"].nunique()
    derniere_date = df["date"].max()
    anomalies_dernier_jour = int(df[df["date"] == derniere_date]["is_anomaly"].sum())

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        kpi_card("Connexions totales", f"{total_connexions:,}".replace(",", " "), accent=BLUE)
    with col2:
        kpi_card("Taux d'anomalies", f"{taux_anomalies:.1%}", f"+{total_anomalies} au total", "up", accent=ROSE)
    with col3:
        kpi_card("Utilisateurs suivis", f"{nb_users}", accent=VIOLET)
    with col4:
        kpi_card("Alertes (dernier jour)", f"{anomalies_dernier_jour}", accent=AMBER)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    section_start("Evolution des connexions dans le temps")
    daily = df.groupby("date").agg(
        total=("user_id", "count"),
        anomalies=("is_anomaly", "sum"),
    ).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["total"], name="Connexions totales",
        line=dict(color=BLUE, width=2.5), fill="tozeroy",
        fillcolor="rgba(59,130,246,0.12)",
    ))
    fig.add_trace(go.Scatter(
        x=daily["date"], y=daily["anomalies"], name="Anomalies",
        line=dict(color=ROSE, width=2.5),
    ))
    st.plotly_chart(style_fig(fig, 380), use_container_width=True)
    section_end()

    col_a, col_b = st.columns(2)
    with col_a:
        section_start("Repartition par source")
        source_counts = df["source"].value_counts().reset_index()
        source_counts.columns = ["source", "count"]
        fig2 = px.pie(source_counts, names="source", values="count", hole=0.62,
                      color_discrete_sequence=CHART_PALETTE)
        fig2.update_traces(textfont=dict(color=TEXT_MAIN))
        st.plotly_chart(style_fig(fig2, 300), use_container_width=True)
        section_end()

    with col_b:
        section_start("Methodes de detection")
        detected = df[df["is_anomaly"] == 1]["detected_by"].value_counts().reset_index()
        detected.columns = ["methode(s)", "count"]
        fig3 = px.bar(detected, x="count", y="methode(s)", orientation="h",
                      color_discrete_sequence=[VIOLET])
        fig3.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig3, 300), use_container_width=True)
        section_end()


def page_anomalies(df: pd.DataFrame):
    page_header("Investigation", "Anomalies detectees", "Explore et filtre les acces suspects")

    with st.sidebar:
        st.markdown("### Filtres")
        types = sorted([t for t in df["anomaly_type"].dropna().unique()])
        selected_types = st.multiselect("Type d'anomalie", types, default=types)
        date_range = st.date_input("Periode", value=(df["date"].min(), df["date"].max()))
        min_score = st.slider("Score minimum", 0.0, 1.0, 0.0, 0.33)

    anomalies = df[df["is_anomaly"] == 1].copy()
    if selected_types:
        anomalies = anomalies[anomalies["anomaly_type"].isin(selected_types)]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        anomalies = anomalies[
            (anomalies["date"] >= date_range[0]) & (anomalies["date"] <= date_range[1])
        ]
    anomalies = anomalies[anomalies["anomaly_score"] >= min_score]

    kpi_card("Anomalies filtrees", f"{len(anomalies)}", accent=ROSE)
    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section_start("Repartition par type")
        type_counts = anomalies["anomaly_type"].value_counts().reset_index()
        type_counts.columns = ["type", "count"]
        fig = px.bar(type_counts, x="type", y="count", color_discrete_sequence=[ROSE])
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(style_fig(fig, 300), use_container_width=True)
        section_end()

    with col_b:
        section_start("Heure x jour de la semaine")
        jours = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        heat = anomalies.groupby(["day_of_week", "hour_of_day"]).size().reset_index(name="count")
        pivot = heat.pivot(index="day_of_week", columns="hour_of_day", values="count").fillna(0)
        pivot = pivot.reindex(range(7))
        fig2 = px.imshow(
            pivot, labels=dict(x="Heure", y="Jour", color="Anomalies"),
            y=[jours[i] for i in pivot.index],
            color_continuous_scale=["#131a2e", VIOLET, ROSE],
        )
        st.plotly_chart(style_fig(fig2, 300), use_container_width=True)
        section_end()

    section_start(f"Detail ({len(anomalies)} lignes)")
    display_cols = [
        "timestamp", "user_id", "source", "country", "city", "status",
        "anomaly_type", "anomaly_score", "detected_by",
    ]
    st.dataframe(
        anomalies[display_cols].sort_values("timestamp", ascending=False),
        use_container_width=True,
        height=380,
    )
    csv = anomalies[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Telecharger en CSV", csv, "anomalies_filtrees.csv", "text/csv")
    section_end()


def page_user_drilldown(df: pd.DataFrame):
    page_header("Profil", "Analyse par utilisateur", "Comportement individuel compare a la baseline habituelle")

    users = sorted(df["user_id"].unique())
    default_index = 0
    users_with_anomalies = df[df["is_anomaly"] == 1]["user_id"].value_counts()
    if len(users_with_anomalies) > 0:
        default_user = users_with_anomalies.index[0]
        default_index = users.index(default_user)

    selected_user = st.selectbox("Choisir un utilisateur", users, index=default_index)
    user_df = df[df["user_id"] == selected_user].sort_values("timestamp")

    col1, col2, col3 = st.columns(3)
    with col1:
        kpi_card("Connexions", f"{len(user_df)}", accent=BLUE)
    with col2:
        kpi_card("Anomalies", f"{int(user_df['is_anomaly'].sum())}", accent=ROSE)
    with col3:
        kpi_card("Pays habituel", user_df["usual_country"].iloc[0] if len(user_df) else "-", accent=VIOLET)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    section_start("Timeline des connexions")
    fig = px.scatter(
        user_df, x="timestamp", y="hour_of_day",
        color=user_df["is_anomaly"].map({0: "Normal", 1: "Anomalie"}),
        color_discrete_map={"Normal": BLUE, "Anomalie": ROSE},
        hover_data=["source", "country", "status", "anomaly_type"],
    )
    fig.update_traces(marker=dict(size=9, line=dict(width=0)))
    st.plotly_chart(style_fig(fig, 380), use_container_width=True)
    section_end()

    if user_df["is_anomaly"].sum() > 0:
        section_start("Anomalies de cet utilisateur")
        st.dataframe(
            user_df[user_df["is_anomaly"] == 1][
                ["timestamp", "source", "country", "status", "anomaly_type", "detected_by"]
            ],
            use_container_width=True,
        )
        section_end()


def main():
    inject_custom_css()
    df = load_data()

    with st.sidebar:
        brand_html = (
            '<div class="brand">'
            '<div class="brand-badge">DF</div>'
            '<div>'
            '<div class="brand-text">Detection Fraude</div>'
            '<div class="brand-sub">Access monitoring</div>'
            '</div>'
            '</div>'
        )
        st.markdown(brand_html, unsafe_allow_html=True)
        page = st.radio(
            "Navigation", ["Overview", "Anomalies", "Utilisateur"],
            label_visibility="collapsed",
        )
        st.markdown("---")

    if page == "Overview":
        page_overview(df)
    elif page == "Anomalies":
        page_anomalies(df)
    else:
        page_user_drilldown(df)


if __name__ == "__main__":
    main()