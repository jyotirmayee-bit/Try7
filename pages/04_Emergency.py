"""
Emergency Dashboard
-------------------
UNIT DASHBOARD for the Emergency incharge.
Opened from the Cluster Dashboard card, the sidebar, or another unit page.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_master_data, filter_by_department
from utils import add_status_column, build_kpi_trend, build_department_trend, THEME
from config import DEPARTMENTS

st.set_page_config(
    page_title="Srikara Hospitals | Emergency",
    page_icon="🚑",
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

st.title("🚑 Emergency — Unit Dashboard")
st.caption("Owner: ER")

# ---------------------------------------------------------------------
# Load data and keep only this department's rows
# ---------------------------------------------------------------------
master_df = load_master_data()
dept_df = filter_by_department(master_df, "Emergency")

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
# TAB — KPI DETAIL (achievement bars, one per KPI)
# =======================================================================
with tab_detail:
    search = st.text_input("Search KPIs in Emergency", placeholder="e.g. mortality, occupancy...")
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
        fig = px.line(dept_trend, x="Period", y="Total", markers=True)
        fig.update_traces(line_color=THEME["primary"], line_width=3, marker_size=10)
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
                fig2 = px.line(kpi_trend, x="Period", y="Value", markers=True)
                fig2.update_traces(line_color=THEME["accent"], line_width=3, marker_size=9)
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
        file_name="emergency.csv",
        mime="text/csv",
    )
