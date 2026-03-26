"""
🛢️ CRUDE EMPIRE - Oil & Gas Tycoon Simulator
Streamlit Web Application
"""

import streamlit as st
import time
import random
import plotly.graph_objects as go
import plotly.express as px
from game_engine import (
    GameState, BasinName, BASIN_CONFIGS, WellStatus, LiftType,
    LIFT_COSTS, LIFT_EFFICIENCY, Well
)
from price_fetcher import fetch_live_prices, simulate_wti, simulate_gas

# ─── Page Config ───
st.set_page_config(
    page_title="Crude Empire",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=JetBrains+Mono:wght@400;700&family=Barlow:wght@300;400;600;700&display=swap');

:root {
    --crude-black: #0a0a0a;
    --crude-dark: #1a1a1a;
    --oil-gold: #d4a017;
    --oil-amber: #f4a523;
    --gas-blue: #2d9cdb;
    --drill-green: #27ae60;
    --danger-red: #e74c3c;
    --steel-gray: #7f8c8d;
    --pipeline-silver: #bdc3c7;
}

.stApp {
    background-color: #0d1117;
}

/* Main title */
.crude-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    color: #d4a017;
    letter-spacing: 6px;
    text-transform: uppercase;
    margin-bottom: 0;
    text-shadow: 0 0 30px rgba(212, 160, 23, 0.3);
}

.crude-subtitle {
    font-family: 'Barlow', sans-serif;
    font-size: 0.95rem;
    color: #7f8c8d;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: -10px;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(212, 160, 23, 0.2);
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
}

.metric-label {
    font-family: 'Barlow', sans-serif;
    font-size: 0.75rem;
    color: #7f8c8d;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.6rem;
    font-weight: 700;
    margin-top: 4px;
}

