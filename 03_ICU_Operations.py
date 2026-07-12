"""
IP Operations Dashboard
-----------------------
UNIT DASHBOARD for the IP Operations incharge.
Opened from the Cluster Dashboard card, the sidebar, or another unit page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import load_master_data, filter_by_department
from utils import add_status_column, build_kpi_trend, build_department_trend, THEME
from config import DEPARTMENTS

st.set_page_config(
    page_title="Srikara Hospitals | IP Operations",
    page_icon="🛏️",
    layout="wide",
)

# ---------------------------------------------------------------------
# Sidebar: jump to the Cluster Dashboard or any other unit, from anywhere
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏥 Srikara Hospitals")
    st.page_link("Home.py", label="Cluster Dashboard", icon="🏠")
    st.markdown("**Unit Dashboards**")
    for dept in DEPARTMENTS:
        st.page_link(dept["page"], label=dept["name"], icon=dept["icon"])
    st.divider()
    st.caption("Data refreshes every 5 minutes.")

st.page_link("Home.py", label="← Back to Cluster Dashboard", icon="🏠")

st.title("🛏️ IP Operations — Unit Dashboard")
st.caption("Owner: IP Incharge")

# ---------------------------------------------------------------------
# Load data and keep only this department's rows
# ---------------------------------------------------------------------
master_df = load_master_data()
dept_df = filter_by_department(master_df, "IP Operations")

if dept_df.empty:
    st.warning("No KPI rows found for this department in the sheet yet.")
    st.stop()

dept_df = add_status_column(dept_df)

# ---------------------------------------------------------------------
# KPI summary cards
# ---------------------------------------------------------------------
on_track = int((dept_df["Status"] == "On Track").sum())
off_track = int((dept_df["Status"] == "Off Track").sum())
no_data = int((dept_df["Status"] == "No Data").sum())
measurable = on_track + off_track
health_score = round((on_track / measurable) * 100, 1) if measurable else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total KPIs", len(dept_df))
c2.metric("🟢 On Track", on_track)
c3.metric("🔴 Off Track", off_track)
c4.metric("⚪ Awaiting Data", no_data)
c5.metric("Health Score", f"{health_score}%")

st.divider()

tab_detail, tab_trend, tab_data = st.tabs(["🎯 KPI Detail", "📈 Trend", "📋 Full Data"])

# =======================================================================
# TAB — KPI DETAIL (gauge + donut + ranked bar + achievement cards)
# =======================================================================
with tab_detail:
    gauge_col, donut_col = st.columns(2)

    with gauge_col:
        st.markdown("#### Health Gauge")
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=health_score,
            number={"suffix": "%"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": THEME["primary"]},
                "steps": [
                    {"range": [0, 50], "color": "#fee2e2"},
                    {"range": [50, 80], "color": "#fef3c7"},
                    {"range": [80, 100], "color": "#dcfce7"},
                ],
            },
        ))
        gauge.update_layout(margin=dict(t=20, b=10, l=20, r=20), height=250)
        st.plotly_chart(gauge, use_container_width=True)

    with donut_col:
        st.markdown("#### Status Breakdown")
        status_counts = dept_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        donut = px.pie(
            status_counts, names="Status", values="Count", hole=0.55,
            color="Status", color_discrete_map=THEME,
        )
        donut.update_layout(margin=dict(t=20, b=10), height=250)
        st.plotly_chart(donut, use_container_width=True)

    st.divider()

    st.markdown("#### Achievement % by KPI (ranked)")
    ranked_df = dept_df.dropna(subset=["Achievement %"]).sort_values("Achievement %")
    if len(ranked_df):
        fig_rank = px.bar(
            ranked_df, x="Achievement %", y="Particulars", orientation="h",
            color="Status", color_discrete_map=THEME, text="Achievement %",
        )
        fig_rank.update_traces(texttemplate="%{text}%", textposition="outside")
        fig_rank.update_layout(margin=dict(t=10), height=max(250, 40 * len(ranked_df)))
        st.plotly_chart(fig_rank, use_container_width=True)
    else:
        st.info("No KPIs with a numeric target/achievement value yet.")

    st.divider()

    search = st.text_input("Search KPIs in IP Operations", placeholder="e.g. mortality, occupancy...")
    view_df = dept_df.copy()
    if search:
        view_df = view_df[view_df["Particulars"].str.contains(search, case=False, na=False)]

    if view_df.empty:
        st.info("No KPIs match your search.")
    else:
        for _, row in view_df.iterrows():
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"**{row['Particulars']}**")
                    st.caption(
                        f"Today: {row.get('Today', 'N/A')} • MTD: {row.get('MTD', 'N/A')} • "
                        f"Target: {row.get('Target', 'N/A')} • Last Month: {row.get('Last Month', 'N/A')}"
                    )
                    achievement = row.get("Achievement %")
                    if achievement is not None and pd.notna(achievement):
                        bar_value = max(0, min(int(achievement), 100))
                        st.progress(bar_value, text=f"{achievement}% of target")
                with col_b:
                    st.markdown(
                        f"<div style='text-align:center; font-size:1.8rem;'>{row['Status Icon']}</div>"
                        f"<div style='text-align:center; font-size:0.85rem; color:gray;'>{row['Status']}</div>",
                        unsafe_allow_html=True,
                    )

# =======================================================================
# TAB — TREND
# =======================================================================
with tab_trend:
    st.subheader("Department Trend: Last Month → MTD → Today")
    dept_trend = build_department_trend(dept_df)
    if len(dept_trend) >= 2:
        dept_trend["Period"] = pd.Categorical(dept_trend["Period"], ["Last Month", "MTD", "Today"], ordered=True)
        dept_trend = dept_trend.sort_values("Period")
        fig = px.area(dept_trend, x="Period", y="Total", markers=True)
        fig.update_traces(line_color=THEME["primary"], fillcolor="rgba(15,76,129,0.15)", line_width=3, marker_size=10)
        fig.update_layout(margin=dict(t=10))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough numeric data yet across Last Month / MTD / Today to plot a trend.")

    st.divider()
    st.subheader("Individual KPI Trends")
    for _, row in dept_df.iterrows():
        kpi_trend = build_kpi_trend(row)
        if len(kpi_trend) >= 2:
            with st.expander(row["Particulars"]):
                fig2 = px.bar(kpi_trend, x="Period", y="Value", text="Value")
                fig2.update_traces(marker_color=THEME["accent"])
                fig2.update_layout(margin=dict(t=10), height=280)
                st.plotly_chart(fig2, use_container_width=True)

# =======================================================================
# TAB — FULL DATA
# =======================================================================
with tab_data:
    display_cols = ["Particulars", "Today", "MTD", "Target", "Last Month",
                     "Achievement %", "Status Icon", "Status"]
    display_cols = [c for c in display_cols if c in dept_df.columns]
    st.dataframe(dept_df[display_cols], use_container_width=True, hide_index=True)

    csv_bytes = dept_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download this department's data as CSV",
        data=csv_bytes,
        file_name="ip_operations.csv",
        mime="text/csv",
    )
