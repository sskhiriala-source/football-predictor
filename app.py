import streamlit as st, streamlit.components.v1 as components, math

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
    hx = max(.25, (hs*.6+ac*.4)*(1-hf/220)*(1-acs/220)*1.25*max(.55,min(1.65,1+d*1.4))*(1.12 if adv else 1))
    ax = max(.25, (as_*.6+hc*.4)*(1-af/220)*(1-hcs/220)*1.25*max(.55,min(1.65,1-d*1.4))*(.94 if adv else 1))
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
    st.subheader("🎯 Top 3 Correct Scores")
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
    "🏆 Champions League (36)": {"Real Madrid":(2.3,.9,44,8,95),"Man City":(2.4,.9,42,8,95),"Bayern":(2.8,1,40,6,94),"Liverpool":(2.3,.7,50,8,94),"Barcelona":(2.7,1.1,34,6,93),"Inter":(2.1,.7,52,8,92),"Arsenal":(2.1,.7,52,10,92),"PSG":(2.4,.9,44,8,90),"Leverkusen":(2.3,1.2,30,8,89),"Atletico":(1.6,.7,54,16,88),"Dortmund":(2,1.4,24,12,86),"Juventus":(1.4,.6,58,22,86),"AC Milan":(1.8,1.2,32,14,85),"Atalanta":(2.4,1.1,34,10,87),"Aston Villa":(1.7,1.2,28,15,84),"Sporting CP":(2.5,.9,44,8,85),"Benfica":(2.1,1,40,10,83),"PSV":(2.4,1.2,30,10,81),"Feyenoord":(1.9,1.3,26,14,79),"Monaco":(1.8,1,38,14,82),"Lille":(1.6,.9,42,16,81),"Brest":(1.4,1.3,28,22,75),"Leipzig":(1.7,1.1,38,16,83),"Stuttgart":(1.9,1.4,24,14,80),"Girona":(1.4,1.4,25,22,77),"Bologna":(1.3,1.2,32,24,76),"Celtic":(2.2,1.3,30,12,76),"Club Brugge":(1.7,1.2,30,16,75),"Shakhtar":(1.6,1.4,24,18,73),"Salzburg":(1.5,1.6,20,20,72),"Sturm Graz":(1.3,1.6,18,24,69),"Sparta Prague":(1.5,1.5,22,20,71),"Dinamo Zagreb":(1.6,1.7,18,20,70),"Red Star":(1.6,1.8,16,20,69),"Young Boys":(1.2,1.9,14,28,67),"Slovan":(1.1,2.2,10,32,64)},
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": {"Arsenal":(2.1,.7,52,10,92),"Man City":(2.4,.9,42,8,95),"Liverpool":(2.3,.7,50,8,94),"Chelsea":(2,1.1,30,12,87),"Aston Villa":(1.7,1.2,28,15,84),"Newcastle":(1.7,1.1,32,16,84),"Tottenham":(2,1.4,22,10,84),"Man United":(1.4,1.2,30,22,82),"Brighton":(1.7,1.3,25,16,81),"Nottm Forest":(1.4,1,38,22,80)},
    "🇪🇸 La Liga": {"Real Madrid":(2.3,.9,44,8,95),"Barcelona":(2.7,1.1,34,6,93),"Atletico":(1.6,.7,54,16,88),"Bilbao":(1.6,.9,42,18,84),"Villarreal":(1.9,1.5,22,12,82),"Sociedad":(1.2,.9,44,28,81),"Betis":(1.3,1.1,34,24,79),"Sevilla":(1.2,1.4,24,28,75)},
    "🇮🇹 Serie A": {"Inter":(2.1,.7,52,8,92),"Atalanta":(2.4,1.1,34,10,87),"Napoli":(1.8,.7,54,14,88),"Juventus":(1.4,.6,58,22,86),"AC Milan":(1.8,1.2,32,14,85),"Lazio":(1.8,1.2,30,15,83),"Fiorentina":(1.8,.9,42,15,83),"AS Roma":(1.3,1.4,26,26,78)},
    "🇩🇪 Bundesliga": {"Bayern":(2.8,1,40,6,94),"Leverkusen":(2.3,1.2,30,8,89),"Frankfurt":(2.1,1.3,28,10,84),"Leipzig":(1.7,1.1,38,16,83),"Dortmund":(2,1.4,24,12,86),"Stuttgart":(1.9,1.4,24,14,80)},
    "🇫🇷 Ligue 1": {"PSG":(2.4,.9,44,8,90),"Monaco":(1.8,1,38,14,82),"Marseille":(2,1.2,30,12,82),"Lille":(1.6,.9,42,16,81),"Lyon":(1.8,1.3,26,15,80),"Nice":(1.7,1.1,34,18,79)},
    "🇹🇳 Tunisia & CAF": {"Esperance":(1.9,.6,56,10,82),"Club Africain":(1.5,.6,56,18,78),"Etoile Sahel":(1.4,.8,45,20,76),"CS Sfaxien":(1.1,.8,46,28,73),"US Monastir":(1.4,.7,50,20,76),"Al Ahly":(2.1,.6,58,10,85),"Sundowns":(2,.6,56,12,84)}
}

st.title("🎯 Match Predictor PRO")
lg = st.selectbox("Competition:", list(DB.keys()))
t = sorted(DB[lg].keys())
hn = st.selectbox("Home Team:", t, 0)
an = st.selectbox("Away Team:", t, 1)
adv = st.checkbox("Home Advantage", True)
if hn != an: run(hn, an, *DB[lg][hn], *DB[lg][an], adv)
