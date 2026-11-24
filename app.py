import streamlit as st
import streamlit.components.v1 as components
import math

st.set_page_config(page_title="Match Predictor PRO", page_icon="🎯", layout="centered")

components.html("""
<script>
const doc = window.parent.document;
function lockInputs() {
    doc.querySelectorAll('input[role="combobox"]').forEach(el => {
        el.setAttribute('readonly', true);
        el.setAttribute('inputmode', 'none');
    });
}
setInterval(lockInputs, 400);
</script>
""", height=0)

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
label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
<div class="hero"><div class="hero-t">🎯 Match Predictor PRO</div><div style="color:#94a3b8;font-size:12px;">Top 3 Correct Scores • 1X2 • Over/Under 2.5 • BTTS</div></div>
""", unsafe_allow_html=True)

def poisson_prob(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def dixon_coles(x, y, lx, ly, rho=-0.04):
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

def analyze_match(h_name, a_name, h_sc, h_con, h_cs, h_fts, h_pwr, a_sc, a_con, a_cs, a_fts, a_pwr, adv):
    pwr_diff = (h_pwr - a_pwr) / 100.0
    h_pwr_mult = max(0.55, min(1.65, 1.0 + pwr_diff * 1.4))
    a_pwr_mult = max(0.55, min(1.65, 1.0 - pwr_diff * 1.4))

    base_h = (h_sc * 0.6 + a_con * 0.4) * (1.0 - h_fts / 220.0) * (1.0 - a_cs / 220.0) * 1.25
    base_a = (a_sc * 0.6 + h_con * 0.4) * (1.0 - a_fts / 220.0) * (1.0 - h_cs / 220.0) * 1.25

    h_xg = max(0.25, base_h * h_pwr_mult * (1.12 if adv else 1.0))
    a_xg = max(0.25, base_a * a_pwr_mult * (0.94 if adv else 1.0))

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

    top3 = sorted(scores.items(), key=lambda kv: kv, reverse=True)[:3]

    st.divider()
    st.subheader(f"🎯 Top 3 Correct Scores (xG: {h_xg:.2f} - {a_xg:.2f})")
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
        "Real Madrid": (2.3, 0.9, 44, 8, 95), "Manchester City": (2.4, 0.9, 42, 8, 95), "Bayern Munich": (2.8, 1.0, 40, 6, 94),
        "Liverpool": (2.3, 0.7, 50, 8, 94), "FC Barcelona": (2.7, 1.1, 34, 6, 93), "Inter Milan": (2.1, 0.7, 52, 8, 92),
        "Arsenal": (2.1, 0.7, 52, 10, 92), "Paris Saint-Germain": (2.4, 0.9, 44, 8, 90), "Bayer Leverkusen": (2.3, 1.2, 30, 8, 89),
        "Atletico Madrid": (1.6, 0.7, 54, 16, 88), "Borussia Dortmund": (2.0, 1.4, 24, 12, 86), "Juventus": (1.4, 0.6, 58, 22, 86),
        "AC Milan": (1.8, 1.2, 32, 14, 85), "Atalanta": (2.4, 1.1, 34, 10, 87), "Aston Villa": (1.7, 1.2, 28, 15, 84),
        "Sporting CP": (2.5, 0.9, 44, 8, 85), "Benfica": (2.1, 1.0, 40, 10, 83), "PSV Eindhoven": (2.4, 1.2, 30, 10, 81),
        "Feyenoord": (1.9, 1.3, 26, 14, 79), "AS Monaco": (1.8, 1.0, 38, 14, 82), "LOSC Lille": (1.6, 0.9, 42, 16, 81),
        "Stade Brestois": (1.4, 1.3, 28, 22, 75), "RB Leipzig": (1.7, 1.1, 38, 16, 83), "VfB Stuttgart": (1.9, 1.4, 24, 14, 80),
        "Girona": (1.4, 1.4, 25, 22, 77), "Bologna": (1.3, 1.2, 32, 24, 76), "Celtic": (2.2, 1.3, 30, 12, 76),
        "Club Brugge": (1.7, 1.2, 30, 16, 75), "Shakhtar Donetsk": (1.6, 1.4, 24, 18, 73), "Red Bull Salzburg": (1.5, 1.6, 20, 20, 72),
        "Sturm Graz": (1.3, 1.6, 18, 24, 69), "Sparta Prague": (1.5, 1.5, 22, 20, 71), "Dinamo Zagreb": (1.6, 1.7, 18, 20, 70),
        "Red Star Belgrade": (1.6, 1.8, 16, 20, 69), "Young Boys": (1.2, 1.9, 14, 28, 67), "Slovan Bratislava": (1.1, 2.2, 10, 32, 64)
    },
    "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": {
        "Arsenal": (2.1, 0.7, 52, 10, 92), "Manchester City": (2.4, 0.9, 42, 8, 95), "Liverpool": (2.3, 0.7, 50, 8, 94),
        "Chelsea": (2.0, 1.1, 30, 12, 87), "Aston Villa": (1.7, 1.2, 28, 15, 84), "Newcastle United": (1.7, 1.1, 32, 16, 84),
        "Tottenham Hotspur": (2.0, 1.4, 22, 10, 84), "Manchester United": (1.4, 1.2, 30, 22, 82), "Brighton": (1.7, 1.3, 25, 16, 81),
        "West Ham": (1.3, 1.6, 18, 25, 76), "Fulham": (1.5, 1.3, 25, 20, 78), "Bournemouth": (1.5, 1.4, 22, 20, 78),
        "Brentford": (1.7, 1.6, 18, 16, 77), "Crystal Palace": (1.1, 1.4, 26, 30, 74), "Nottingham Forest": (1.4, 1.0, 38, 22, 80),
        "Everton": (1.0, 1.4, 28, 34, 72), "Wolves": (1.3, 1.9, 12, 24, 71), "Leicester City": (1.2, 1.9, 14, 28, 70)
    },
    "🇪🇸 Spanish La Liga": {
        "Real Madrid": (2.3, 0.9, 44, 8, 95), "FC Barcelona": (2.7, 1.1, 34, 6, 93), "Atletico Madrid": (1.6, 0.7, 54, 16, 88),
        "Athletic Bilbao": (1.6, 0.9, 42, 18, 84), "Villarreal": (1.9, 1.5, 22, 12, 82), "Real Sociedad": (1.2, 0.9, 44, 28, 81),
        "Real Betis": (1.3, 1.1, 34, 24, 79), "Girona": (1.4, 1.4, 25, 22, 77), "Osasuna": (1.3, 1.4, 26, 25, 76),
        "Celta Vigo": (1.5, 1.6, 18, 20, 75), "Mallorca": (1.0, 1.0, 40, 34, 76), "Sevilla": (1.2, 1.4, 24, 28, 75)
    },
    "🇮🇹 Italian Serie A": {
        "Inter Milan": (2.1, 0.7, 52, 8, 92), "Atalanta": (2.4, 1.1, 34, 10, 87), "Napoli": (1.8, 0.7, 54, 14, 88),
        "Juventus": (1.4, 0.6, 58, 22, 86), "AC Milan": (1.8, 1.2, 32, 14, 85), "Lazio": (1.8, 1.2, 30, 15, 83),
        "Fiorentina": (1.8, 0.9, 42, 15, 83), "Bologna": (1.3, 1.2, 32, 24, 76), "AS Roma": (1.3, 1.4, 26, 26, 78)
    },
    "🇩🇪 German Bundesliga": {
        "Bayern Munich": (2.8, 1.0, 40, 6, 94), "Bayer Leverkusen": (2.3, 1.2, 30, 8, 89), "Eintracht Frankfurt": (2.1, 1.3, 28, 10, 84),
        "RB Leipzig": (1.7, 1.1, 38, 16, 83), "Borussia Dortmund": (2.0, 1.4, 24, 12, 86), "VfB Stuttgart": (1.9, 1.4, 24, 14, 80)
    },
    "🇫🇷 French Ligue 1": {
        "Paris Saint-Germain": (2.4, 0.9, 44, 8, 90), "AS Monaco": (1.8, 1.0, 38, 14, 82), "Olympique Marseille": (2.0, 1.2, 30, 12, 82),
        "LOSC Lille": (1.6, 0.9, 42, 16, 81), "Olympique Lyon": (1.8, 1.3, 26, 15, 80), "OGC Nice": (1.7, 1.1, 34, 18, 79)
    },
    "🇹🇳 Tunisian Ligue 1 & CAF": {
        "Esperance Sportive de Tunis": (1.9, 0.6, 56, 10, 82), "Club Africain": (1.5, 0.6, 56, 18, 78),
        "Etoile Sportive du Sahel": (1.4, 0.8, 45, 20, 76), "CS Sfaxien": (1.1, 0.8, 46, 28, 73),
        "US Monastir": (1.4, 0.7, 50, 20, 76), "Stade Tunisien": (1.4, 0.8, 44, 22, 75),
        "Al Ahly SC": (2.1, 0.6, 58, 10, 85), "Mamelodi Sundowns": (2.0, 0.6, 56, 12, 84)
    }
}

selected_lg = st.selectbox("1️⃣ Select Competition:", list(CLUBS_DB.keys()))
teams_dict = CLUBS_DB[selected_lg]
team_names = sorted(list(teams_dict.keys()))

hn = st.selectbox("2️⃣ Home Team:", team_names, index=0)
an = st.selectbox("3️⃣ Away Team:", team_names, index=1 if len(team_names) > 1 else 0)
