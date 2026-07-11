"""
IP Operations Dashboard
-----------------------
UNIT DASHBOARD for the IP Operations incharge.
This page is opened by clicking the department card on the Cluster Dashboard
(Home.py), or directly from the sidebar.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_master_data, filter_by_department
from utils import add_status_column

st.set_page_config(
    page_title="Srikara Hospitals | IP Operations",
    page_icon="🛏️",
    layout="wide",
)

# Link back up to the Cluster Dashboard (this is the two-way connection)
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
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total KPIs", len(dept_df))
c2.metric("🟢 On Track", int((dept_df["Status"] == "On Track").sum()))
c3.metric("🔴 Off Track", int((dept_df["Status"] == "Off Track").sum()))
c4.metric("⚪ Awaiting Data", int((dept_df["Status"] == "No Data").sum()))

st.divider()

# ---------------------------------------------------------------------
# Detailed KPI table
# ---------------------------------------------------------------------
st.subheader("KPI Detail")
display_cols = ["Particulars", "Today", "MTD", "Target", "Last Month", "Status Icon", "Status"]
display_cols = [c for c in display_cols if c in dept_df.columns]
st.dataframe(dept_df[display_cols], use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------
# Chart: Today vs Target (only for KPIs where a number could be read)
# ---------------------------------------------------------------------
numeric_df = dept_df.copy()
numeric_df["Today_num"] = pd.to_numeric(numeric_df["Today"], errors="coerce") if "Today" in numeric_df else None

chartable = numeric_df.dropna(subset=["Today_num"]) if "Today_num" in numeric_df else numeric_df.iloc[0:0]

if not chartable.empty:
    st.subheader("Today's Performance")
    fig = px.bar(chartable, x="Particulars", y="Today_num", color="Status",
                 color_discrete_map={"On Track": "#2ecc71", "Off Track": "#e74c3c",
                                     "No Data": "#bdc3c7", "Not Measurable": "#3498db"})
    fig.update_layout(xaxis_tickangle=-30, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No numeric 'Today' values entered yet for this department, so no chart is shown.")
