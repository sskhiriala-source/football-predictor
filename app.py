import streamlit as st
import math
import json
import urllib.request

st.set_page_config(page_title="محلل المباريات الذكي", page_icon="⚽", layout="centered")

# تصميم احترافي بخلفية ملعب ليلية وتأثير الزجاج (Glassmorphism)
st.markdown("""
<style>
    @import url('https://googleapis.com');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
    }

    .stApp {
        direction: rtl;
        text-align: right;
        background: radial-gradient(circle at 50% 0%, rgba(16, 185, 129, 0.22) 0%, transparent 55%),
                    linear-gradient(160deg, #070b14 0%, #0d192b 50%, #061714 100%);
        color: #f8fafc;
    }

    /* إخفاء شريط Streamlit العلوي الافتراضي لمظهر تطبيق أصلي */
    header[data-testid="stHeader"] { background: transparent; }

    /* ترويسة التطبيق */
    .hero-banner {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(16, 185, 129, 0.35);
        border-radius: 18px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    }
    .hero-title {
        font-size: 26px;
        font-weight: 900;
        background: linear-gradient(90deg, #34d399, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .hero-sub {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
    }

    /* بطاقات الفرق */
    .team-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 15px;
        text-align: center;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }

    /* بطاقات التلوين الشرطي */
    .metric-card {
        padding: 16px 10px;
        border-radius: 14px;
        text-align: center;
        margin-bottom: 12px;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease;
    }
    .high-prob {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1.5px solid #10b981;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.2);
    }
    .med-prob {
        background: rgba(245, 158, 11, 0.18);
        color: #fbbf24;
        border: 1.5px solid #f59e0b;
        box-shadow: 0 4px 20px rgba(245, 158, 11, 0.15);
    }
    .low-prob {
        background: rgba(239, 68, 68, 0.18);
        color: #f87171;
        border: 1.5px solid #ef4444;
    }
    .card-title { font-size: 14px; font-weight: 700; color: #e2e8f0; margin-bottom: 6px; }
    .card-value { font-size: 26px; font-weight: 900; }

    /* بطاقة النتيجة الدقيقة */
    .score-card {
        background: rgba(59, 130, 246, 0.15);
        border: 1.5px solid #3b82f6;
        border-radius: 14px;
        padding: 14px;
        text-align: center;
        margin-bottom: 10px;
    }
    .score-num { font-size: 22px; font-weight: 900; color: #60a5fa; }
    .score-pct { font-size: 14px; color: #cbd5e1; }

    /* تحسين الأزرار والمدخلات */
    .stButton > button {
        background: linear-gradient(90deg, #10b981, #059669) !important;
        color: white !important;
        font-weight: 800 !important;
        font-size: 17px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.35) !important;
    }
    label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

# ترويسة احترافية
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">⚽ محلل المباريات الذكي PRO</div>
    <div class="hero-sub">تحليل إحصائي متقدم • جلب تلقائي للبيانات • تلوين شرطي ذكي</div>
</div>
""", unsafe_allow_html=True)

# دوال الحساب الرياضي (توزيع بواسون)
def poisson_probability(actual, mean):
    return (math.pow(mean, actual) * math.exp(-mean)) / math.factorial(actual)

def get_color_class(pct):
    if pct >= 55:
        return "high-prob"
    elif pct >= 35:
        return "med-prob"
    else:
        return "low-prob"

