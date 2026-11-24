import streamlit as st, streamlit.components.v1 as components, math, json, os

st.set_page_config(page_title="Predictor PRO", page_icon="🎯", layout="centered")
components.html('<script>setInterval(()=>{window.parent.document.querySelectorAll(\'input[role="combobox"]\').forEach(e=>{e.setAttribute("readonly",1);e.setAttribute("inputmode","none")})},400)</script>', height=0)

st.markdown("""<style>
.stApp{background:linear-gradient(160deg,#070b14,#0d192b,#061714);color:#f8fafc}
header{background:transparent!important}
.box{border-radius:12px;padding:10px;text-align:center;margin-bottom:8px}
.g{background:rgba(16,185,129,.22);border:1.5px solid #10b981;color:#34d399}
.y{background:rgba(245,158,11,.18);border:1.5px solid #f59e0b;color:#fbbf24}
.r{background:rgba(239,68,68,.18);border:1.5px solid #ef4444;color:#f87171}
.b{background:rgba(59,130,246,.2);border:1.5px solid #3b82f6;color:#60a5fa}
.v{font-size:21px;font-weight:900}
label,h1,h2,h3,p{color:#f1f5f9!important}
</style>""", unsafe_allow_html=True)

def card(t, v, pct, force=None):
    c = force or ("g" if pct >= 55 else ("y" if pct >= 35 else "r"))
    st.markdown(f'<div class="box {c}"><div style="font-size:12px;color:#e2e8f0">{t}</div><div class="v">{v}</div></div>', unsafe_allow_html=True)

def run(hn, an, hs, hc, hcs, hf, hp, as_, ac, acs, af, ap, adv):
    d = (hp - ap) / 100
    hx = max(.25, min(3.2, (hs*.55+ac*.45)*(1-hf/240)*(1-acs/240)*max(.6,min(1.5,1+d*1.1))*(1.08 if adv else 1)))
    ax = max(.25, min(3.2, (as_*.55+hc*.45)*(1-af/240)*(1-hcs/240)*max(.6,min(1.5,1-d*1.1))*(.95 if adv else 1)))
    sc, tot, w1, dr, w2, o25, by = {}, 0, 0, 0, 0, 0, 0
    for i in range(11):
        for j in range(11):
            tau = 1-(hx*ax*-.04) if i==0 and j==0 else (1+hx*-.04 if i==0 and j==1 else (1+ax*-.04 if i==1 and j==0 else (1.04 if i==1 and j==1 else 1)))
            p = max(0, (hx**i*math.exp(-hx)/math.factorial(i))*(ax**j*math.exp(-ax)/math.factorial(j))*tau)
            sc[f"{i} - {j}"] = p; tot += p
            if i > j: w1 += p
            elif i == j: dr += p
            else: w2 += p
            if i + j > 2.5: o25 += p
            if i > 0 and j > 0: by += p
        top3 = sorted(sc.items(), key=lambda item: item, reverse=True)[:3]
    st.subheader(f"🎯 Top 3 Correct Scores (xG: {hx:.2f} - {ax:.2f})")
    cols = st.columns(3)
    for k, (s, p) in enumerate(top3):
        with cols[k]: card(["🥇 #1","🥈 #2","🥉 #3"][k], f"{s} ({p/tot*100:.1f}%)", 0, "g" if k==0 else "b")
    st.subheader("🏆 Match Result (1 X 2)")
    m1, m2, m3 = st.columns(3)
    with m1: card(f"1 ({hn[:10]})", f"{w1/tot*100:.1f}%", w1/tot*100)
    with m2: card("X (Draw)", f"{dr/tot*100:.1f}%", dr/tot*100)
    with m3: card(f"2 ({an[:10]})", f"{w2/tot*100:.1f}%", w2/tot*100)
    st.subheader("⚽ Goals & BTTS")
    g1, g2 = st.columns(2)
    with g1: card("Over 2.5", f"{o25/tot*100:.1f}%", o25/tot*100)
    with g2: card("Under 2.5", f"{100-o25/tot*100:.1f}%", 100-o25/tot*100)
    b1, b2 = st.columns(2)
    with b1: card("BTTS: Yes", f"{by/tot*100:.1f}%", by/tot*100)
    with b2: card("BTTS: No", f"{100-by/tot*100:.1f}%", 100-by/tot*100)

DB = json.load(open("leagues.json", encoding="utf-8")) if os.path.exists("leagues.json") else {"🏆 UCL 2026/2027": {"Real Madrid":[3.25,1.75,30,5,95],"PSG":[3.5,1.25,40,5,96]}}
st.title("🎯 Match Predictor PRO")
lg = st.selectbox("Competition:", list(DB.keys()))
t = sorted(DB[lg].keys())
hn = st.selectbox("Home Team:", t, 0)
an = st.selectbox("Away Team:", t, 1 if len(t)>1 else 0)
adv = st.checkbox("Home Advantage", True)
if hn != an: run(hn, an, *DB[lg][hn], *DB[lg][an], adv)
