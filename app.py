import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="NIFTY SCANNER PRO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

IST = ZoneInfo("Asia/Kolkata")

st.markdown("""
<style>
.block-container {padding-top: 1.1rem; padding-bottom: 2rem; max-width: 1200px;}
[data-testid="stMetric"] {background: rgba(120,120,120,.08); padding: 12px; border-radius: 12px;}
div[data-testid="stDataFrame"] {border-radius: 10px;}
.small-note {font-size: .86rem; opacity: .78;}
.signal-buy {padding: 12px; border-radius: 12px; background: rgba(22,163,74,.10); border: 1px solid rgba(22,163,74,.35);}
.signal-watch {padding: 12px; border-radius: 12px; background: rgba(234,179,8,.10); border: 1px solid rgba(234,179,8,.35);}
.signal-none {padding: 12px; border-radius: 12px; background: rgba(120,120,120,.10); border: 1px solid rgba(120,120,120,.25);}
</style>
""", unsafe_allow_html=True)

st.title("📈 NIFTY SCANNER PRO")
st.caption("V1.0 · 5-minute option scanner dashboard · Signal-only · No orders are placed")

now = datetime.now(IST)
st.caption(f"Dashboard time: {now.strftime('%d %b %Y, %I:%M:%S %p')} IST")

with st.sidebar:
    st.header("Scanner Settings")
    mode = st.radio("Data mode", ["Demo preview", "Manual market data"])
    st.selectbox("Expiry coverage", ["Current + Next expiry", "Current expiry only", "Next expiry only"])
    st.selectbox("Scan interval", ["5 minutes"])
    st.number_input("Volume spike threshold (x)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
    st.number_input("Minimum score for candidate (out of 5)", min_value=1, max_value=5, value=4)
    st.info("Groww live API is not connected in V1.0. No live price or trade signal is claimed.")

st.warning("DEMO / PROTOTYPE MODE — નીચેના ઉદાહરણના આંકડા વાસ્તવિક Live Market Data નથી. આ ડેટા પરથી ટ્રેડ ન કરશો.")

tab_overview, tab_current, tab_next, tab_manual, tab_rules = st.tabs([
    "Overview", "Current Expiry", "Next Expiry", "Manual Scanner", "Rules & Risk"
])

# Explicitly illustrative demo data, not current market quotes.
demo = pd.DataFrame([
    ["Current", "CE", 25200, 192.90, 1.65, 2.1, 1.2, 0.6, 3, "WATCH"],
    ["Current", "PE", 25200, 146.00, 2.25, 3.4, 2.0, 0.7, 4, "CANDIDATE"],
    ["Current", "CE", 25250, 166.50, 1.25, 1.0, 0.8, 0.5, 2, "NO TRADE"],
    ["Current", "PE", 25250, 170.85, 2.05, 2.8, 1.6, 0.8, 4, "CANDIDATE"],
    ["Current", "CE", 25300, 143.55, 1.10, -0.8, 1.1, 0.6, 2, "NO TRADE"],
    ["Next", "CE", 25200, 205.00, 1.40, 1.2, 0.5, 0.9, 2, "NO TRADE"],
    ["Next", "PE", 25200, 158.00, 1.90, 2.1, 1.2, 0.7, 3, "WATCH"],
    ["Next", "CE", 25250, 180.00, 2.20, 2.7, 1.8, 0.6, 4, "CANDIDATE"],
    ["Next", "PE", 25250, 175.00, 1.30, -0.5, 0.9, 0.8, 2, "NO TRADE"],
], columns=["Expiry", "Type", "Strike", "Premium ₹", "Volume Spike x", "Premium 5m %", "OI 5m %", "Spread %", "Score / 5", "Status"])

def enrich(df):
    out = df.copy()
    out["Entry ₹"] = out["Premium ₹"].round(2)
    out["Stop Loss ₹"] = (out["Premium ₹"] * 0.80).round(2)
    out["Target 1 ₹"] = (out["Premium ₹"] * 1.30).round(2)
    out["Target 2 ₹"] = (out["Premium ₹"] * 1.40).round(2)
    return out

def show_table(df):
    cols = ["Type", "Strike", "Premium ₹", "Volume Spike x", "Premium 5m %", "OI 5m %", "Spread %", "Score / 5", "Status"]
    st.dataframe(df[cols], use_container_width=True, hide_index=True)

with tab_overview:
    st.subheader("Market Scanner Overview")
    a,b,c,d = st.columns(4)
    a.metric("Expiry Coverage", "2")
    b.metric("Contracts Watched", "14*", help="Target structure: 7 CE + 7 PE per expiry")
    c.metric("Scan Interval", "5 min")
    d.metric("Data Connection", "Not connected")
    st.caption("*Prototype sample rows are illustrative; actual 14-strike live scan will be enabled after data integration.")
    left, right = st.columns(2)
    with left:
        st.markdown("#### Current Expiry · Top candidates")
        cur = demo[demo["Expiry"] == "Current"].sort_values(["Score / 5","Volume Spike x"], ascending=False)
        show_table(cur.head(3))
    with right:
        st.markdown("#### Next Expiry · Top candidates")
        nxt = demo[demo["Expiry"] == "Next"].sort_values(["Score / 5","Volume Spike x"], ascending=False)
        show_table(nxt.head(3))
    st.markdown("#### Status")
    st.info("Live connection pending. Candidate labels shown in Demo Preview are examples only, not actionable trading recommendations.")

with tab_current:
    st.subheader("Current Expiry")
    st.caption("Illustrative sample only — replace with real completed 5-minute readings.")
    cur = enrich(demo[demo["Expiry"] == "Current"])
    show_table(cur)
    st.markdown("**Risk levels shown below are placeholders for interface testing only.**")
    st.dataframe(cur[["Type","Strike","Entry ₹","Stop Loss ₹","Target 1 ₹","Target 2 ₹"]], use_container_width=True, hide_index=True)

with tab_next:
    st.subheader("Next Expiry")
    st.caption("Illustrative sample only — actual next expiry will be selected from Groww instrument data.")
    nxt = enrich(demo[demo["Expiry"] == "Next"])
    show_table(nxt)
    st.dataframe(nxt[["Type","Strike","Entry ₹","Stop Loss ₹","Target 1 ₹","Target 2 ₹"]], use_container_width=True, hide_index=True)

with tab_manual:
    st.subheader("Manual Data Entry")
    st.write("Growwમાંથી વાંચેલા આંકડા દાખલ કરીને સ્કોરિંગનું પરીક્ષણ કરો. આ Live API નથી.")
    template = pd.DataFrame([
        {"Expiry":"Current","Type":"CE","Strike":25200,"Premium ₹":100.0,"Volume Spike x":2.0,"Premium 5m %":1.5,"OI 5m %":1.0,"Spread %":0.8,"NIFTY direction":"UP"},
        {"Expiry":"Current","Type":"PE","Strike":25200,"Premium ₹":100.0,"Volume Spike x":2.0,"Premium 5m %":1.5,"OI 5m %":1.0,"Spread %":0.8,"NIFTY direction":"DOWN"},
    ])
    edited = st.data_editor(template, num_rows="dynamic", use_container_width=True, hide_index=True)
    if st.button("Analyze Manual Readings", type="primary"):
        results=[]
        for _, r in edited.iterrows():
            score=0; reasons=[]
            if float(r["Volume Spike x"]) >= 2:
                score += 1; reasons.append("Volume spike")
            if float(r["Premium 5m %"]) > 0:
                score += 1; reasons.append("Premium rising")
            if float(r["OI 5m %"]) > 0:
                score += 1; reasons.append("OI rising (not proof of buying)")
            direction=str(r["NIFTY direction"]).upper()
            if (r["Type"]=="CE" and direction=="UP") or (r["Type"]=="PE" and direction=="DOWN"):
                score += 1; reasons.append("Underlying direction agrees")
            if float(r["Spread %"]) <= 1.5:
                score += 1; reasons.append("Spread within filter")
            label = "CANDIDATE — verify manually" if score >= 4 else "WATCH" if score == 3 else "NO TRADE"
            p=float(r["Premium ₹"])
            results.append({
                "Expiry":r["Expiry"],"Type":r["Type"],"Strike":r["Strike"],
                "Score / 5":score,"Status":label,"Entry reference ₹":round(p,2),
                "Illustrative SL ₹":round(p*.80,2),
                "Illustrative T1 ₹":round(p*1.30,2),
                "Illustrative T2 ₹":round(p*1.40,2),
                "Reasons":", ".join(reasons)
            })
        st.dataframe(pd.DataFrame(results), use_container_width=True, hide_index=True)
        st.warning("આ સ્કોરિંગ પ્રોટોટાઇપ છે. SL/Targets માત્ર UI માટેના ઉદાહરણ છે; live trading માટે માન્ય કે backtested નથી.")

with tab_rules:
    st.subheader("Scanner Rules & Risk")
    st.markdown("""
**Proposed screening rules (to be validated in paper trading):**
- 5-minute volume spike: current completed candle volume ÷ average of previous 3 completed candles.
- Premium momentum: completed 5-minute premium change.
- OI change: context only; rising OI does not identify whether buyer or seller is aggressive.
- Underlying direction: NIFTY price action / VWAP confirmation.
- Liquidity: bid-ask spread filter.
- Score 4/5 or higher means a candidate for manual review, not an automatic BUY instruction.

**Risk controls**
- No order placement or broker execution.
- No guaranteed signals or returns.
- Stop-loss and targets must be validated with historical testing and paper trading.
- Avoid signals from incomplete candles and stale quotes.
- Expiry-day gamma/theta and slippage can make option premiums move sharply.
""")
    st.markdown("**Live integration requirements**")
    st.write("1. Active Groww plan with required market-data entitlements.")
    st.write("2. Groww API authentication stored as cloud secrets, never in code.")
    st.write("3. Verified option-chain, quote and historical-candle endpoint schemas.")
    st.write("4. Scheduler, logging, stale-data checks and failure alerts.")

st.divider()
st.caption("NIFTY SCANNER PRO V1.0 · Prototype only · Not investment advice · No live feed connected")
