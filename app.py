import streamlit as st
import math
import json
import urllib.request
from datetime import datetime, timedelta

st.set_page_config(page_title="Correct Score Predictor PRO", page_icon="🎯", layout="centered")

# Professional Dark Stadium Theme (LTR English)
st.markdown("""
<style>
    @import url('https://googleapis.com');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    .stApp {
        direction: ltr;
        text-align: left;
        background: radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.22) 0%, transparent 55%),
                    linear-gradient(160deg, #070b14 0%, #0d192b 50%, #061714 100%);
        color: #f8fafc;
    }

    header[data-testid="stHeader"] { background: transparent; }

    /* Fix Tab Text Visibility */
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] {
        color: #f8fafc !important;
        font-weight: 700 !important;
        font-size: 15px !important;
    }

    .hero-banner {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 18px;
        padding: 18px;
        text-align: center;
        margin-bottom: 18px;
        backdrop-filter: blur(12px);
    }
    .hero-title {
        font-size: 24px;
        font-weight: 900;
        background: linear-gradient(90deg, #34d399, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub { color: #94a3b8; font-size: 13px; margin-top: 5px; }

    .team-box {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        margin-bottom: 12px;
    }

    .cs-card {
        border-radius: 16px;
        padding: 16px 10px;
        text-align: center;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
    }
    .cs-top1 {
        background: rgba(16, 185, 129, 0.22);
        border: 2px solid #10b981;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.25);
    }
    .cs-top2 {
        background: rgba(59, 130, 246, 0.18);
        border: 1.5px solid #3b82f6;
    }
    .cs-top3 {
        background: rgba(245, 158, 11, 0.15);
        border: 1.5px solid #f59e0b;
    }
    .cs-rank { font-size: 12px; font-weight: 700; color: #cbd5e1; margin-bottom: 4px; }
    .cs-score { font-size: 28px; font-weight: 900; color: #ffffff; letter-spacing: 2px; }
    .cs-pct { font-size: 14px; font-weight: 700; color: #34d399; margin-top: 4px; }

    .safety-green {
        background: rgba(16, 185, 129, 0.18);
        border: 1.5px solid #10b981;
        color: #34d399;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        margin-bottom: 15px;
    }
    .safety-yellow {
        background: rgba(245, 158, 11, 0.18);
        border: 1.5px solid #f59e0b;
        color: #fbbf24;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        margin-bottom: 15px;
    }
    .safety-red {
        background: rgba(239, 68, 68, 0.18);
        border: 1.5px solid #ef4444;
        color: #f87171;
        padding: 14px;
        border-radius: 14px;
        text-align: center;
        font-weight: 800;
        margin-bottom: 15px;
    }

    .stButton > button {
        background: linear-gradient(90deg, #10b981, #059669) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎯 Correct Score Predictor PRO</div>
    <div class="hero-sub">Dixon-Coles Model • 10×10 Goal Matrix • Statistical Stability Filter</div>
</div>
""", unsafe_allow_html=True)

