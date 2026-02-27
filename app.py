"""
Urban Longevity - Streamlit Dashboard
Solving the Green Paradox: optimize tree planting to reduce PM2.5 without triggering pollen-induced asthma.
"""

import streamlit as st
import plotly.express as px
import pandas as pd
from pathlib import Path

# --- Page config ---
st.set_page_config(page_title="Urban Longevity", layout="wide")

# Base typography only (theme CSS injected in main from session state)
st.markdown(
    """<style>html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif !important; }</style>""",
    unsafe_allow_html=True,
)

# --- Paths ---
DATA_DIR = Path(__file__).resolve().parent
MASTER_CSV = DATA_DIR / "manhattan_master.csv"

# --- Mock recommendation logic (no live pollen DB) ---
def recommended_action(asthma_rate: float, median_asthma: float) -> str:
    if asthma_rate > median_asthma:
        return "High Risk: Plant strictly Low-Pollen female trees (e.g., Female Ginkgo or Red Maple)."
    return "Monitor: Safe for standard green infrastructure."


def recommended_tree(tree_count: int, median_trees: float) -> str:
    """Suggest species by spatial constraint: densely built (low tree count) vs open (high)."""
    if tree_count < median_trees:
        return "Japanese Zelkova"
    return "Northern Red Oak"


