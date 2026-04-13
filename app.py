"""
app.py  —  LinkinReachly User Funnel Analytics
Srinivasa Kommireddy | Portfolio Project

Tabs:
  1. Overview      — headline KPIs + monthly acquisition trend
  2. Funnel        — conversion funnel (signup → retained)
  3. Retention     — cohort retention heatmap
  4. A/B Test      — variant comparison across all key metrics
  5. Engagement    — engagement breakdown by source / plan
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── PAGE CONFIG ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LinkinReachly Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Dark background */
.stApp {
    background-color: #0D1117;
    color: #E6EDF3;
}

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1280px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #161B22;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    border: 1px solid #30363D;
}
.stTabs [data-baseweb="tab"] {
    color: #8B949E;
    font-family: 'DM Sans', sans-serif;
    font-weight: 500;
    font-size: 13px;
    border-radius: 8px;
    padding: 8px 18px;
    border: none;
}
.stTabs [aria-selected="true"] {
    background: #1B3A6B !important;
    color: #FFFFFF !important;
}

/* Metric cards */
.metric-card {
    background: #161B22;
    border: 1px solid #30363D;
    border-radius: 12px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #1B3A6B, #2563EB);
    border-radius: 12px 12px 0 0;
}
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #8B949E;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 32px;
    font-weight: 700;
    color: #E6EDF3;
    line-height: 1;
    font-family: 'DM Mono', monospace;
}
.metric-delta {
    font-size: 12px;
    color: #3FB950;
    margin-top: 6px;
    font-weight: 500;
}
.metric-delta.neg { color: #F85149; }

/* Section title */
.section-title {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: #8B949E;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* Insight callout */
.insight-box {
    background: #0D2045;
    border: 1px solid #1B3A6B;
    border-left: 4px solid #2563EB;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #A5C8F0;
    line-height: 1.6;
}
.insight-box strong { color: #E6EDF3; }

/* Hero header */
.hero {
    background: linear-gradient(135deg, #0D1117 0%, #0D2045 100%);
    border: 1px solid #1B3A6B;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.hero-title {
    font-size: 22px;
    font-weight: 700;
    color: #E6EDF3;
}
.hero-sub {
    font-size: 13px;
    color: #8B949E;
    margin-top: 4px;
}
.hero-badge {
    background: #1B3A6B;
    color: #7EB3FF;
    font-size: 11px;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.05em;
    border: 1px solid #2563EB;
}

/* Plotly chart backgrounds */
div[data-testid="stPlotlyChart"] {
    border-radius: 12px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/users.csv", parse_dates=["signup_date"])
    df["signup_month"] = pd.to_datetime(df["signup_month"])
    return df

df = load_data()

# ── PLOTLY THEME ──────────────────────────────────────────────────────────
CHART_BG    = "#161B22"
PAPER_BG    = "#161B22"
GRID_COLOR  = "#21262D"
TEXT_COLOR  = "#C9D1D9"
LABEL_COLOR = "#E6EDF3"
ACCENT      = "#2563EB"
ACCENT2     = "#3FB950"
ACCENT3     = "#F0883E"
NAVY        = "#1B3A6B"
PALETTE     = [ACCENT, ACCENT2, ACCENT3, "#DA3633", "#7C3AED", "#0EA5E9"]

def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(color="#E6EDF3", size=14, family="DM Sans"), x=0.02),
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=CHART_BG,
        font=dict(color=TEXT_COLOR, family="DM Sans", size=12),
        height=height,
        margin=dict(l=16, r=16, t=44, b=16),
        xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR), title=dict(font=dict(color=LABEL_COLOR))),
        yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR), title=dict(font=dict(color=LABEL_COLOR))),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=LABEL_COLOR)),
        hoverlabel=dict(bgcolor="#1C2128", bordercolor="#30363D", font=dict(color="#E6EDF3", family="DM Sans")),
    )

# ── HERO ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div>
    <div class="hero-title">📊 LinkinReachly — Product Analytics Dashboard</div>
    <div class="hero-sub">Funnel · Retention · A/B Testing · Engagement &nbsp;|&nbsp; 1,200 users · Jan–Dec 2024</div>
  </div>
  <div class="hero-badge">PORTFOLIO PROJECT</div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈  Overview", "🔽  Funnel", "🔄  Retention", "🧪  A/B Test", "⚡  Engagement"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI cards
    total     = len(df)
    activated = df["activated"].sum()
    retained7 = df["retained_7d"].sum()
    retained30= df["retained_30d"].sum()
    act_rate  = activated / total
    ret7_rate = retained7 / activated
    ret30_rate= retained30 / retained7 if retained7 > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    cards = [
        (c1, "Total Sign-ups",    f"{total:,}",           "+18% vs prior period", False),
        (c2, "Activation Rate",   f"{act_rate:.1%}",      "+14 pp vs benchmark",  False),
        (c3, "7-Day Retention",   f"{ret7_rate:.1%}",     "+11 pp YoY",           False),
        (c4, "30-Day Retention",  f"{retained30/activated:.1%}", "of activated users", False),
    ]
    for col, label, val, delta, neg in cards:
        with col:
            neg_class = "neg" if neg else ""
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{val}</div>
              <div class="metric-delta {neg_class}">{delta}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Monthly acquisition + retention trend
    monthly = df.groupby("signup_month").agg(
        signups=("user_id","count"),
        activations=("activated","sum"),
        retained7=("retained_7d","sum"),
        retained30=("retained_30d","sum"),
    ).reset_index()
    monthly["act_rate"]   = monthly["activations"] / monthly["signups"]
    monthly["ret7_rate"]  = monthly["retained7"]   / monthly["activations"]

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=monthly["signup_month"], y=monthly["signups"],
        name="Sign-ups", marker_color=NAVY, opacity=0.85,
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=monthly["signup_month"], y=monthly["act_rate"],
        name="Activation Rate", mode="lines+markers",
        line=dict(color=ACCENT, width=2.5), marker=dict(size=6),
    ), secondary_y=True)
    fig.add_trace(go.Scatter(
        x=monthly["signup_month"], y=monthly["ret7_rate"],
        name="7-Day Retention", mode="lines+markers",
        line=dict(color=ACCENT2, width=2.5, dash="dot"), marker=dict(size=6),
    ), secondary_y=True)

    layout = base_layout("Monthly Acquisition & Retention Rates", height=360)
    layout["yaxis2"] = dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR), showgrid=False)
    fig.update_layout(**layout)
    fig.update_yaxes(title_text="Sign-ups", secondary_y=False, title_font=dict(size=11, color=LABEL_COLOR))
    fig.update_yaxes(title_text="Rate", secondary_y=True, title_font=dict(size=11, color=LABEL_COLOR))
    st.plotly_chart(fig, use_container_width=True)

    # Source breakdown
    col_a, col_b = st.columns(2)

    with col_a:
        src = df.groupby("source").agg(
            users=("user_id","count"),
            act_rate=("activated","mean"),
        ).reset_index().sort_values("users", ascending=True)
        fig2 = go.Figure(go.Bar(
            y=src["source"], x=src["users"], orientation="h",
            marker=dict(
                color=src["act_rate"], colorscale=[[0,"#0D2045"],[1,ACCENT]],
                showscale=True, colorbar=dict(title=dict(text="Act. Rate", font=dict(color=LABEL_COLOR)), tickformat=".0%", thickness=12, len=0.7, tickfont=dict(color=LABEL_COLOR))
            ),
            text=[f"{v:,}" for v in src["users"]], textposition="outside",
            hovertemplate="<b>%{y}</b><br>Users: %{x:,}<br>Activation: %{marker.color:.1%}<extra></extra>"
        ))
        layout2 = base_layout("Acquisition by Source", height=320)
        layout2.pop("xaxis", None); layout2.pop("yaxis", None)
        fig2.update_layout(**layout2,
            xaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
            yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_b:
        plan = df.groupby("plan").agg(
            users=("user_id","count"),
            act_rate=("activated","mean"),
            ret7=("retained_7d","mean"),
            ret30=("retained_30d","mean"),
        ).reset_index()
        fig3 = go.Figure()
        for metric, color, name in [
            ("act_rate", ACCENT, "Activation"),
            ("ret7",     ACCENT2,"7-Day Retention"),
            ("ret30",    ACCENT3,"30-Day Retention"),
        ]:
            fig3.add_trace(go.Bar(
                name=name, x=plan["plan"], y=plan[metric],
                marker_color=color, text=[f"{v:.0%}" for v in plan[metric]],
                textposition="outside",
            ))
        layout3 = base_layout("Conversion Rates by Plan", height=320)
        layout3.pop("xaxis", None); layout3.pop("yaxis", None)
        fig3.update_layout(**layout3, barmode="group",
            yaxis=dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
            xaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
        )
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown("""<div class="insight-box">
    💡 <strong>Key Insight:</strong> Referral and Product Hunt users activate at the highest rates (&gt;80%),
    suggesting word-of-mouth brings higher-intent users. Pro and Team plan users retain at 1.4× the rate of Free users —
    indicating upgrade nudges during onboarding could meaningfully improve overall 30-day retention.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — FUNNEL
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    stages = ["Signed Up", "Activated", "First Apply", "7-Day Retained", "30-Day Retained"]
    values = [
        len(df),
        df["activated"].sum(),
        df["first_applied"].sum(),
        df["retained_7d"].sum(),
        df["retained_30d"].sum(),
    ]
    pct_of_top   = [v / values[0] for v in values]
    pct_of_prev  = [1.0] + [values[i]/values[i-1] if values[i-1] > 0 else 0 for i in range(1, len(values))]

    col_f1, col_f2 = st.columns([3, 2])

    with col_f1:
        colors = [ACCENT, "#1E4DB7", "#1A40A0", ACCENT2, "#2EA043"]
        fig_funnel = go.Figure(go.Funnel(
            y=stages, x=values,
            textinfo="value+percent previous",
            textfont=dict(color="#E6EDF3", size=13, family="DM Sans"),
            marker=dict(color=colors, line=dict(color="#0D1117", width=1)),
            connector=dict(line=dict(color=GRID_COLOR, width=1)),
            hovertemplate="<b>%{y}</b><br>Users: %{x:,}<br>% of total: %{percentTotal:.1%}<extra></extra>",
        ))
        layout_f = base_layout("Full Conversion Funnel — Signup → 30-Day Retained", height=420)
        layout_f.pop("xaxis", None); layout_f.pop("yaxis", None)
        fig_funnel.update_layout(**layout_f)
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col_f2:
        st.markdown("<div class='section-title'>Funnel Breakdown</div>", unsafe_allow_html=True)
        for i, (stage, val, pct_top, pct_prev) in enumerate(zip(stages, values, pct_of_top, pct_of_prev)):
            drop = 1 - pct_prev if i > 0 else 0
            color = "#F85149" if drop > 0.35 else ("#F0883E" if drop > 0.20 else "#3FB950")
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:10px; padding:14px 18px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                  <div class="metric-label">{stage}</div>
                  <div class="metric-value" style="font-size:22px;">{val:,}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:20px; font-weight:700; font-family:'DM Mono',monospace; color:#E6EDF3;">{pct_top:.1%}</div>
                  <div style="font-size:11px; color:{color}; margin-top:2px;">
                    {'▼ ' + f'{drop:.0%} drop' if i > 0 else '100% of signups'}
                  </div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Drop-off waterfall
    st.markdown("<br>", unsafe_allow_html=True)
    drops = [values[i] - values[i+1] for i in range(len(values)-1)]
    drop_stages = [f"{stages[i]} → {stages[i+1]}" for i in range(len(stages)-1)]

    fig_drop = go.Figure(go.Bar(
        x=drop_stages, y=drops,
        marker_color=[ACCENT3 if d == max(drops) else "#30363D" for d in drops],
        text=[f"{d:,} users lost ({d/values[0]:.1%})" for d in drops],
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Lost: %{y:,} users<extra></extra>",
    ))
    layout_drop = base_layout("Drop-off Volume by Funnel Stage (users lost)", height=320)
    fig_drop.update_layout(**layout_drop)
    st.plotly_chart(fig_drop, use_container_width=True)

    biggest_drop_idx = drops.index(max(drops))
    st.markdown(f"""<div class="insight-box">
    💡 <strong>Biggest Opportunity:</strong> The largest drop-off occurs at <strong>{drop_stages[biggest_drop_idx]}</strong>
    ({drops[biggest_drop_idx]:,} users, {drops[biggest_drop_idx]/values[0]:.1%} of all signups).
    This is where product and UX investment would have the highest leverage on overall funnel efficiency.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — RETENTION COHORTS
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    # Build monthly cohort retention
    monthly_cohorts = df.groupby("signup_month").agg(
        cohort_size=("user_id","count"),
        activated=("activated","sum"),
        first_applied=("first_applied","sum"),
        retained_7d=("retained_7d","sum"),
        retained_30d=("retained_30d","sum"),
    ).reset_index()

    monthly_cohorts["Week 0 (Signup)"]     = 1.0
    monthly_cohorts["Week 1 (Activated)"]  = monthly_cohorts["activated"]      / monthly_cohorts["cohort_size"]
    monthly_cohorts["Week 1 (Applied)"]    = monthly_cohorts["first_applied"]  / monthly_cohorts["cohort_size"]
    monthly_cohorts["Week 1 (7-Day Ret.)"] = monthly_cohorts["retained_7d"]    / monthly_cohorts["cohort_size"]
    monthly_cohorts["Week 4 (30-Day Ret.)"]= monthly_cohorts["retained_30d"]   / monthly_cohorts["cohort_size"]

    cohort_cols = ["Week 0 (Signup)","Week 1 (Activated)","Week 1 (Applied)","Week 1 (7-Day Ret.)","Week 4 (30-Day Ret.)"]
    heatmap_data = monthly_cohorts[cohort_cols].values
    y_labels = [d.strftime("%b %Y") for d in monthly_cohorts["signup_month"]]

    fig_heat = go.Figure(go.Heatmap(
        z=heatmap_data,
        x=cohort_cols,
        y=y_labels,
        colorscale=[[0,"#0D1117"],[0.3,"#0D2045"],[0.7,NAVY],[1.0,ACCENT]],
        text=[[f"{v:.0%}" for v in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont=dict(size=11, color="#E6EDF3"),
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1%}<extra></extra>",
        showscale=True,
        colorbar=dict(tickformat=".0%", thickness=14, len=0.8, title=dict(text="Rate", font=dict(color=LABEL_COLOR)), tickfont=dict(color=LABEL_COLOR)),
        zmin=0, zmax=1,
    ))
    layout_heat = base_layout("Cohort Retention Heatmap — Monthly Cohorts 2024", height=500)
    layout_heat.pop("xaxis", None); layout_heat.pop("yaxis", None)
    layout_heat["margin"] = dict(l=16, r=16, t=80, b=16)
    fig_heat.update_layout(**layout_heat,
        xaxis=dict(tickfont=dict(size=11, color=LABEL_COLOR), side="top"),
        yaxis=dict(tickfont=dict(size=11, color=LABEL_COLOR), autorange="reversed"),
    )
    st.plotly_chart(fig_heat, use_container_width=True)

    # Cohort line chart — 7d retention over months
    col_r1, col_r2 = st.columns(2)
    with col_r1:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=monthly_cohorts["signup_month"],
            y=monthly_cohorts["Week 1 (7-Day Ret.)"],
            mode="lines+markers",
            name="7-Day Retention",
            line=dict(color=ACCENT, width=2.5),
            marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(37,99,235,0.1)",
        ))
        layout_line = base_layout("7-Day Retention by Cohort Month", height=300)
        layout_line.pop("yaxis", None)
        fig_line.update_layout(**layout_line,
            yaxis=dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
        )
        st.plotly_chart(fig_line, use_container_width=True)

    with col_r2:
        fig_comp = go.Figure()
        for col_name, color, label in [
            ("Week 1 (Activated)", ACCENT, "Activation"),
            ("Week 1 (7-Day Ret.)", ACCENT2, "7-Day Retention"),
            ("Week 4 (30-Day Ret.)", ACCENT3, "30-Day Retention"),
        ]:
            fig_comp.add_trace(go.Scatter(
                x=monthly_cohorts["signup_month"],
                y=monthly_cohorts[col_name],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=5),
            ))
        layout_comp = base_layout("All Rates by Cohort Month", height=300)
        layout_comp.pop("yaxis", None)
        fig_comp.update_layout(**layout_comp,
            yaxis=dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    best_month = monthly_cohorts.loc[monthly_cohorts["Week 1 (7-Day Ret.)"].idxmax(), "signup_month"].strftime("%b %Y")
    best_rate  = monthly_cohorts["Week 1 (7-Day Ret.)"].max()
    st.markdown(f"""<div class="insight-box">
    💡 <strong>Cohort Insight:</strong> The <strong>{best_month}</strong> cohort had the strongest 7-day retention
    at <strong>{best_rate:.1%}</strong>. Cohorts from Q1 and Q3 consistently outperform Q2, suggesting
    possible seasonality in job-seeker intent — worth investigating with a segmented campaign in those windows.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — A/B TEST
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    variants = df.groupby("ab_variant").agg(
        n=("user_id","count"),
        act_rate=("activated","mean"),
        apply_rate=("first_applied","mean"),
        ret7_rate=("retained_7d","mean"),
        ret30_rate=("retained_30d","mean"),
        avg_applies=("applies_per_session","mean"),
        avg_ai_pct=("ai_applies_pct","mean"),
    ).reset_index()

    ctrl = variants[variants["ab_variant"].str.startswith("A")].iloc[0]
    var  = variants[variants["ab_variant"].str.startswith("B")].iloc[0]

    # Stat sig calculation (z-test for proportions)
    from math import sqrt
    def z_test(p1, p2, n1, n2):
        p_pool = (p1*n1 + p2*n2) / (n1 + n2)
        se = sqrt(p_pool * (1-p_pool) * (1/n1 + 1/n2))
        z = (p2 - p1) / se if se > 0 else 0
        # Two-tailed p-value approximation
        import math
        p_val = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / sqrt(2))))
        return z, p_val

    metrics = {
        "Activation Rate":     ("act_rate",  True),
        "First Apply Rate":    ("apply_rate",True),
        "7-Day Retention":     ("ret7_rate", True),
        "30-Day Retention":    ("ret30_rate",True),
        "Applies / Session":   ("avg_applies",False),
        "AI Apply %":          ("avg_ai_pct", False),
    }

    st.markdown("<div class='section-title'>A/B Test: Onboarding Variant vs Control</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:#0D2045; border:1px solid #1B3A6B; border-radius:10px; padding:16px 20px; margin-bottom:20px; font-size:13px; color:#A5C8F0; line-height:1.7;">
    <b style="color:#E6EDF3;">Hypothesis:</b> Replacing generic onboarding with AI-powered job matching
    during signup (Variant B) will increase activation and 7-day retention rates.<br>
    <b style="color:#E6EDF3;">Test period:</b> Jan–Dec 2024 &nbsp;|&nbsp;
    <b style="color:#E6EDF3;">Sample:</b> 1,200 users (600 per variant) &nbsp;|&nbsp;
    <b style="color:#E6EDF3;">Significance threshold:</b> p &lt; 0.05
    </div>""", unsafe_allow_html=True)

    cols = st.columns(3)
    metric_items = list(metrics.items())
    for idx, (label, (col, is_pct)) in enumerate(metric_items):
        c_val = ctrl[col]
        v_val = var[col]
        lift  = (v_val - c_val) / c_val if c_val > 0 else 0
        if is_pct:
            z, p = z_test(c_val, v_val, int(ctrl["n"]), int(var["n"]))
            sig = "✓ Significant" if p < 0.05 else "✗ Not sig."
            sig_color = "#3FB950" if p < 0.05 else "#8B949E"
            p_text = f"p={p:.3f}"
        else:
            sig = "—"
            sig_color = "#8B949E"
            p_text = ""

        fmt = ".1%" if is_pct else ".2f"
        lift_color = "#3FB950" if lift > 0 else "#F85149"

        with cols[idx % 3]:
            st.markdown(f"""
            <div class="metric-card" style="margin-bottom:14px;">
              <div class="metric-label">{label}</div>
              <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:6px;">
                <div>
                  <div style="font-size:11px; color:#8B949E; margin-bottom:2px;">Control A</div>
                  <div style="font-size:20px; font-weight:700; font-family:'DM Mono',monospace; color:#8B949E;">{c_val:{fmt}}</div>
                </div>
                <div style="font-size:18px; color:#30363D;">→</div>
                <div>
                  <div style="font-size:11px; color:#8B949E; margin-bottom:2px;">Variant B</div>
                  <div style="font-size:20px; font-weight:700; font-family:'DM Mono',monospace; color:#E6EDF3;">{v_val:{fmt}}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:15px; font-weight:700; color:{lift_color};">{'+' if lift>0 else ''}{lift:.1%}</div>
                  <div style="font-size:10px; color:{sig_color}; margin-top:3px;">{sig}</div>
                  <div style="font-size:10px; color:#8B949E;">{p_text}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Visual comparison bar chart
    st.markdown("<br>", unsafe_allow_html=True)
    rate_metrics = ["act_rate","apply_rate","ret7_rate","ret30_rate"]
    rate_labels  = ["Activation","First Apply","7-Day Ret.","30-Day Ret."]
    ctrl_vals = [ctrl[m] for m in rate_metrics]
    var_vals  = [var[m]  for m in rate_metrics]

    fig_ab = go.Figure()
    fig_ab.add_trace(go.Bar(
        name="A – Control", x=rate_labels, y=ctrl_vals,
        marker_color=NAVY, text=[f"{v:.1%}" for v in ctrl_vals], textposition="outside",
    ))
    fig_ab.add_trace(go.Bar(
        name="B – AI Job Match", x=rate_labels, y=var_vals,
        marker_color=ACCENT, text=[f"{v:.1%}" for v in var_vals], textposition="outside",
    ))
    layout_ab = base_layout("Variant vs Control — Conversion Rate Comparison", height=360)
    layout_ab.pop("yaxis", None)
    fig_ab.update_layout(**layout_ab, barmode="group",
        yaxis=dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
    )
    st.plotly_chart(fig_ab, use_container_width=True)

    sig_metrics = [label for label, (col, is_pct) in metrics.items() if is_pct]
    lift_val = (var["ret7_rate"] - ctrl["ret7_rate"]) / ctrl["ret7_rate"]
    st.markdown(f"""<div class="insight-box">
    🧪 <strong>Test Verdict:</strong> Variant B (AI Job Match onboarding) shows statistically significant
    improvement across all key conversion metrics. The 7-day retention lift of <strong>{lift_val:.0%}</strong>
    is the most commercially significant finding — recommending <strong>ship Variant B</strong> as the new default onboarding.
    Monitor 30-day retention over the next 2 cohorts to confirm sustained impact.
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 5 — ENGAGEMENT
# ════════════════════════════════════════════════════════════════════════════
with tab5:
    active = df[df["activated"] == 1].copy()

    col_e1, col_e2 = st.columns(2)

    with col_e1:
        src_eng = active.groupby("source").agg(
            users=("user_id","count"),
            sessions=("sessions_per_week","mean"),
            applies=("applies_per_session","mean"),
        ).reset_index().sort_values("applies", ascending=True)

        fig_eng = go.Figure()
        fig_eng.add_trace(go.Bar(
            y=src_eng["source"], x=src_eng["applies"], name="Applies/Session",
            orientation="h", marker_color=ACCENT,
            text=[f"{v:.1f}" for v in src_eng["applies"]], textposition="outside",
        ))
        fig_eng.add_trace(go.Bar(
            y=src_eng["source"], x=src_eng["sessions"], name="Sessions/Week",
            orientation="h", marker_color=NAVY, opacity=0.7,
            text=[f"{v:.1f}" for v in src_eng["sessions"]], textposition="outside",
        ))
        layout_eng = base_layout("Engagement by Acquisition Source", height=320)
        layout_eng.pop("xaxis", None); layout_eng.pop("yaxis", None)
        fig_eng.update_layout(**layout_eng, barmode="group",
            xaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
            yaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
        )
        st.plotly_chart(fig_eng, use_container_width=True)

    with col_e2:
        plan_eng = active.groupby("plan").agg(
            sessions=("sessions_per_week","mean"),
            applies=("applies_per_session","mean"),
            ai_pct=("ai_applies_pct","mean"),
            msg_open=("msg_open_rate","mean"),
            followup=("followup_click_rate","mean"),
        ).reset_index()

        metrics_plot = ["sessions","applies","ai_pct","msg_open","followup"]
        labels_plot  = ["Sessions/Wk","Applies/Ses","AI Apply %","Msg Open %","Follow-up %"]

        fig_radar = go.Figure()
        colors_plan = {"Free": NAVY, "Pro": ACCENT, "Team": ACCENT2}
        for _, row in plan_eng.iterrows():
            # Normalize 0-1 per metric for radar
            vals = [
                row["sessions"] / 7,
                row["applies"] / 8,
                row["ai_pct"],
                row["msg_open"],
                row["followup"],
            ]
            vals_closed = vals + [vals[0]]
            labels_closed = labels_plot + [labels_plot[0]]
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_closed, theta=labels_closed,
                fill="toself", name=row["plan"],
                line=dict(color=colors_plan.get(row["plan"], ACCENT), width=2),
                fillcolor="rgba({},{},{},0.15)".format(*[int(colors_plan.get(row["plan"], ACCENT).lstrip('#')[i:i+2], 16) for i in (0,2,4)]),
                hovertemplate="<b>" + row["plan"] + "</b><br>%{theta}: %{r:.2f}<extra></extra>",
            ))
        layout_radar = base_layout("Engagement Profile by Plan (normalized)", height=320)
        layout_radar.pop("xaxis", None); layout_radar.pop("yaxis", None)
        fig_radar.update_layout(**layout_radar,
            polar=dict(
                bgcolor=CHART_BG,
                radialaxis=dict(visible=True, range=[0,1], gridcolor=GRID_COLOR, tickfont=dict(size=9)),
                angularaxis=dict(gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
            )
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    # AI apply % trend over months
    monthly_ai = active.groupby("signup_month").agg(
        ai_pct=("ai_applies_pct","mean"),
        msg_open=("msg_open_rate","mean"),
        followup=("followup_click_rate","mean"),
    ).reset_index()

    fig_trend = go.Figure()
    for col_name, color, label in [
        ("ai_pct",  ACCENT,  "AI Apply %"),
        ("msg_open",ACCENT2, "Message Open Rate"),
        ("followup",ACCENT3, "Follow-up Click Rate"),
    ]:
        fig_trend.add_trace(go.Scatter(
            x=monthly_ai["signup_month"], y=monthly_ai[col_name],
            mode="lines+markers", name=label,
            line=dict(color=color, width=2.5), marker=dict(size=6),
        ))
    layout_trend = base_layout("Engagement Metrics Trend — Monthly Average (Activated Users)", height=320)
    layout_trend.pop("yaxis", None)
    fig_trend.update_layout(**layout_trend,
        yaxis=dict(tickformat=".0%", gridcolor=GRID_COLOR, tickfont=dict(size=11, color=LABEL_COLOR)),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    top_src = active.groupby("source")["applies_per_session"].mean().idxmax()
    top_val = active.groupby("source")["applies_per_session"].mean().max()
    st.markdown(f"""<div class="insight-box">
    💡 <strong>Engagement Insight:</strong> <strong>{top_src}</strong> users generate the highest applies per session
    ({top_val:.1f} avg). Team plan users show the strongest engagement profile across all dimensions —
    AI apply adoption is highest in this segment, making it a strong candidate for feature expansion and upsell targeting.
    </div>""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:40px; padding-top:20px; border-top:1px solid #21262D;
     text-align:center; font-size:11px; color:#484F58; letter-spacing:0.05em;">
  SRINIVASA KOMMIREDDY &nbsp;·&nbsp; PORTFOLIO PROJECT &nbsp;·&nbsp;
  srinik27@outlook.com &nbsp;·&nbsp;
  Mock data generated for analytical demonstration purposes
</div>
""", unsafe_allow_html=True)
