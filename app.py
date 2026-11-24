import streamlit as st
import math

st.set_page_config(page_title="Correct Score PRO", page_icon="🎯", layout="centered")

st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { direction: ltr; text-align: left; background: linear-gradient(160deg, #070b14 0%, #0d192b 50%, #061714 100%); color: #f8fafc; }
header[data-testid="stHeader"] { background: transparent; }
.hero { background: rgba(255,255,255,0.05); border: 1px solid #10b981; border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 18px; }
.hero-t { font-size: 22px; font-weight: 900; color: #34d399; margin: 0; }
.team-box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 12px; }
.cs-card { border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 10px; }
.cs-1 { background: rgba(16,185,129,0.22); border: 2px solid #10b981; }
.cs-2 { background: rgba(59,130,246,0.18); border: 1.5px solid #3b82f6; }
.cs-3 { background: rgba(245,158,11,0.15); border: 1.5px solid #f59e0b; }
.cs-sc { font-size: 28px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.s-green { background: rgba(16,185,129,0.2); border: 1.5px solid #10b981; color: #34d399; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.s-yellow { background: rgba(245,158,11,0.2); border: 1.5px solid #f59e0b; color: #fbbf24; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.s-red { background: rgba(239,68,68,0.2); border: 1.5px solid #ef4444; color: #f87171; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.stButton > button { background: linear-gradient(90deg, #10b981, #059669) !important; color: white !important; font-weight: 800 !important; font-size: 16px !important; border-radius: 12px !important; padding: 12px !important; }
label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
<div class="hero"><div class="hero-t">🎯 Correct Score Predictor PRO</div><div style="color:#94a3b8;font-size:12px;">Full UCL 36 Teams • Dixon-Coles Model • Stability Filter</div></div>
""", unsafe_allow_html=True)

def poisson_prob(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def dixon_coles(x, y, lx, ly, rho=-0.13):
    if x == 0 and y == 0: return 1.0 - (lx * ly * rho)
    if x == 0 and y == 1: return 1.0 + (lx * rho)
    if x == 1 and y == 0: return 1.0 + (ly * rho)
    if x == 1 and y == 1: return 1.0 - rho
    return 1.0

def calculate_correct_scores(h_name, a_name, h_sc, h_con, a_sc, a_con, h_cs, h_fts, a_cs, a_fts, adv):
    h_xg = max(0.2, ((h_sc + a_con) / 2.0) * (1.0 - h_fts / 200.0) * (1.0 - a_cs / 200.0) * 1.35)
    a_xg = max(0.2, ((a_sc + h_con) / 2.0) * (1.0 - a_fts / 200.0) * (1.0 - h_cs / 200.0) * 1.35)
    if adv: h_xg *= 1.08

    scores, total = {}, 0.0
    for i in range(11):
        for j in range(11):
            p = max(0.0, poisson_prob(i, h_xg) * poisson_prob(j, a_xg) * dixon_coles(i, j, h_xg, a_xg))
            scores[f"{i} - {j}"] = p
            total += p

    top5 = sorted(scores.items(), key=lambda x: x, reverse=True)[:5]
    cov = sum(x for x in top5) / total * 100.0
    s1, p1 = top5
    pct1 = (p1 / total) * 100.0

    st.divider()
    if cov >= 48.0 and pct1 >= 12.5:
        st.markdown(f'<div class="s-green">✅ High Stability: Top 5 cover {cov:.1f}% of probability</div>', unsafe_allow_html=True)
    elif cov >= 40.0:
        st.markdown(f'<div class="s-yellow">⚠️ Moderate Stability: Top 5 cover {cov:.1f}% (Caution)</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="s-red">🛑 High Volatility: {cov:.1f}% coverage (Avoid)</div>', unsafe_allow_html=True)

    st.subheader(f"🎯 {h_name} vs {a_name}")
    st.markdown(f'<div class="cs-card cs-1"><div style="font-size:12px;color:#cbd5e1;">🥇 #1 Best Correct Score</div><div class="cs-sc">{s1}</div><div style="color:#34d399;font-weight:700;">Probability: {pct1:.1f}% | xG: {h_xg:.2f} - {a_xg:.2f}</div></div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    labels = ["🥈 #2 Option", "🥉 #3 Option", "4️⃣ #4 Option", "5️⃣ #5 Option"]
    for idx in range(1, 5):
        sc, pr = top5[idx]
        cls = "cs-2" if idx < 3 else "cs-3"
        with (c1 if idx % 2 == 1 else c2):
            st.markdown(f'<div class="cs-card {cls}"><div style="font-size:12px;color:#cbd5e1;">{labels[idx-1]}</div><div class="cs-sc">{sc}</div><div style="color:#93c5fd;">{(pr/total)*100:.1f}%</div></div>', unsafe_allow_html=True)

CLUBS_DB = {
    "🏆 UEFA Champions League (All 36 Teams)": {
        "Real Madrid": (2.2, 0.8, 46, 10), "Manchester City": (2.3, 0.9, 40, 8), "Bayern Munich": (2.7, 0.8, 48, 6),
        "Liverpool": (2.2, 0.8, 45, 10), "FC Barcelona": (2.5, 1.0, 38, 8), "Inter Milan": (2.2, 0.8, 48, 8),
        "Arsenal": (2.1, 0.7, 50, 10), "Paris Saint-Germain": (2.5, 0.8, 46, 8), "Bayer Leverkusen": (2.2, 1.2, 32, 8),
        "Atletico Madrid": (1.7, 0.7, 52, 15), "Borussia Dortmund": (1.9, 1.4, 26, 14), "Juventus": (1.5, 0.6, 56, 20),
        "AC Milan": (1.7, 1.1, 34, 16), "Atalanta": (2.3, 1.1, 35, 10), "Aston Villa": (1.7, 1.2, 28, 15),
        "Sporting CP": (2.4, 0.9, 45, 8), "Benfica": (2.1, 0.9, 44, 10), "PSV Eindhoven": (2.5, 1.0, 40, 8),
        "Feyenoord": (2.0, 1.2, 30, 12), "AS Monaco": (1.8, 0.9, 42, 14), "LOSC Lille": (1.6, 0.9, 44, 16),
        "Stade Brestois": (1.5, 1.3, 28, 20), "RB Leipzig": (1.6, 0.9, 46, 18), "VfB Stuttgart": (1.9, 1.4, 24, 14),
        "Girona": (1.5, 1.3, 28, 20), "Bologna": (1.4, 1.1, 34, 22), "Celtic": (2.4, 0.9, 44, 8),
        "Club Brugge": (1.9, 1.1, 34, 14), "Shakhtar Donetsk": (1.8, 1.2, 30, 15), "Red Bull Salzburg": (1.7, 1.3, 28, 16),
        "Sturm Graz": (1.6, 1.3, 26, 18), "Sparta Prague": (1.8, 1.2, 32, 15), "Dinamo Zagreb": (1.9, 1.2, 32, 14),
        "Red Star Belgrade": (2.0, 1.3, 30, 14), "Young Boys": (1.5, 1.5, 22, 20), "Slovan Bratislava": (1.5, 1.6, 20, 22)
    },
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": {
        "Arsenal": (2.1, 0.7, 50, 10), "Manchester City": (2.3, 0.9, 40, 8), "Liverpool": (2.2, 0.8, 45, 10),
        "Chelsea": (1.8, 1.1, 30, 15), "Aston Villa": (1.7, 1.2, 28, 15), "Newcastle United": (1.7, 1.1, 32, 16),
        "Tottenham Hotspur": (1.9, 1.4, 22, 12), "Manchester United": (1.4, 1.2, 30, 22), "Brighton": (1.6, 1.3, 25, 18),
        "West Ham": (1.3, 1.5, 20, 25), "Fulham": (1.4, 1.3, 25, 22), "Bournemouth": (1.5, 1.4, 22, 20),
        "Brentford": (1.6, 1.5, 20, 18), "Crystal Palace": (1.2, 1.3, 28, 28), "Nottingham Forest": (1.3, 1.1, 35, 24),
        "Everton": (1.1, 1.3, 30, 32), "Wolves": (1.2, 1.7, 15, 26), "Leicester City": (1.2, 1.8, 15, 28)
    },
    "🇪🇸 Spanish La Liga": {
        "Real Madrid": (2.2, 0.8, 46, 10), "FC Barcelona": (2.5, 1.0, 38, 8), "Atletico Madrid": (1.7, 0.7, 52, 15),
        "Athletic Bilbao": (1.6, 0.9, 42, 18), "Villarreal": (1.8, 1.4, 24, 14), "Real Sociedad": (1.2, 0.9, 44, 28),
        "Real Betis": (1.3, 1.1, 34, 24), "Girona": (1.5, 1.3, 28, 20), "Osasuna": (1.3, 1.3, 28, 25),
        "Celta Vigo": (1.5, 1.5, 20, 20), "Mallorca": (1.0, 1.0, 38, 34), "Sevilla": (1.2, 1.3, 26, 28)
    },
    "🇮🇹 Italian Serie A": {
        "Inter Milan": (2.2, 0.8, 48, 8), "Atalanta": (2.3, 1.1, 35, 10), "Napoli": (1.7, 0.7, 54, 15),
        "Juventus": (1.5, 0.6, 56, 20), "AC Milan": (1.7, 1.1, 34, 16), "Lazio": (1.8, 1.2, 30, 15),
        "Fiorentina": (1.8, 0.9, 42, 15), "Bologna": (1.4, 1.1, 34, 22), "AS Roma": (1.3, 1.3, 28, 25)
    },
    "🇩🇪 German Bundesliga": {
        "Bayern Munich": (2.7, 0.8, 48, 6), "Bayer Leverkusen": (2.2, 1.2, 32, 8), "Eintracht Frankfurt": (2.1, 1.3, 28, 10),
        "RB Leipzig": (1.6, 0.9, 46, 18), "Borussia Dortmund": (1.9, 1.4, 26, 14), "VfB Stuttgart": (1.9, 1.4, 24, 14)
    },
    "🇫🇷 French Ligue 1": {
        "Paris Saint-Germain": (2.5, 0.8, 46, 8), "AS Monaco": (1.8, 0.9, 42, 14), "Olympique Marseille": (2.0, 1.2, 30, 12),
        "LOSC Lille": (1.6, 0.9, 44, 16), "Olympique Lyon": (1.8, 1.3, 26, 15), "OGC Nice": (1.7, 1.1, 34, 18)
    },
    "🇹🇳 Tunisian Ligue 1 & CAF": {
        "Esperance Sportive de Tunis": (1.8, 0.6, 55, 12), "Club Africain": (1.5, 0.6, 56, 18),
        "Etoile Sportive du Sahel": (1.4, 0.8, 45, 20), "CS Sfaxien": (1.2, 0.8, 46, 26),
        "US Monastir": (1.4, 0.7, 50, 20), "Stade Tunisien": (1.4, 0.8, 44, 22),
        "Al Ahly SC": (2.0, 0.6, 58, 10), "Mamelodi Sundowns": (1.9, 0.6, 56, 12)
    }
}

selected_lg = st.selectbox("1️⃣ Select Competition:", list(CLUBS_DB.keys()))
teams_dict = CLUBS_DB[selected_lg]
team_names = sorted(list(teams_dict.keys()))

col_sel1, col_sel2 = st.columns(2)
with col_sel1:
    hn = st.selectbox("2️⃣ Home Team:", team_names, index=0)
with col_sel2:
    an = st.selectbox("3️⃣ Away Team:", team_names, index=1 if len(team_names) > 1 else 0)

if hn == an:
    st.warning("⚠️ Please select two different teams.")
else:
    hsc, hcon, hcs, hfts = teams_dict[hn]
    asc, acon, acs, afts = teams_dict[an]
    ch, ca = st.columns(2)
    with ch:
        st.markdown(f'<div class="team-box"><b>🏠 {hn}</b><br><span style="color:#34d399;font-size:12px;">GF: {hsc} | GA: {hcon}<br>CS: {hcs}% | FTS: {hfts}%</span></div>', unsafe_allow_html=True)
    with ca:
        st.markdown(f'<div class="team-box"><b>✈️ {an}</b><br><span style="color:#60a5fa;font-size:12px;">GF: {asc} | GA: {acon}<br>CS: {acs}% | FTS: {afts}%</span></div>', unsafe_allow_html=True)

    adv = st.checkbox("Apply Home Advantage (+8%)", value=True)
    if st.button("🎯 Predict Correct Score", use_container_width=True):
        calculate_correct_scores(hn, an, hsc, hcon, asc, acon, hcs, hfts, acs, afts, adv)
