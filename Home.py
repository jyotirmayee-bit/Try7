"""
Home.py
-------
CLUSTER DASHBOARD -- the executive view for higher management.
Run the whole app with:  streamlit run Home.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from data_loader import load_master_data
from utils import add_status_column, department_summary, compute_conversion_metrics, THEME
from config import DEPARTMENTS

st.set_page_config(
    page_title="Srikara Hospitals | Cluster Dashboard",
    page_icon="🏥",
    layout="wide",
)

# ---------------------------------------------------------------------
# Light custom styling -- keeps the built-in Streamlit look but tidies
# up spacing and gives KPI cards a bit more "boardroom" polish.
# ---------------------------------------------------------------------
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 14px 16px 8px 16px;
    }
    div[data-testid="stMetricValue"] { font-size: 1.6rem; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------
# Sidebar: quick navigation to every unit dashboard from anywhere
# ---------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🏥 Srikara Hospitals")
    st.page_link("Home.py", label="Cluster Dashboard", icon="🏠")
    st.markdown("**Unit Dashboards**")
    for dept in DEPARTMENTS:
        st.page_link(dept["page"], label=dept["name"], icon=dept["icon"])
    st.divider()
    st.caption("Data refreshes every 5 minutes.")

# ---------------------------------------------------------------------
# Load & prepare data
# ---------------------------------------------------------------------
raw_df = load_master_data()
df = add_status_column(raw_df)
summary_df = department_summary(df)

# ---------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------
st.title("🏥 Srikara Hospitals — Cluster Dashboard")
st.caption("Executive overview across all departments, updated live from the Unit Tracker sheet.")

# ---------------------------------------------------------------------
# Filters (sit above the tabs so they apply everywhere)
# ---------------------------------------------------------------------
f1, f2, f3 = st.columns([2, 1.2, 2])
with f1:
    dept_filter = st.multiselect(
        "Filter by department",
        options=[d["name"] for d in DEPARTMENTS],
        default=[],
        placeholder="All departments",
    )
with f2:
    status_filter = st.multiselect(
        "Filter by status",
        options=["On Track", "Off Track", "No Data", "Not Measurable"],
        default=[],
        placeholder="All statuses",
    )
with f3:
    search_text = st.text_input("Search KPI name", placeholder="e.g. bed occupancy, mortality...")

filtered_df = df.copy()
if dept_filter:
    filtered_df = filtered_df[filtered_df["Department"].isin(dept_filter)]
if status_filter:
    filtered_df = filtered_df[filtered_df["Status"].isin(status_filter)]
if search_text:
    filtered_df = filtered_df[filtered_df["Particulars"].str.contains(search_text, case=False, na=False)]

filtered_summary = department_summary(filtered_df) if len(filtered_df) else summary_df.iloc[0:0]

st.divider()

# ---------------------------------------------------------------------
# Tabs: Overview | Trends & Conversion | Deep Dive | Raw Data
# ---------------------------------------------------------------------
tab_overview, tab_trends, tab_deepdive, tab_raw = st.tabs(
    ["📊 Overview", "📈 Trends & Conversion", "🔍 Department Deep-Dive", "📋 Raw Data"]
)

# =======================================================================
# TAB 1 — OVERVIEW
# =======================================================================
with tab_overview:
    total_kpis = len(filtered_df)
    on_track = int((filtered_df["Status"] == "On Track").sum())
    off_track = int((filtered_df["Status"] == "Off Track").sum())
    no_data = int((filtered_df["Status"] == "No Data").sum())
    measurable = on_track + off_track
    overall_health = round((on_track / measurable) * 100, 1) if measurable else 0.0

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total KPIs Tracked", total_kpis)
    c2.metric("🟢 On Track", on_track)
    c3.metric("🔴 Off Track", off_track)
    c4.metric("⚪ Awaiting Data", no_data)
    c5.metric("Overall Health Score", f"{overall_health}%")

    st.divider()

    left, right = st.columns([2, 1])

    with left:
        st.subheader("Department-wise KPI Status")
        if len(filtered_summary):
            chart_df = filtered_summary.melt(
                id_vars="Department",
                value_vars=["On Track", "Off Track", "No Data", "Not Measurable"],
                var_name="Status",
                value_name="Count",
            )
            fig = px.bar(
                chart_df, x="Department", y="Count", color="Status",
                color_discrete_map=THEME, barmode="stack",
            )
            fig.update_layout(xaxis_tickangle=-30, legend_title_text="", margin=dict(t=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data matches the current filters.")

    with right:
        st.subheader("Overall Health")
        if len(filtered_df):
            donut_df = filtered_df["Status"].value_counts().reset_index()
            donut_df.columns = ["Status", "Count"]
            fig2 = px.pie(
                donut_df, names="Status", values="Count", hole=0.55,
                color="Status", color_discrete_map=THEME,
            )
            fig2.update_layout(showlegend=True, margin=dict(t=10))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No data to show.")

    st.divider()

    # ---- Health Score leaderboard (ranked, so management sees who needs attention) ----
    st.subheader("Department Health Score Ranking")
    if len(filtered_summary):
        ranked = filtered_summary.sort_values("Health Score", ascending=True)
        fig3 = px.bar(
            ranked, x="Health Score", y="Department", orientation="h",
            color="Health Score", color_continuous_scale=["#dc2626", "#f59e0b", "#16a34a"],
            range_color=[0, 100], text="Health Score",
        )
        fig3.update_traces(texttemplate="%{text}%", textposition="outside")
        fig3.update_layout(coloraxis_showscale=False, margin=dict(t=10), xaxis_range=[0, 110])
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No data matches the current filters.")

    st.divider()

    # ---- Departments needing attention ----
    st.subheader("⚠️ Departments Needing Attention")
    if len(filtered_summary):
        attention = filtered_summary[filtered_summary["Off Track"] > 0].sort_values("Off Track", ascending=False)
        if len(attention):
            st.dataframe(
                attention[["Department", "Off Track", "On Track", "Total KPIs", "Health Score"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.success("No departments have off-track KPIs right now. 🎉")

    st.divider()
    st.subheader("Open a Unit Dashboard")
    cols = st.columns(3)
    for i, dept in enumerate(DEPARTMENTS):
        dept_rows = summary_df[summary_df["Department"] == dept["name"]]
        total = int(dept_rows["Total KPIs"].iloc[0]) if not dept_rows.empty else 0
        off = int(dept_rows["Off Track"].iloc[0]) if not dept_rows.empty else 0
        health = float(dept_rows["Health Score"].iloc[0]) if not dept_rows.empty else 0

        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### {dept['icon']} {dept['name']}")
                st.caption(f"{total} KPIs • {off} off track • {health}% healthy")
                st.page_link(dept["page"], label="Open Unit Dashboard →", icon="➡️")

# =======================================================================
# TAB 2 — TRENDS & CONVERSION
# =======================================================================
with tab_trends:
    st.subheader("Cluster-wide Trend: Last Month → MTD → Today")
    st.caption("Total of every numeric KPI in the sheet, added up across all departments, at each time snapshot.")

    trend_rows = []
    for period in ["Last Month", "MTD", "Today"]:
        numeric = pd.to_numeric(filtered_df[period], errors="coerce").dropna()
        if len(numeric):
            trend_rows.append({"Period": period, "Total": numeric.sum()})
    trend_df = pd.DataFrame(trend_rows)

    if len(trend_df) >= 2:
        trend_df["Period"] = pd.Categorical(trend_df["Period"], ["Last Month", "MTD", "Today"], ordered=True)
        trend_df = trend_df.sort_values("Period")
        fig4 = px.line(trend_df, x="Period", y="Total", markers=True)
        fig4.update_traces(line_color=THEME["primary"], line_width=3, marker_size=10)
        fig4.update_layout(margin=dict(t=10))
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("Not enough numeric data across Last Month / MTD / Today yet to plot a trend.")

    st.divider()

    st.subheader("🔄 Conversion Metrics")
    st.caption("Automatically detected funnel rates, e.g. how many OPD visitors convert to admissions.")
    conversions = compute_conversion_metrics(df)
    if conversions:
        cols = st.columns(len(conversions))
        for col, conv in zip(cols, conversions):
            with col:
                st.metric(conv["label"], f"{conv['rate']}%", help=conv["help"])
                st.caption(f"{conv['numerator_label']} ÷ {conv['denominator_label']}")
    else:
        st.info(
            "No matching KPI pairs found yet to calculate a conversion rate. "
            "Once the sheet has clearly labeled footfall/admission-type rows with 'Today' values filled in, "
            "conversion rates will appear here automatically."
        )

# =======================================================================
# TAB 3 — DEPARTMENT DEEP-DIVE
# =======================================================================
with tab_deepdive:
    st.subheader("Compare Departments Side-by-Side")
    compare_depts = st.multiselect(
        "Choose departments to compare",
        options=[d["name"] for d in DEPARTMENTS],
        default=[d["name"] for d in DEPARTMENTS[:3]],
    )
    if compare_depts:
        compare_df = filtered_summary[filtered_summary["Department"].isin(compare_depts)]
        if len(compare_df):
            fig5 = px.bar(
                compare_df, x="Department", y="Health Score", color="Department",
                text="Health Score",
            )
            fig5.update_traces(texttemplate="%{text}%", textposition="outside")
            fig5.update_layout(showlegend=False, margin=dict(t=10), yaxis_range=[0, 110])
            st.plotly_chart(fig5, use_container_width=True)

            st.dataframe(
                compare_df[["Department", "On Track", "Off Track", "No Data", "Total KPIs", "Health Score"]],
                use_container_width=True, hide_index=True,
            )
        else:
            st.info("No data for the selected departments under the current filters.")
    else:
        st.info("Pick at least one department above to compare.")

# =======================================================================
# TAB 4 — RAW DATA
# =======================================================================
with tab_raw:
    st.subheader("Full KPI Table")
    display_cols = ["Department", "Particulars", "Today", "MTD", "Target", "Last Month",
                     "Achievement %", "Status Icon", "Status"]
    display_cols = [c for c in display_cols if c in filtered_df.columns]
    st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)

    csv_bytes = filtered_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download this view as CSV",
        data=csv_bytes,
        file_name="srikara_cluster_dashboard.csv",
        mime="text/csv",
    )

st.divider()
st.caption("Data source: Srikara Hospitals Unit Tracker (Google Sheet) • Auto-refreshes every 5 minutes")
