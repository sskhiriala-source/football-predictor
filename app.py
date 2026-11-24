import streamlit as st
import math

st.set_page_config(page_title="Match Predictor PRO", page_icon="🎯", layout="centered")

st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { direction: ltr; text-align: left; background: linear-gradient(160deg, #070b14 0%, #0d192b 50%, #061714 100%); color: #f8fafc; }
header[data-testid="stHeader"] { background: transparent; }
.hero { background: rgba(255,255,255,0.05); border: 1px solid #10b981; border-radius: 16px; padding: 14px; text-align: center; margin-bottom: 16px; }
.hero-t { font-size: 21px; font-weight: 900; color: #34d399; margin: 0; }
.team-box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 12px; text-align: center; margin-bottom: 10px; }
.card { border-radius: 14px; padding: 12px 8px; text-align: center; margin-bottom: 10px; }
.c-green { background: rgba(16,185,129,0.22); border: 1.5px solid #10b981; color: #34d399; }
.c-yellow { background: rgba(245,158,11,0.18); border: 1.5px solid #f59e0b; color: #fbbf24; }
.c-red { background: rgba(239,68,68,0.18); border: 1.5px solid #ef4444; color: #f87171; }
.c-blue { background: rgba(59,130,246,0.20); border: 1.5px solid #3b82f6; color: #60a5fa; }
.c-title { font-size: 12px; font-weight: 700; color: #e2e8f0; margin-bottom: 4px; }
.c-val { font-size: 22px; font-weight: 900; }
.stButton > button { background: linear-gradient(90deg, #10b981, #059669) !important; color: white !important; font-weight: 800 !important; font-size: 16px !important; border-radius: 12px !important; padding: 12px !important; }
label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
<div class="hero"><div class="hero-t">🎯 Match Predictor PRO</div><div style="color:#94a3b8;font-size:12px;">Top 3 Correct Scores • 1X2 • Over/Under 2.5 • BTTS</div></div>
""", unsafe_allow_html=True)

def poisson_prob(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def dixon_coles(x, y, lx, ly, rho=-0.13):
    if x == 0 and y == 0: return 1.0 - (lx * ly * rho)
    if x == 0 and y == 1: return 1.0 + (lx * rho)
    if x == 1 and y == 0: return 1.0 + (ly * rho)
    if x == 1 and y == 1: return 1.0 - rho
    return 1.0

def color_cls(pct):
    if pct >= 55.0: return "c-green"
    if pct >= 35.0: return "c-yellow"
    return "c-red"

def show_box(title, val_str, pct_for_color):
    cls = color_cls(pct_for_color)
    st.markdown(f'<div class="card {cls}"><div class="c-title">{title}</div><div class="c-val">{val_str}</div></div>', unsafe_allow_html=True)

def analyze_match(h_name, a_name, h_sc, h_con, a_sc, a_con, h_cs, h_fts, a_cs, a_fts, adv):
    h_xg = max(0.2, ((h_sc + a_con) / 2.0) * (1.0 - h_fts / 200.0) * (1.0 - a_cs / 200.0) * 1.35)
    a_xg = max(0.2, ((a_sc + h_con) / 2.0) * (1.0 - a_fts / 200.0) * (1.0 - h_cs / 200.0) * 1.35)
    if adv: h_xg *= 1.08

    scores = {}
    total, w1, draw, w2, over25, btts_yes = 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    for i in range(11):
        for j in range(11):
            p = max(0.0, poisson_prob(i, h_xg) * poisson_prob(j, a_xg) * dixon_coles(i, j, h_xg, a_xg))
            scores[f"{i} - {j}"] = p
            total += p
            if i > j: w1 += p
            elif i == j: draw += p
            else: w2 += p
            if (i + j) > 2.5: over25 += p
            if i > 0 and j > 0: btts_yes += p

    p_1 = (w1 / total) * 100.0
    p_x = (draw / total) * 100.0
    p_2 = (w2 / total) * 100.0
    p_o25 = (over25 / total) * 100.0
    p_u25 = 100.0 - p_o25
    p_by = (btts_yes / total) * 100.0
    p_bn = 100.0 - p_by

    top3 = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)[:3]

    st.divider()
    st.subheader("🎯 Top 3 Correct Scores")
    c1, c2, c3 = st.columns(3)
    medals = ["🥇 #1", "🥈 #2", "🥉 #3"]
    for idx, (sc, pr) in enumerate(top3):
        sc_pct = (pr / total) * 100.0
        box_style = "c-green" if idx == 0 else "c-blue"
        with [c1, c2, c3][idx]:
            st.markdown(f'<div class="card {box_style}"><div class="c-title">{medals[idx]}</div><div class="c-val">{sc}</div><div style="font-size:13px;font-weight:700;">{sc_pct:.1f}%</div></div>', unsafe_allow_html=True)

    st.subheader("🏆 Match Result (1 X 2)")
    m1, m2, m3 = st.columns(3)
    with m1: show_box(f"1 ({h_name[:12]})", f"{p_1:.1f}%", p_1)
    with m2: show_box("X (Draw)", f"{p_x:.1f}%", p_x)
    with m3: show_box(f"2 ({a_name[:12]})", f"{p_2:.1f}%", p_2)

    st.subheader("⚽ Goals & Both Teams to Score")
    g1, g2 = st.columns(2)
    with g1: show_box("Over 2.5 Goals", f"{p_o25:.1f}%", p_o25)
    with g2: show_box("Under 2.5 Goals", f"{p_u25:.1f}%", p_u25)

    b1, b2 = st.columns(2)
    with b1: show_box("BTTS: Yes", f"{p_by:.1f}%", p_by)
    with b2: show_box("BTTS: No", f"{p_bn:.1f}%", p_bn)

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
    if st.button("🎯 Predict Match", use_container_width=True):
