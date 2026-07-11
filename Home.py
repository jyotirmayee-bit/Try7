"""
Home.py
-------
This is the CLUSTER DASHBOARD -- the main page higher management sees.
Run the whole app with:  streamlit run Home.py
"""

import streamlit as st
import plotly.express as px

from data_loader import load_master_data
from utils import add_status_column, department_summary
from config import DEPARTMENTS

st.set_page_config(
    page_title="Srikara Hospitals | Cluster Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ---------------------------------------------------------------------
# Load & prepare data
# ---------------------------------------------------------------------
raw_df = load_master_data()
df = add_status_column(raw_df)

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("🏥 Srikara Hospitals — Cluster Dashboard")
st.caption("Executive overview across all departments. Click a department below to open its unit dashboard.")

# ---------------------------------------------------------------------
# Top KPI cards
# ---------------------------------------------------------------------
total_kpis = len(df)
on_track = int((df["Status"] == "On Track").sum())
off_track = int((df["Status"] == "Off Track").sum())
no_data = int((df["Status"] == "No Data").sum())

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total KPIs Tracked", total_kpis)
c2.metric("🟢 On Track", on_track)
c3.metric("🔴 Off Track", off_track)
c4.metric("⚪ Awaiting Data", no_data)

st.divider()

# ---------------------------------------------------------------------
# Department-wise summary chart
# ---------------------------------------------------------------------
summary_df = department_summary(df)

left, right = st.columns([2, 1])

with left:
    st.subheader("Department-wise KPI Status")
    chart_df = summary_df.melt(
        id_vars="Department",
        value_vars=["On Track", "Off Track", "No Data", "Not Measurable"],
        var_name="Status",
        value_name="Count",
    )
    fig = px.bar(
        chart_df,
        x="Department",
        y="Count",
        color="Status",
        color_discrete_map={
            "On Track": "#2ecc71",
            "Off Track": "#e74c3c",
            "No Data": "#bdc3c7",
            "Not Measurable": "#3498db",
        },
        barmode="stack",
    )
    fig.update_layout(xaxis_tickangle=-30, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Overall Health")
    donut_df = df["Status"].value_counts().reset_index()
    donut_df.columns = ["Status", "Count"]
    fig2 = px.pie(
        donut_df,
        names="Status",
        values="Count",
        hole=0.55,
        color="Status",
        color_discrete_map={
            "On Track": "#2ecc71",
            "Off Track": "#e74c3c",
            "No Data": "#bdc3c7",
            "Not Measurable": "#3498db",
        },
    )
    fig2.update_layout(showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------
# Department cards -> links to Unit Dashboards
# This is the "Cluster dashboard connected to unit dashboards" part.
# ---------------------------------------------------------------------
st.subheader("Open a Unit Dashboard")

cols = st.columns(3)
for i, dept in enumerate(DEPARTMENTS):
    dept_rows = summary_df[summary_df["Department"] == dept["name"]]
    total = int(dept_rows["Total KPIs"].iloc[0]) if not dept_rows.empty else 0
    off = int(dept_rows["Off Track"].iloc[0]) if not dept_rows.empty else 0

    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"### {dept['icon']} {dept['name']}")
            st.caption(f"{total} KPIs tracked  |  {off} off track")
            st.page_link(dept["page"], label="Open Unit Dashboard →", icon="➡️")

st.divider()
st.caption("Data source: Srikara Hospitals Unit Tracker (Google Sheet) • Auto-refreshes every 5 minutes")
