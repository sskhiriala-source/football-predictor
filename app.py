import streamlit as st, streamlit.components.v1 as components, math

st.set_page_config(page_title="Predictor PRO 26/27", page_icon="🎯", layout="centered")
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
    hx = max(.25, (hs*.6+ac*.4)*(1-hf/220)*(1-acs/220)*1.15*max(.55,min(1.65,1+d*1.3))*(1.10 if adv else 1))
    ax = max(.25, (as_*.6+hc*.4)*(1-af/220)*(1-hcs/220)*1.15*max(.55,min(1.65,1-d*1.3))*(.94 if adv else 1))
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
    top3 = sorted(sc.items(), key=lambda x: x[1], reverse=True)[:3]
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

DB = {
    "🏆 UCL 2026/2027 (36 Teams)": {
        "PSG":(3.5,1.25,40,5,96),"Real Madrid":(3.25,1.75,30,5,95),"Aston Villa":(2.4,1.2,40,20,90),"Arsenal":(2.0,.75,55,10,93),
        "Como":(3.4,1.5,30,10,88),"Barcelona":(3.5,1.5,30,5,94),"Manchester City":(3.0,1.75,30,8,94),"Liverpool":(3.5,2.5,20,8,92),
        "Club Brugge KV":(2.75,1.75,28,12,86),"Sporting CP":(2.0,1.0,45,12,88),"Betis":(2.0,1.5,32,15,86),"Dortmund":(1.75,1.25,38,15,87),
        "Bayern Munich":(3.0,1.25,40,8,93),"Stuttgart":(1.75,1.0,45,15,85),"LASK":(2.0,1.8,35,20,81),"Galatasaray":(1.6,1.8,35,20,82),
        "Inter":(2.0,1.5,35,12,89),"Manchester Utd":(2.0,2.0,25,12,85),"Fenerbahce":(1.5,2.75,18,20,79),"Bodo/Glimt":(0.8,1.8,35,30,78),
        "AS Roma":(2.5,2.0,22,12,82),"Shakhtar Donetsk":(1.0,1.0,45,25,80),"Viking":(2.25,2.5,18,15,77),"Atl. Madrid":(1.0,1.25,42,25,84),
        "PSV":(0.75,1.0,45,30,81),"FC Porto":(1.5,1.75,28,20,80),"Napoli":(1.5,2.75,18,22,80),"Villarreal":(2.0,3.5,12,15,79),
        "AEK Athens":(1.25,2.75,18,25,75),"RB Leipzig":(1.25,2.75,18,25,79),"Sabah FC":(1.0,2.5,20,30,72),"Feyenoord":(1.0,2.75,18,30,76),
        "Lens":(1.0,4.0,10,32,74),"Slavia Prague":(1.25,2.25,22,25,73),"Lille":(1.0,2.5,20,30,74),"Slovan Bratislava":(0.25,4.25,8,75,65)
    },
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {"Arsenal":(2.1,.7,52,10,93),"Manchester City":(2.5,1.1,40,8,94),"Liverpool":(2.6,1.2,38,8,93),"Aston Villa":(2.1,1.1,40,12,89),"Chelsea":(2.0,1.1,32,12,87),"Newcastle":(1.7,1.1,32,16,84),"Tottenham":(2.0,1.4,22,10,84),"Manchester Utd":(1.7,1.4,28,16,84)},
    "🇪🇸 La Liga": {"Real Madrid":(2.6,1.1,40,6,95),"Barcelona":(2.8,1.2,34,6,94),"Atl. Madrid":(1.5,.8,50,18,86),"Betis":(1.8,1.2,34,15,85),"Villarreal":(1.9,1.8,20,14,81),"Athletic Bilbao":(1.6,.9,42,18,84)},
    "🇮🇹 Serie A": {"Inter":(2.1,.9,46,10,91),"Como":(2.4,1.3,32,10,86),"Atalanta":(2.3,1.1,34,10,87),"Juventus":(1.5,.6,56,20,86),"AC Milan":(1.8,1.2,32,14,85),"Napoli":(1.6,1.3,30,18,83),"AS Roma":(1.8,1.5,25,15,82)},
    "🇩🇪 Bundesliga": {"Bayern Munich":(2.9,1.0,42,6,94),"Leverkusen":(2.3,1.2,30,8,89),"Dortmund":(1.9,1.2,32,12,87),"Stuttgart":(1.8,1.1,38,14,85),"RB Leipzig":(1.6,1.4,26,18,82)},
    "🇫🇷 Ligue 1": {"PSG":(2.8,.9,45,6,95),"Monaco":(1.8,1.0,38,14,83),"Marseille":(2.0,1.2,30,12,82),"Lille":(1.4,1.4,28,22,79),"Lens":(1.3,1.6,22,25,77)},
    "🇹🇳 Tunisia & CAF": {"Esperance":(1.9,.6,56,10,82),"Club Africain":(1.5,.6,56,18,78),"Etoile Sahel":(1.4,.8,45,20,76),"CS Sfaxien":(1.1,.8,46,28,73),"US Monastir":(1.4,.7,50,20,76),"Al Ahly":(2.1,.6,58,10,85),"Sundowns":(2,.6,56,12,84)}
}

st.title("🎯 Match Predictor PRO")
lg = st.selectbox("Competition:", list(DB.keys()))
t = sorted(DB[lg].keys())
hn = st.selectbox("Home Team:", t, 0)
an = st.selectbox("Away Team:", t, 1)
adv = st.checkbox("Home Advantage", True)
if hn != an: run(hn, an, *DB[lg][hn], *DB[lg][an], adv)