def main():
    # Theme: user-controlled toggle (default dark); key="dark_theme" is single source of truth
    with st.sidebar:
        st.toggle("Dark mode (Forest theme)", value=st.session_state.get("dark_theme", True), key="dark_theme")
        st.divider()

    # Inject theme CSS: Deep Forest Green (dark) / Soft White (light) + floating card look (15px radius, box-shadow)
    dark_css = """
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp { background-color: #002211 !important; }
    [data-testid="stSidebar"] { background-color: #001a0e !important; }
    p, span, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #E8F0EC !important; }
    h1, h2, h3, h4 { color: #FFFFFF !important; }
    .stPlotlyChart { border-radius: 15px !important; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.3); min-height: 480px; }
    [data-testid="stMetric"] { border-radius: 15px !important; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
    [data-testid="stExpander"] { border-radius: 15px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.15); }
    </style>
    """
    light_css = """
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stHeader"], .stApp { background-color: #F8F9FA !important; }
    [data-testid="stSidebar"] { background-color: #EEF0F2 !important; }
    p, span, label, [data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #333333 !important; }
    h1, h2, h3, h4 { color: #333333 !important; }
    .stPlotlyChart { border-radius: 15px !important; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.08); min-height: 480px; }
    [data-testid="stMetric"] { border-radius: 15px !important; box-shadow: 0 1px 4px rgba(0,0,0,0.06); }
    [data-testid="stExpander"] { border-radius: 15px !important; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    </style>
    """
    st.markdown(dark_css if st.session_state.get("dark_theme", True) else light_css, unsafe_allow_html=True)

    # Load data
    if not MASTER_CSV.exists():
        st.error(f"Master dataset not found: {MASTER_CSV}. Run `python data_prep.py` first.")
        return

    df = pd.read_csv(MASTER_CSV)
    df["zip"] = df["zip"].astype(int)
    median_asthma = df["asthma_rate_per_10k"].median()
    df["Recommended_Action"] = df["asthma_rate_per_10k"].apply(
        lambda r: recommended_action(r, median_asthma)
    )

    # Synthesized variance for demo: Need Index (fewer trees = higher need, 0–100)
    df["Need_Index"] = (1 - (df["tree_count"] / df["tree_count"].max())) * 100
    # Readable asthma %: rate per 10k → percentage (e.g. 1891 → 18.91%)
    df["asthma_pct"] = (df["asthma_rate_per_10k"] / 10000) * 100

    # --- Sidebar: Recommended Action logic + Data Insights ---
    with st.sidebar:
        st.subheader("Recommended Action logic")
        st.caption(
            "Recommendations are based on asthma rate vs. borough median. "
            "**Above median** → High Risk: plant low-pollen female trees (e.g., Female Ginkgo or Red Maple). "
            "**Below median** → Monitor: safe for standard green infrastructure."
        )
        st.divider()
        st.subheader("Legend")
        st.caption(
            "**Map color scale (Need Index)**  \n"
            "• **Dark green** → Low need  \n"
            "• **Neon green** → High need (fewer trees)"
        )
        st.divider()
        st.subheader("Data Insights")
        total_trees = int(df["tree_count"].sum())
        avg_pm25 = df["pm25"].mean()
        st.metric("Total Tree Count", f"{total_trees:,}")
        st.metric("Average PM2.5", f"{avg_pm25:.2f} mcg/m³")

    # --- Header ---
    st.title("Urban Longevity: Solving the Green Paradox")
    st.subheader(
        "Optimizing tree planting to reduce PM2.5 without triggering pollen-induced asthma. "
        "Use the map to identify high-risk zip codes and recommended actions."
    )

    # --- Metric cards row (centered) ---
    _, col1, col2, col3, _ = st.columns([0.25, 1, 1, 1, 0.25])
    with col1:
        st.metric("Total Trees", f"{int(df['tree_count'].sum()):,}")
    with col2:
        avg_asthma_pct = df["asthma_pct"].mean()
        st.metric("Avg Asthma", f"{avg_asthma_pct:.2f}%")
    with col3:
        high_need_zips = (df["Need_Index"] >= 50).sum()
        st.metric("High Need Zips", high_need_zips)

    st.divider()

    # Neon map scale: Dark Green (#002211) → Neon Green (#00ff88)
    color_scale = [[0, "#002211"], [0.4, "#004d33"], [0.7, "#00aa55"], [1, "#00ff88"]]
    map_style = "carto-darkmatter" if st.session_state.get("dark_theme", True) else "carto-positron"

    # --- Map container (hero) ---
    with st.container():
        st.markdown("#### Manhattan intervention need & risk")
        fig = px.scatter_mapbox(
            df,
            lat="latitude",
            lon="longitude",
            color="Need_Index",
            size="tree_count",
            color_continuous_scale=color_scale,
            size_max=30,
            mapbox_style=map_style,
            custom_data=["zip", "Need_Index", "pm25", "Recommended_Action"],
        )
        # Premium Hover Card: symmetric vertical clearance (3 br top/bottom), 5×&nbsp; bumpers, double br at header/data and pollution/action
        hovertemplate = (
            "<br><br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>ZIP CODE: %{customdata[0]}</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Urgency Index: <b>%{customdata[1]:.1f}%</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Health Baseline: <b>18.91%</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; PM2.5 Pollution: <b>%{customdata[2]:.2f} µg/m³</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br><br>"
            "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Action: <b>%{customdata[3]}</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<br><br><br>"
            "<extra></extra>"
        )
        fig.update_traces(hovertemplate=hovertemplate)
        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            coloraxis_colorbar_title="Need Index",
            height=600,
            hoverlabel=dict(
                bgcolor="rgba(0, 34, 17, 0.95)",
                bordercolor="rgba(0, 255, 136, 0.8)",
                font=dict(family="Inter, Arial, sans-serif", size=18, color="white"),
                align="left",
                namelength=0,
            ),
        )
        st.plotly_chart(fig, use_container_width=True, config={"scrollZoom": True})

    # --- Priority Intervention Table (sorted by Need_Index) ---
    median_trees = df["tree_count"].median()
    df["Recommended_Tree"] = df["tree_count"].apply(lambda c: recommended_tree(c, median_trees))

    tree_max = df["tree_count"].max()
    df["Tree_Planting_Progress"] = (df["tree_count"] / tree_max * 100).round(1)

    table_df = df[
        [
            "zip",
            "Need_Index",
            "pm25",
            "asthma_pct",
            "Recommended_Tree",
            "Tree_Planting_Progress",
            "tree_count",
            "Recommended_Action",
        ]
    ].copy()
    table_df = table_df.sort_values("Need_Index", ascending=False).reset_index(drop=True)
    table_df = table_df.rename(
        columns={
            "zip": "Zip Code",
            "pm25": "PM2.5 Baseline",
            "asthma_pct": "Asthma Rate (%)",
            "Recommended_Tree": "Recommended Tree",
            "Tree_Planting_Progress": "Tree Planting Progress",
            "tree_count": "Tree Count",
        }
    )

    with st.container():
        with st.expander("📋 Detailed Zip Code Analysis", expanded=False):
            st.dataframe(
                table_df,
                column_config={
                    "Zip Code": st.column_config.NumberColumn("Zip Code", format="%d"),
                    "Need_Index": st.column_config.NumberColumn("Need Index", format="%.1f%%"),
                    "PM2.5 Baseline": st.column_config.NumberColumn("PM2.5 Baseline", format="%.2f"),
                    "Asthma Rate (%)": st.column_config.NumberColumn(
                        "Asthma Rate (%)", format="%.2f%%", help="Asthma ED rate as % of population (per 10k scale)"
                    ),
                    "Recommended Tree": st.column_config.TextColumn("Recommended Tree"),
                    "Tree Planting Progress": st.column_config.ProgressColumn(
                        "Tree Planting Progress",
                        format="%.1f%%",
                        min_value=0,
                        max_value=100,
                    ),
                    "Tree Count": st.column_config.NumberColumn("Tree Count", format="%d"),
                    "Recommended_Action": st.column_config.TextColumn("Recommended Action"),
                },
                use_container_width=True,
                hide_index=True,
            )


if __name__ == "__main__":
    main()