.gold { color: #d4a017; }
.green { color: #27ae60; }
.blue { color: #2d9cdb; }
.red { color: #e74c3c; }
.white { color: #ecf0f1; }

/* Well cards */
.well-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-left: 4px solid #d4a017;
    border-radius: 0 8px 8px 0;
    padding: 16px;
    margin-bottom: 12px;
}

.well-card.producing {
    border-left-color: #27ae60;
}

.well-card.drilling {
    border-left-color: #2d9cdb;
}

.well-card.shut-in {
    border-left-color: #e74c3c;
}

/* Event banner */
.event-banner {
    background: linear-gradient(135deg, #1a0000 0%, #2d0000 100%);
    border: 1px solid #e74c3c;
    border-radius: 8px;
    padding: 12px 16px;
    margin-bottom: 8px;
    animation: pulse 2s infinite;
}

.event-banner.positive {
    background: linear-gradient(135deg, #001a00 0%, #002d00 100%);
    border-color: #27ae60;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.85; }
}

/* Basin selector */
.basin-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(212, 160, 23, 0.15);
    border-radius: 8px;
    padding: 16px;
    transition: all 0.3s ease;
}

.basin-card:hover {
    border-color: #d4a017;
    box-shadow: 0 0 20px rgba(212, 160, 23, 0.1);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0a0f1a;
    border-right: 1px solid rgba(212, 160, 23, 0.15);
}

/* Buttons */
.stButton > button {
    font-family: 'Barlow', sans-serif;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    border-radius: 4px;
}

/* Progress bars */
.phase-progress {
    background: #1a1a2e;
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
}

.phase-progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}

/* Tables */
.dataframe { font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem !important; }

div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid rgba(212, 160, 23, 0.15);
    border-radius: 8px;
    padding: 12px 16px;
}

div[data-testid="stMetric"] label {
    font-family: 'Barlow', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    font-size: 0.7rem !important;
}

div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    font-family: 'JetBrains Mono', monospace !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Session State Init ───
if "game" not in st.session_state:
    st.session_state.game = GameState()
    prices = fetch_live_prices()
    st.session_state.game.wti_price = prices["wti"]
    st.session_state.game.gas_price = prices["gas"]
    st.session_state.price_source = prices["source"]
    st.session_state.show_new_lease = False
    st.session_state.last_events = []

game: GameState = st.session_state.game


def format_currency(val, short=False):
    if short:
        if abs(val) >= 1_000_000:
            return f"${val / 1_000_000:.1f}M"
        elif abs(val) >= 1_000:
            return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"


def format_number(val, decimals=0):
    if decimals == 0:
        return f"{val:,.0f}"
    return f"{val:,.{decimals}f}"


def status_emoji(status: WellStatus) -> str:
    return {
        WellStatus.LEASE_ACQUIRED: "📋",
        WellStatus.PERMITTING: "📝",
        WellStatus.DRILLING: "⛏️",
        WellStatus.COMPLETING: "💥",
        WellStatus.FLOWBACK: "🌊",
        WellStatus.PRODUCING: "🛢️",
        WellStatus.SHUT_IN: "🚫",
        WellStatus.PLUGGED: "⚰️",
    }.get(status, "❓")


def basin_emoji(basin: BasinName) -> str:
    return {
        BasinName.PERMIAN: "🏜️",
        BasinName.BAKKEN: "❄️",
        BasinName.EAGLE_FORD: "🦅",
        BasinName.DJ_BASIN: "⛰️",
        BasinName.SCOOP_STACK: "🌪️",
    }.get(basin, "🗺️")


# ═══════════════════════════════════════════
# SIDEBAR - Controls & Info
# ═══════════════════════════════════════════
with st.sidebar:
    st.markdown('<p class="crude-title" style="font-size:2rem;">🛢️ Crude Empire</p>', unsafe_allow_html=True)
    st.markdown('<p class="crude-subtitle">Oil & Gas Tycoon Simulator</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Game Controls
    st.markdown("#### ⏱️ Game Controls")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Next Month", use_container_width=True, type="primary"):
            game.wti_price = simulate_wti(game.wti_price)
            game.gas_price = simulate_gas(game.gas_price)
            game.advance_month()
            st.rerun()
    with col2:
        if st.button("⏩ Skip 6 Mo", use_container_width=True):
            for _ in range(6):
                game.wti_price = simulate_wti(game.wti_price)
                game.gas_price = simulate_gas(game.gas_price)
                game.advance_month()
            st.rerun()

    if st.button("⏭️ Skip 1 Year", use_container_width=True):
        for _ in range(12):
            game.wti_price = simulate_wti(game.wti_price)
            game.gas_price = simulate_gas(game.gas_price)
            game.advance_month()
        st.rerun()

    st.markdown("---")

    # Prices
    st.markdown("#### 📊 Commodity Prices")
    st.metric("WTI Crude ($/bbl)", f"${game.wti_price:.2f}",
              delta=f"${game.wti_price - 70:.2f}" if game.month > 0 else None)
    st.metric("Henry Hub Gas ($/mcf)", f"${game.gas_price:.2f}",
              delta=f"${game.gas_price - 3.50:.2f}" if game.month > 0 else None)
    st.caption(f"Source: {st.session_state.get('price_source', 'Simulated')}")

    st.markdown("---")

    # Quick Stats
    st.markdown("#### 📈 Portfolio")
    st.metric("Cash", format_currency(game.cash, short=True))
    st.metric("Portfolio Value", format_currency(game.portfolio_value, short=True))
    st.metric("Total Wells", len(game.wells))
    producing = len([w for w in game.wells if w.status == WellStatus.PRODUCING])
    st.metric("Producing Wells", producing)

    st.markdown("---")
    if st.button("🔄 New Game", use_container_width=True):
        st.session_state.game = GameState()
        prices = fetch_live_prices()
        st.session_state.game.wti_price = prices["wti"]
        st.session_state.game.gas_price = prices["gas"]
        st.session_state.price_source = prices["source"]
        st.rerun()


# ═══════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════

# Header
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:baseline;">
    <div>
        <p class="crude-title">Crude Empire</p>
        <p class="crude-subtitle">Month {game.month} — {game.current_month_name} {game.year}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Game Over
if game.game_over:
    st.error("## 💀 GAME OVER — You went bankrupt! Your company has been liquidated.")
    st.info(f"You lasted **{game.month} months** and produced **{sum(w.cumulative_oil for w in game.wells):,.0f} barrels** of oil.")
    st.stop()

# ─── Active Events Banner ───
if game.event_log:
    recent_events = [e for e in game.event_log if e["month"] == game.month]
    for evt in recent_events:
        css_class = "positive" if evt["cost"] <= 0 else ""
        cost_str = format_currency(abs(evt["cost"]))
        sign = "+" if evt["cost"] <= 0 else "-"
        st.markdown(f"""
        <div class="event-banner {css_class}">
            <strong>⚠️ {evt['event']}</strong> — {evt['well']}<br>
            <span style="color:#bdc3c7;">{evt['description']}</span><br>
            <span style="font-family:'JetBrains Mono',monospace; color:{'#27ae60' if evt['cost'] <= 0 else '#e74c3c'};">
                Impact: {sign}{cost_str}
            </span>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════
# TABS
# ═══════════════════════════════════════════
tab_dashboard, tab_wells, tab_acquire, tab_operations, tab_economics = st.tabs([
    "📊 Dashboard", "🛢️ Wells", "🗺️ Acquire Leases", "🔧 Operations", "💰 Economics"
])

# ─── TAB: Dashboard ───
with tab_dashboard:
    # Top metrics
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("Cash Balance", format_currency(game.cash, True),
                  delta=format_currency(game.monthly_history[-1]["revenue"] - game.monthly_history[-1]["opex"], True) if game.monthly_history else None)
    with m2:
        st.metric("Daily Oil (bbl/d)", format_number(game.total_daily_oil))
    with m3:
        st.metric("Daily Gas (mcf/d)", format_number(game.total_daily_gas))
    with m4:
        st.metric("Total Revenue", format_currency(game.total_revenue, True))
    with m5:
        st.metric("Total CAPEX", format_currency(game.total_capex, True))

    st.markdown("---")

    if game.monthly_history:
        col_chart1, col_chart2 = st.columns(2)

        with col_chart1:
            st.markdown("##### 💵 Cash & Revenue Over Time")
            fig = go.Figure()
            months = [h["label"] for h in game.monthly_history]
            fig.add_trace(go.Scatter(
                x=months, y=[h["cash"] for h in game.monthly_history],
                name="Cash Balance", fill="tozeroy",
                line=dict(color="#d4a017", width=2),
                fillcolor="rgba(212,160,23,0.1)"
            ))
            fig.add_trace(go.Scatter(
                x=months, y=[h["revenue"] for h in game.monthly_history],
                name="Monthly Revenue",
                line=dict(color="#27ae60", width=2)
            ))
            fig.add_trace(go.Scatter(
                x=months, y=[h["opex"] for h in game.monthly_history],
                name="Monthly OPEX",
                line=dict(color="#e74c3c", width=2, dash="dot")
            ))
            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", y=-0.15),
                font=dict(family="Barlow"),
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_chart2:
            st.markdown("##### 🛢️ Production History")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=months, y=[h["oil_production"] for h in game.monthly_history],
                name="Oil (bbl)", marker_color="#d4a017"
            ))
            fig2.add_trace(go.Scatter(
                x=months, y=[h["gas_production"] / 6 for h in game.monthly_history],
                name="Gas (BOE)", line=dict(color="#2d9cdb", width=2),
                yaxis="y"
            ))
            fig2.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                height=350,
                margin=dict(l=0, r=0, t=30, b=0),
                legend=dict(orientation="h", y=-0.15),
                font=dict(family="Barlow"),
                barmode="stack",
            )
            st.plotly_chart(fig2, use_container_width=True)

        # Price chart
        st.markdown("##### 📈 Commodity Price History")
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            x=months, y=[h["wti_price"] for h in game.monthly_history],
            name="WTI ($/bbl)", line=dict(color="#d4a017", width=2)
        ))
        fig3.add_trace(go.Scatter(
            x=months, y=[h["gas_price"] for h in game.monthly_history],
            name="Henry Hub ($/mcf)", line=dict(color="#2d9cdb", width=2),
            yaxis="y2"
        ))
        fig3.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=300,
            margin=dict(l=0, r=50, t=30, b=0),
            legend=dict(orientation="h", y=-0.15),
            font=dict(family="Barlow"),
            yaxis=dict(title="WTI $/bbl"),
            yaxis2=dict(title="Gas $/mcf", overlaying="y", side="right"),
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("👆 Advance the game by clicking **Next Month** in the sidebar to start seeing data.")

# ─── TAB: Wells ───
with tab_wells:
    if not game.wells:
        st.info("No wells yet. Go to **Acquire Leases** to buy your first lease!")
    else:
        for well in game.wells:
            config = BASIN_CONFIGS[well.basin]
            emoji = status_emoji(well.status)
            b_emoji = basin_emoji(well.basin)

            with st.expander(f"{emoji} {well.name} — {well.status.value} | {b_emoji} {well.basin.value}", expanded=(well.status == WellStatus.PRODUCING)):
                info_col, prod_col, econ_col = st.columns(3)

                with info_col:
                    st.markdown("**Well Info**")
                    st.text(f"ID:       {well.id}")
                    st.text(f"Basin:    {well.basin.value}")
                    st.text(f"Acres:    {well.lease_acres}")
                    st.text(f"Status:   {well.status.value}")
                    st.text(f"Lift:     {well.lift_type.value}")
                    if well.status in (WellStatus.PERMITTING, WellStatus.DRILLING,
                                       WellStatus.COMPLETING, WellStatus.FLOWBACK):
                        progress = well.days_in_current_phase / max(well.days_required_current_phase, 1)
                        st.progress(min(progress, 1.0), text=f"{well.status.value}: {well.days_in_current_phase}/{well.days_required_current_phase} days")

                with prod_col:
                    st.markdown("**Production**")
                    if well.status == WellStatus.PRODUCING:
                        st.text(f"Oil Rate:     {well.current_oil_rate:,.0f} bbl/d")
                        st.text(f"Gas Rate:     {well.current_gas_rate:,.0f} mcf/d")
                        st.text(f"Water Rate:   {well.current_water_rate:,.0f} bbl/d")
                        st.text(f"Months Online: {well.months_online}")
                        st.text(f"Cum Oil:      {well.cumulative_oil:,.0f} bbl")
                        st.text(f"Cum Gas:      {well.cumulative_gas:,.0f} mcf")

                        # Mini decline curve
                        if well.months_online > 1:
                            months_range = list(range(0, max(well.months_online + 24, 60)))
                            forecast_oil = [well.ip_oil * well.get_decline_rate(m) for m in months_range]
                            fig_decline = go.Figure()
                            fig_decline.add_trace(go.Scatter(
                                x=months_range, y=forecast_oil,
                                line=dict(color="#d4a017", width=2),
                                fill="tozeroy", fillcolor="rgba(212,160,23,0.1)"
                            ))
                            fig_decline.add_vline(x=well.months_online, line_dash="dash",
                                                  line_color="#e74c3c", annotation_text="Today")
                            fig_decline.update_layout(
                                template="plotly_dark", height=200,
                                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                margin=dict(l=0, r=0, t=20, b=0),
                                xaxis_title="Months", yaxis_title="Oil Rate (bbl/d)",
                                font=dict(family="Barlow", size=10),
                                showlegend=False,
                            )
                            st.plotly_chart(fig_decline, use_container_width=True)
                    else:
                        st.text("Not yet producing")

                with econ_col:
                    st.markdown("**Economics**")
                    st.text(f"Lease Cost:      {format_currency(well.lease_cost)}")
                    st.text(f"Drill Cost:      {format_currency(well.drill_cost)}")
                    st.text(f"Completion Cost: {format_currency(well.completion_cost)}")
                    st.text(f"Facility Cost:   {format_currency(well.facility_cost)}")
                    st.text(f"Total CAPEX:     {format_currency(well.total_capex)}")
                    st.text(f"─────────────────────")
                    st.text(f"Total Revenue:   {format_currency(well.cumulative_revenue)}")
                    st.text(f"Total OPEX:      {format_currency(well.cumulative_opex)}")
                    net = well.cumulative_revenue - well.cumulative_opex - well.total_capex
                    color = "green" if net > 0 else "red"
                    st.markdown(f"**Net Income: :{color}[{format_currency(net)}]**")

# ─── TAB: Acquire Leases ───
with tab_acquire:
    st.markdown("### 🗺️ Select a Basin")
    st.markdown("Choose where to acquire your next lease. Each basin has different risk/reward profiles.")

    basin_cols = st.columns(len(BASIN_CONFIGS))
    for i, (basin_name, config) in enumerate(BASIN_CONFIGS.items()):
        with basin_cols[i]:
            emoji = basin_emoji(basin_name)
            st.markdown(f"""
            <div class="basin-card">
                <h4>{emoji} {basin_name.value}</h4>
                <p style="font-size:0.8rem; color:#bdc3c7;">{config.description}</p>
            </div>
            """, unsafe_allow_html=True)

            st.caption(f"Lease: ${config.lease_cost_per_acre[0]:,}-${config.lease_cost_per_acre[1]:,}/acre")
            st.caption(f"D&C: ${(config.drill_cost[0]+config.completion_cost[0])/1e6:.1f}-${(config.drill_cost[1]+config.completion_cost[1])/1e6:.1f}M")
            st.caption(f"IP Oil: {config.ip_oil[0]:,}-{config.ip_oil[1]:,} bbl/d")
            st.caption(f"IP Gas: {config.ip_gas[0]:,}-{config.ip_gas[1]:,} mcf/d")
            st.caption(f"Risk Factor: {'🔴' * int(config.event_risk_factor * 30)}{'⚪' * (6 - int(config.event_risk_factor * 30))}")

    st.markdown("---")
    st.markdown("### 📝 Acquire New Lease")

    acq_col1, acq_col2 = st.columns(2)
    with acq_col1:
        selected_basin = st.selectbox("Basin", [b.value for b in BasinName])
    with acq_col2:
        well_name = st.text_input("Well Name", value=f"Crude Empire #{len(game.wells) + 1}")

    if st.button("🏷️ Acquire Lease", type="primary", use_container_width=True):
        basin = BasinName(selected_basin)
        well = game.buy_lease(basin, well_name)
        if well:
            st.success(f"✅ Acquired **{well.lease_acres} acres** in {basin.value} for **{format_currency(well.lease_cost)}**!")
            st.info(f"Estimated D&C Budget: **{format_currency(well.drill_cost + well.completion_cost + well.facility_cost)}**")
            st.rerun()
        else:
            st.error("❌ Insufficient funds to acquire this lease!")

# ─── TAB: Operations ───
with tab_operations:
    st.markdown("### 🔧 Well Operations")

    if not game.wells:
        st.info("No wells to operate. Acquire a lease first!")
    else:
        for well in game.wells:
            with st.container():
                op_col1, op_col2, op_col3 = st.columns([2, 1, 1])
                with op_col1:
                    st.markdown(f"**{status_emoji(well.status)} {well.name}** — {well.status.value} ({well.basin.value})")

                with op_col2:
                    # Start drilling
                    if well.status == WellStatus.LEASE_ACQUIRED:
                        est_total = well.drill_cost + well.completion_cost + well.facility_cost
                        if st.button(f"🔨 Start Permitting", key=f"permit_{well.id}"):
                            if game.cash >= est_total:
                                game.start_permitting(well.id)
                                st.success(f"Permitting started for {well.name}!")
                                st.rerun()
                            else:
                                st.error(f"Need ~{format_currency(est_total)} for full D&C. You have {format_currency(game.cash)}.")

                    # Artificial lift
                    if well.status == WellStatus.PRODUCING and well.lift_type == LiftType.NATURAL_FLOW:
                        recommended = well.needs_artificial_lift()
                        if recommended:
                            st.warning(f"⚠️ Consider {recommended.value}")

                with op_col3:
                    # Artificial lift installation
                    if well.status == WellStatus.PRODUCING and well.lift_type == LiftType.NATURAL_FLOW:
                        lift_choice = st.selectbox(
                            "Install Lift",
                            [lt.value for lt in LiftType if lt != LiftType.NATURAL_FLOW],
                            key=f"lift_{well.id}"
                        )
                        if st.button("Install", key=f"install_lift_{well.id}"):
                            lt = LiftType(lift_choice)
                            if game.install_artificial_lift(well.id, lt):
                                st.success(f"Installed {lt.value} on {well.name}!")
                                st.rerun()
                            else:
                                st.error("Insufficient funds!")

                    # Workover
                    if well.status == WellStatus.PRODUCING and well.months_online > 6:
                        if st.button(f"🔧 Workover", key=f"workover_{well.id}"):
                            success, cost = game.perform_workover(well.id)
                            if success:
                                st.success(f"Workover complete on {well.name}! Cost: {format_currency(cost)}")
                                st.rerun()
                            else:
                                st.error(f"Insufficient funds! Need ~{format_currency(cost)}")

                st.markdown("---")

# ─── TAB: Economics ───
with tab_economics:
    st.markdown("### 💰 Financial Summary")

    if not game.monthly_history:
        st.info("Advance the game to see financial data.")
    else:
        e1, e2, e3, e4 = st.columns(4)
        with e1:
            st.metric("Total Revenue", format_currency(game.total_revenue, True))
        with e2:
            st.metric("Total OPEX", format_currency(game.total_opex, True))
        with e3:
            st.metric("Total CAPEX", format_currency(game.total_capex, True))
        with e4:
            net_income = game.total_revenue - game.total_opex - game.total_capex + 10_000_000
            st.metric("Net Income (from $10M)", format_currency(net_income, True),
                      delta=f"{'▲' if net_income > 10_000_000 else '▼'} {format_currency(abs(net_income - 10_000_000), True)}")

        # Well economics table
        st.markdown("##### Well-Level Economics")
        well_data = []
        for w in game.wells:
            net = w.cumulative_revenue - w.cumulative_opex - w.total_capex
            roi = (net / w.total_capex * 100) if w.total_capex > 0 else 0
            well_data.append({
                "Well": w.name,
                "Basin": w.basin.value,
                "Status": w.status.value,
                "CAPEX": format_currency(w.total_capex),
                "Revenue": format_currency(w.cumulative_revenue),
                "OPEX": format_currency(w.cumulative_opex),
                "Net": format_currency(net),
                "ROI": f"{roi:.1f}%",
                "Cum Oil (bbl)": format_number(w.cumulative_oil),
                "Months": w.months_online,
            })
        if well_data:
            st.dataframe(well_data, use_container_width=True, hide_index=True)

        # Event log
        if game.event_log:
            st.markdown("##### 📋 Event History")
            event_data = [{
                "Month": e["label"],
                "Well": e["well"],
                "Event": e["event"],
                "Category": e["category"],
                "Cost": format_currency(abs(e["cost"])),
            } for e in game.event_log[-20:]]  # Last 20 events
            st.dataframe(event_data, use_container_width=True, hide_index=True)

# ─── Footer ───
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#7f8c8d; font-family:'Barlow',sans-serif; font-size:0.8rem;">
    🛢️ <strong>CRUDE EMPIRE</strong> — Oil & Gas Tycoon Simulator<br>
    Prices use real WTI & Henry Hub data when available. Production uses Arps hyperbolic decline curves.<br>
    Built for fun. Not financial advice. <em>Drill baby drill.</em>
</div>
""", unsafe_allow_html=True)