def render_card(title, pct):
    color_class = get_color_class(pct)
    st.markdown(f"""
    <div class="metric-card {color_class}">
        <div class="card-title">{title}</div>
        <div class="card-value">{pct:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

def display_predictions(home_team, away_team, home_scored, home_conceded, away_scored, away_conceded, home_adv):
    home_xg = (home_scored + away_conceded) / 2
    away_xg = (away_scored + home_conceded) / 2
    if home_adv:
        home_xg *= 1.10

    home_win, draw, away_win = 0, 0, 0
    over_25, btts_yes = 0, 0
    scores = {}

    for i in range(11):
        for j in range(11):
            prob = poisson_probability(i, home_xg) * poisson_probability(j, away_xg)
            scores[f"{i} - {j}"] = prob
            if i > j:
                home_win += prob
            elif i == j:
                draw += prob
            else:
                away_win += prob
            if (i + j) > 2.5:
                over_25 += prob
            if i > 0 and j > 0:
                btts_yes += prob

    total = home_win + draw + away_win
    home_win_pct = (home_win / total) * 100
    draw_pct = (draw / total) * 100
    away_win_pct = (away_win / total) * 100
    over_25_pct = (over_25 / total) * 100
    under_25_pct = 100 - over_25_pct
    btts_yes_pct = (btts_yes / total) * 100
    btts_no_pct = 100 - btts_yes_pct

    st.divider()
    st.subheader("🏆 احتمالات نتيجة المباراة (1X2)")
    c1, c2, c3 = st.columns(3)
    with c1: render_card(f"فوز {home_team}", home_win_pct)
    with c2: render_card("التعادل", draw_pct)
    with c3: render_card(f"فوز {away_team}", away_win_pct)

    st.subheader("⚽ مؤشرات الأهداف")
    g1, g2 = st.columns(2)
    with g1: render_card("أكثر من 2.5 هدف", over_25_pct)
    with g2: render_card("أقل من 2.5 هدف", under_25_pct)

    g3, g4 = st.columns(2)
    with g3: render_card("كلا الفريقين يسجل (نعم)", btts_yes_pct)
    with g4: render_card("كلا الفريقين يسجل (لا)", btts_no_pct)

    st.subheader("🎯 أكثر 3 نتائج دقيقة ترجيحاً")
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    s1, s2, s3 = st.columns(3)
    for idx, (score, prob) in enumerate(top_scores):
        score_pct = (prob / total) * 100
        with [s1, s2, s3][idx]:
            st.markdown(f"""
            <div class="score-card">
                <div class="score-num">{score}</div>
                <div class="score-pct">الاحتمال: {score_pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# دوال الجلب التلقائي من قاعدة بيانات TheSportsDB المجانية
@st.cache_data(ttl=1800)
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None

def get_team_last5_stats(team_id):
    data = fetch_json(f"https://thesportsdb.com{team_id}")
    if not data or not data.get("results"):
        return 1.4, 1.2, 0
    scored, conceded, count = 0, 0, 0
    for m in data["results"][:5]:
        hs = m.get("intHomeScore")
        as_ = m.get("intAwayScore")
        if hs is not None and as_ is not None:
            hs, as_ = int(hs), int(as_)
            if str(m.get("idHomeTeam")) == str(team_id):
                scored += hs
                conceded += as_
            else:
                scored += as_
                conceded += hs
            count += 1
    if count == 0:
        return 1.4, 1.2, 0
    return round(scored / count, 2), round(conceded / count, 2), count

# التبويبات: جلب تلقائي أو إدخال يدوي
tab_auto, tab_manual = st.tabs(["⚡ جلب تلقائي للمباريات", "✍️ إدخال يدوي مخصص"])

with tab_auto:
    leagues = {
        "🏴󠁧󠁢󠁥󠁮󠁧󠁿 الدوري الإنجليزي الممتاز": "4328",
        "🇪🇸 الدوري الإسباني": "4335",
        "🇮🇹 الدوري الإيطالي": "4332",
        "🇩🇪 الدوري الألماني": "4331",
        "🇫🇷 الدوري الفرنسي": "4334",
        "🏆 دوري أبطال أوروبا": "4480"
    }
    selected_league = st.selectbox("اختر البطولة:", list(leagues.keys()))
    league_id = leagues[selected_league]

    events_data = fetch_json(f"https://thesportsdb.com{league_id}")
    events = events_data.get("events") if events_data else None

    if events:
        match_options = {f"{e['strHomeTeam']} 🆚 {e['strAwayTeam']} ({e['dateEvent']})": e for e in events[:15]}
        selected_match_label = st.selectbox("اختر المباراة القادمة:", list(match_options.keys()))
        match = match_options[selected_match_label]

        h_name = match["strHomeTeam"]
        a_name = match["strAwayTeam"]
        h_id = match["idHomeTeam"]
        a_id = match["idAwayTeam"]
        h_badge = match.get("strHomeTeamBadge") or ""
        a_badge = match.get("strAwayTeamBadge") or ""

        h_scored, h_conceded, h_cnt = get_team_last5_stats(h_id)
        a_scored, a_conceded, a_cnt = get_team_last5_stats(a_id)

        col_h, col_a = st.columns(2)
        with col_h:
            img_h = f'<img src="{h_badge}" width="48" style="margin-bottom:8px;"><br>' if h_badge else ""
            st.markdown(f"""
            <div class="team-box">
                {img_h}<b>🏠 {h_name}</b><br>
                <span style="color:#34d399; font-size:13px;">سجل: {h_scored} | استقبل: {h_conceded}</span>
            </div>
            """, unsafe_allow_html=True)
        with col_a:
            img_a = f'<img src="{a_badge}" width="48" style="margin-bottom:8px;"><br>' if a_badge else ""
            st.markdown(f"""
            <div class="team-box">
                {img_a}<b>✈️ {a_name}</b><br>