def poisson_prob(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

def dixon_coles_tau(x, y, lam_x, lam_y, rho=-0.13):
    if x == 0 and y == 0:
        return 1 - (lam_x * lam_y * rho)
    elif x == 0 and y == 1:
        return 1 + (lam_x * rho)
    elif x == 1 and y == 0:
        return 1 + (lam_y * rho)
    elif x == 1 and y == 1:
        return 1 - rho
    else:
        return 1.0

def calculate_correct_scores(home_team, away_team, h_scored, h_conceded, a_scored, a_conceded, h_cs_pct, h_fts_pct, a_cs_pct, a_fts_pct, home_adv):
    base_h_xg = (h_scored + a_conceded) / 2.0
    base_a_xg = (a_scored + h_conceded) / 2.0

    h_attack_factor = 1.0 - (h_fts_pct / 200.0)
    a_defense_factor = 1.0 - (a_cs_pct / 200.0)
    a_attack_factor = 1.0 - (a_fts_pct / 200.0)
    h_defense_factor = 1.0 - (h_cs_pct / 200.0)

    home_xg = max(0.2, base_h_xg * h_attack_factor * a_defense_factor * 1.35)
    away_xg = max(0.2, base_a_xg * a_attack_factor * h_defense_factor * 1.35)

    if home_adv:
        home_xg *= 1.08

    scores = {}
    total_prob = 0.0

    for i in range(11):
        for j in range(11):
            p = poisson_prob(i, home_xg) * poisson_prob(j, away_xg) * dixon_coles_tau(i, j, home_xg, away_xg)
            p = max(0.0, p)
            scores[f"{i} - {j}"] = p
            total_prob += p

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top5 = sorted_scores[:5]
    top5_coverage = sum(item[1] for item in top5) / total_prob * 100.0
    s1_score, s1_prob = top5[0]
    s1_pct = (s1_prob / total_prob) * 100.0

    st.divider()

    # Safety & Stability Filter
    if top5_coverage >= 48.0 and s1_pct >= 12.5:
        st.markdown(f"""
        <div class="safety-green">
            ✅ High Stability: Top 5 scorelines cover {top5_coverage:.1f}% of total match probability
        </div>
        """, unsafe_allow_html=True)
    elif top5_coverage >= 40.0:
        st.markdown(f"""
        <div class="safety-yellow">
            ⚠️ Moderate Stability: Top 5 coverage is {top5_coverage:.1f}% (Proceed with caution)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="safety-red">
            🛑 High Volatility Match: High goal variance ({top5_coverage:.1f}% coverage - Avoid)
        </div>
        """, unsafe_allow_html=True)

    st.subheader(f"🎯 Top Correct Scores: {home_team} vs {away_team}")

    st.markdown(f"""
    <div class="cs-card cs-top1">
        <div class="cs-rank">🥇 #1 Most Likely Correct Score</div>
        <div class="cs-score">{s1_score}</div>
        <div class="cs-pct">Probability: {s1_pct:.1f}% | Expected Goals (xG): {home_xg:.2f} - {away_xg:.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    medals = ["🥈 #2 Option", "🥉 #3 Option", "4️⃣ #4 Option", "5️⃣ #5 Option"]
    for idx in range(1, 5):
        sc, pr = top5[idx]
        pct = (pr / total_prob) * 100.0
        css_cls = "cs-top2" if idx < 3 else "cs-top3"
        target_col = col_a if idx % 2 == 1 else col_b
        with target_col:
            st.markdown(f"""
            <div class="cs-card {css_cls}">
                <div class="cs-rank">{medals[idx - 1]}</div>
                <div class="cs-score">{sc}</div>
                <div class="cs-pct" style="color:#93c5fd;">Probability: {pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

@st.cache_data(ttl=1800)
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None

def parse_score(sc_obj):
    if isinstance(sc_obj, dict):
        return int(float(sc_obj.get("value", 0)))
    try:
        return int(float(sc_obj))
    except Exception:
        return 0

@st.cache_data(ttl=1800)
def get_espn_team_stats(league_code, team_id):
    data = fetch_json(f"https://espn.com{league_code}/teams/{team_id}/schedule")
    if not data or not isinstance(data.get("events"), list):
        return 1.4, 1.2, 25, 25

    completed = []
    for ev in data["events"]:
        comps = ev.get("competitions")
        if not comps or not isinstance(comps, list):
            continue
        comp0 = comps[0]
        status = comp0.get("status", {}).get("type", {})
        if status.get("completed") is True:
            completed.append(comp0)

    last5 = completed[-5:]
    if not last5:
        return 1.4, 1.2, 25, 25

    scored, conceded, cs, fts, count = 0, 0, 0, 0, 0
    for comp in last5:
        competitors = comp.get("competitors", [])
        if len(competitors) < 2:
            continue
        team_s, team_c = 0, 0
        for c in competitors:
            c_id = str(c.get("id", ""))
            t_id = str(c.get("team", {}).get("id", ""))
            if c_id == str(team_id) or t_id == str(team_id):
                team_s = parse_score(c.get("score"))
            else:
                team_c = parse_score(c.get("score"))
        scored += team_s
        conceded += team_c
        if team_c == 0:
            cs += 1
        if team_s == 0:
            fts += 1
        count += 1

    if count == 0:
        return 1.4, 1.2, 25, 25

    return (
        round(scored / count, 2),
        round(conceded / count, 2),
        int((cs / count) * 100),
        int((fts / count) * 100)
    )

tab_auto, tab_manual = st.tabs(["⚡ Auto-Fetch Fixtures", "✍️ Manual Stats Input"])

with tab_auto:
    leagues = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 English Premier League": "eng.1",
        "🏆 UEFA Champions League": "uefa.champions",
        "🇪🇸 Spanish La Liga": "esp.1",
        "🇮🇹 Italian Serie A": "ita.1",
        "🇩🇪 German Bundesliga": "ger.1",
