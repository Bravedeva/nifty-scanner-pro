import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(page_title="NIFTY SCANNER PRO", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")
IST = ZoneInfo("Asia/Kolkata")

st.markdown("""
<style>
.block-container {padding-top:1rem;padding-bottom:2rem;max-width:1250px}
[data-testid="stMetric"] {background:rgba(120,120,120,.08);padding:12px;border-radius:12px}
.small-note {font-size:.86rem;opacity:.8}
</style>
""", unsafe_allow_html=True)

st.title("📈 NIFTY SCANNER PRO")
st.caption("V1.1 · Risk tools + CSV analysis + paper-trading journal · Signal-only · No orders placed")
st.caption(f"Dashboard time: {datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p')} IST")
st.warning("DEMO / OFFLINE MODE — Groww Live Market Data જોડાયેલું નથી. CSV અથવા દાખલ કરેલા આંકડા જ વિશ્લેષણમાં વપરાય છે. આઉટપુટ ટ્રેડ ભલામણ નથી.")

with st.sidebar:
    st.header("મોડ")
    st.info("હાલનું સંસ્કરણ Live API વિના કાર્ય કરે છે. Groww API Token / TOTP અહીં દાખલ કરશો નહીં.")
    st.caption("Live feed માટે અલગથી યોગ્ય Groww Market Data entitlement અને verified API integration જરૂરી રહેશે.")

tabs = st.tabs(["Overview", "CSV Scanner", "Risk Calculator", "Paper Trading Journal", "Rules & Safety"])

# Demo data is deliberately synthetic and never presented as live market data.
demo = pd.DataFrame([
    ["Current", "CE", 25200, 192.90, 1.65, 2.1, 1.2, 0.6],
    ["Current", "PE", 25200, 146.00, 2.25, 3.4, 2.0, 0.7],
    ["Current", "CE", 25250, 166.50, 1.25, 1.0, 0.8, 0.5],
    ["Current", "PE", 25250, 170.85, 2.05, 2.8, 1.6, 0.8],
    ["Next", "CE", 25200, 205.00, 1.40, 1.2, 0.5, 0.9],
    ["Next", "PE", 25200, 158.00, 1.90, 2.1, 1.2, 0.7],
], columns=["Expiry", "Type", "Strike", "Premium", "VolumeSpike", "Premium5mPct", "OI5mPct", "SpreadPct"])

def score_rows(df):
    out = df.copy()
    for c in ["Premium", "VolumeSpike", "Premium5mPct", "OI5mPct", "SpreadPct"]:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    out = out.dropna(subset=["Premium", "VolumeSpike", "Premium5mPct", "OI5mPct", "SpreadPct"])
    score=[]; reasons=[]; labels=[]
    for _, r in out.iterrows():
        pts=0; why=[]
        if r.VolumeSpike >= 2: pts+=1; why.append("Volume spike")
        if r.Premium5mPct > 0: pts+=1; why.append("Premium rising")
        if r.OI5mPct > 0: pts+=1; why.append("OI rising (direction not confirmed)")
        if r.SpreadPct <= 1.5: pts+=1; why.append("Spread filter passed")
        if pts>=4: label="REVIEW CANDIDATE"
        elif pts==3: label="WATCH"
        else: label="NO SETUP"
        score.append(pts); reasons.append(", ".join(why)); labels.append(label)
    out["Score / 4"]=score; out["Screening Status"]=labels; out["Factors"]=reasons
    return out.sort_values(["Score / 4", "VolumeSpike"], ascending=False)

with tabs[0]:
    st.subheader("Dashboard Overview")
    c1,c2,c3,c4=st.columns(4)
    c1.metric("Data connection", "Offline")
    c2.metric("Scan interval target", "5 min")
    c3.metric("Expiry view", "Current + Next")
    c4.metric("Order execution", "Disabled")
    st.info("આ પેજમાં દેખાતા નમૂનાના આંકડા કલ્પિત છે. વાસ્તવિક બજાર ભાવ નથી.")
    st.markdown("**ઉપલબ્ધ સાધનો**")
    st.markdown("- CSV Scanner: એકસાથે અનેક CE/PE પંક્તિઓનું સ્ક્રીનિંગ\n- Risk Calculator: નક્કી કરેલી મહત્તમ નુકસાની પ્રમાણે quantity\n- Paper Trading Journal: પ્રેક્ટિસ ટ્રેડની નોંધ અને CSV export")
    st.dataframe(score_rows(demo), use_container_width=True, hide_index=True)

with tabs[1]:
    st.subheader("CSV Scanner")
    st.write("તમારી પાસે option-chain / candle dataની CSV હોય તો અપલોડ કરો. આ ટૂલ CSVમાં રહેલા ડેટા પરથી જ સ્કોર આપે છે; તે પોતે Growwમાંથી ડેટા ખેંચતું નથી.")
    st.caption("જરૂરી કૉલમ: Type, Strike, Premium, VolumeSpike, Premium5mPct, OI5mPct, SpreadPct. Expiry વૈકલ્પિક છે.")
    uploaded=st.file_uploader("CSV ફાઇલ પસંદ કરો", type=["csv"], key="csvscan")
    if uploaded:
        try:
            raw=pd.read_csv(uploaded)
            if "Expiry" not in raw.columns: raw["Expiry"]="Unknown"
            required=["Type","Strike","Premium","VolumeSpike","Premium5mPct","OI5mPct","SpreadPct"]
            missing=[x for x in required if x not in raw.columns]
            if missing:
                st.error("આ કૉલમ ખૂટે છે: " + ", ".join(missing))
            else:
                result=score_rows(raw)
                st.success(f"{len(result)} પંક્તિઓનું વિશ્લેષણ થયું.")
                st.dataframe(result, use_container_width=True, hide_index=True)
                st.download_button("વિશ્લેષણ CSV ડાઉનલોડ કરો", result.to_csv(index=False).encode("utf-8-sig"), "nifty_scan_results.csv", "text/csv")
        except Exception as e:
            st.error(f"CSV વાંચવામાં સમસ્યા: {e}")
    with st.expander("CSV નમૂનો જુઓ"):
        st.dataframe(demo, use_container_width=True, hide_index=True)
        st.download_button("નમૂનાની CSV ડાઉનલોડ કરો", demo.to_csv(index=False).encode("utf-8-sig"), "nifty_scanner_template.csv", "text/csv")

with tabs[2]:
    st.subheader("Risk Calculator")
    st.write("આ ગણતરી માત્ર position sizing માટે છે. તે કોઈ ટ્રેડ લેવાની સલાહ નથી.")
    a,b=st.columns(2)
    with a:
        capital=st.number_input("ટ્રેડિંગ મૂડી (₹)", min_value=1000.0, value=25000.0, step=1000.0)
        risk_pct=st.number_input("એક ટ્રેડમાં મહત્તમ જોખમ (%)", min_value=0.1, max_value=5.0, value=1.0, step=0.1)
        entry=st.number_input("Option Entry Premium (₹)", min_value=0.05, value=100.0, step=1.0)
    with b:
        sl=st.number_input("Stop Loss Premium (₹)", min_value=0.05, value=80.0, step=1.0)
        lot=st.number_input("એક Lotમાં Units", min_value=1, value=25, step=1)
        charges=st.number_input("અંદાજિત કુલ ખર્ચ પ્રતિ Lot (₹)", min_value=0.0, value=60.0, step=10.0)
    risk_cash=capital*risk_pct/100
    loss_per_unit=max(0.0, entry-sl)
    loss_per_lot=loss_per_unit*lot+charges
    lots=int(risk_cash//loss_per_lot) if loss_per_lot>0 else 0
    x,y,z=st.columns(3)
    x.metric("મહત્તમ જોખમ", f"₹{risk_cash:,.2f}")
    y.metric("અંદાજિત નુકસાન / Lot", f"₹{loss_per_lot:,.2f}")
    z.metric("જોખમ મર્યાદામાં Lots", str(lots))
    if sl>=entry: st.error("Stop Loss premium, Entry કરતાં ઓછું હોવું જોઈએ.")
    elif lots==0: st.warning("આ માપદંડ મુજબ એક Lot પણ જોખમ મર્યાદામાં ફિટ થતો નથી. ટ્રેડ ટાળો અથવા જોખમ/કદ ફરી તપાસો.")
    else: st.success(f"ગણિત મુજબ મહત્તમ {lots} Lot (કુલ {lots*lot} units). Slippage અને વાસ્તવિક chargesથી નુકસાન વધી શકે છે.")
    st.caption("Lot size દરેક expiry/contract માટે exchange instrument મુજબ ચકાસો. આ કૅલ્ક્યુલેટર lot size આપમેળે અપડેટ કરતું નથી.")

with tabs[3]:
    st.subheader("Paper Trading Journal")
    st.write("અહીં પ્રેક્ટિસ ટ્રેડ નોંધો. કોઈ વાસ્તવિક order મૂકાતો નથી. આ નોંધો હાલના browser session પૂરતી છે.")
    with st.form("paper_form"):
        p1,p2,p3=st.columns(3)
        with p1:
            trade_date=st.date_input("તારીખ", value=datetime.now(IST).date())
            opt_type=st.selectbox("પ્રકાર", ["CE","PE"])
            strike=st.number_input("Strike", min_value=1, value=25200, step=50)
        with p2:
            entry_p=st.number_input("Entry Premium ₹", min_value=0.05, value=100.0, step=1.0)
            exit_p=st.number_input("Exit Premium ₹", min_value=0.0, value=110.0, step=1.0)
            units=st.number_input("Units", min_value=1, value=25, step=1)
        with p3:
            fees=st.number_input("કુલ Charges ₹", min_value=0.0, value=40.0, step=5.0)
            note=st.text_input("નોંધ (વૈકલ્પિક)")
        save=st.form_submit_button("Paper Trade ઉમેરો")
    if "paper_trades" not in st.session_state:
        st.session_state.paper_trades=[]
    if save:
        pnl=(exit_p-entry_p)*units-fees
        st.session_state.paper_trades.append({"Date":str(trade_date),"Type":opt_type,"Strike":int(strike),"Entry ₹":entry_p,"Exit ₹":exit_p,"Units":int(units),"Charges ₹":fees,"Net P/L ₹":round(pnl,2),"Note":note})
        st.success(f"Paper trade નોંધાયો. Net P/L: ₹{pnl:,.2f}")
    if st.session_state.paper_trades:
        journal=pd.DataFrame(st.session_state.paper_trades)
        st.dataframe(journal, use_container_width=True, hide_index=True)
        total=journal["Net P/L ₹"].sum()
        st.metric("કુલ Paper P/L", f"₹{total:,.2f}")
        st.download_button("Journal CSV ડાઉનલોડ કરો", journal.to_csv(index=False).encode("utf-8-sig"), "paper_trading_journal.csv", "text/csv")
        if st.button("આ sessionની નોંધો સાફ કરો"):
            st.session_state.paper_trades=[]
            st.rerun()
    else:
        st.info("હજુ કોઈ Paper Trade નોંધાયો નથી.")

with tabs[4]:
    st.subheader("Rules & Safety")
    st.markdown("""
**CSV સ્ક્રીનિંગના નિયમો**
- Volume Spike ≥ 2x: એક સ્કોર
- Premium 5-minute change > 0: એક સ્કોર
- OI 5-minute change > 0: એક સ્કોર; OIથી buyer કે sellerની દિશા એકલી નક્કી થતી નથી
- Bid-ask spread ≤ 1.5%: એક સ્કોર
- 4/4 = વધુ તપાસ માટેનો ઉમેદવાર; BUY સૂચના નહીં

**જોખમ નિયંત્રણ**
- કોઈ automatic order placement નથી.
- અધૂરી candle અથવા જૂના quote પરથી નિર્ણય ન લેવો.
- Optionમાં slippage, theta અને expiry-day volatilityનું જોખમ ઊંચું હોઈ શકે છે.
- Paper trading અને પૂરતી backtesting વિના live trade signal સક્રિય ન કરવો.

**Live integration માટે પછી જરૂરી રહેશે**
- Growwમાં યોગ્ય Market Data entitlement
- અધિકૃત અને ચકાસેલા API endpoints / schemas
- Cloud secretsમાં સુરક્ષિત credentials
- 5-minute scheduler, logging, stale-data checks અને failure alerts
""")

st.divider()
st.caption("NIFTY SCANNER PRO V1.1 · Offline tools only · No Groww live feed · No orders placed · Not investment advice")
