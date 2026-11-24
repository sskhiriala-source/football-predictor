import streamlit as st
import math
import json
import urllib.request

st.set_page_config(page_title="متنبئ النتيجة الدقيقة PRO", page_icon="🎯", layout="centered")

# تصميم ليلي احترافي مع التلوين الشرطي
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

    header[data-testid="stHeader"] { background: transparent; }

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
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 14px;
        text-align: center;
        margin-bottom: 12px;
    }

    /* بطاقات النتيجة الدقيقة بالتلوين الشرطي */
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

    /* شريط حالة الأمان */
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
        font-size: 17px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px !important;
    }
    label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-banner">
    <div class="hero-title">🎯 محلل النتيجة الدقيقة (Correct Score)</div>
    <div class="hero-sub">نموذج Dixon-Coles المتقدم • مصفوفة 10×10 • فلتر الاستقرار الإحصائي</div>
</div>
""", unsafe_allow_html=True)

# دالة بواسون الأساسية
def poisson_prob(k, lam):
    return (math.pow(lam, k) * math.exp(-lam)) / math.factorial(k)

# عامل تصحيح Dixon-Coles للنتائج المنخفضة (0-0, 1-0, 0-1, 1-1)
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
    # حساب الأهداف المتوقعة الأساسية
    base_h_xg = (h_scored + a_conceded) / 2
    base_a_xg = (a_scored + h_conceded) / 2

    # تعديل الأهداف المتوقعة بناءً على الشباك النظيفة والفشل في التسجيل
    h_attack_factor = 1 - (h_fts_pct / 200)
    a_defense_factor = 1 - (a_cs_pct / 200)
    a_attack_factor = 1 - (a_fts_pct / 200)
    h_defense_factor = 1 - (h_cs_pct / 200)

    home_xg = max(0.2, base_h_xg * h_attack_factor * a_defense_factor * 1.35)
    away_xg = max(0.2, base_a_xg * a_attack_factor * h_defense_factor * 1.35)

    if home_adv:
        home_xg *= 1.08

    scores = {}
    total_prob = 0.0

    # مصفوفة شاملة حتى 10 أهداف لكل فريق
    for i in range(11):
        for j in range(11):
            p = poisson_prob(i, home_xg) * poisson_prob(j, away_xg) * dixon_coles_tau(i, j, home_xg, away_xg)
            p = max(0.0, p)
            scores[f"{i} - {j}"] = p
            total_prob += p

    # ترتيب النتائج من الأعلى احتمالاً إلى الأقل
    sorted_scores = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top5 = sorted_scores[:5]
    top5_coverage = sum(p for _, p in top5) / total_prob * 100
    top1_pct = (top5[0][1] / total_prob) * 100

    st.divider()

    # فلتر الأمان والاستقرار الإحصائي
    if top5_coverage >= 48.0 and top1_pct >= 12.5:
        st.markdown(f"""
        <div class="safety-green">
            ✅ مؤشر استقرار عالٍ: احتمالية انحصار النتيجة ضمن القائمة بالأسفل هي {top5_coverage:.1f}%
        </div>
        """, unsafe_allow_html=True)
    elif top5_coverage >= 40.0:
        st.markdown(f"""
        <div class="safety-yellow">
            ⚠️ مؤشر استقرار متوسط: التغطية الإحصائية لأعلى 5 نتائج هي {top5_coverage:.1f}% (يُنصح بالحذر)
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="safety-red">
            🛑 مباراة عالية التذبذب: تشتت الأهداف كبير (التغطية {top5_coverage:.1f}% فقط - يُفضل تجنبها)
        </div>
        """, unsafe_allow_html=True)

    st.subheader(f"🎯 أقرب النتائج الصحيحة لمباراة {home_team} و {away_team}")

    # عرض النتيجة الأولى الأبرز
    s1_score, s1_prob = top5[0]
    s1_pct = (s1_prob / total_prob) * 100
    st.markdown(f"""
    <div class="cs-card cs-top1">
        <div class="cs-rank">🥇 النتيجة الصحيحة الأولى (الأقوى ترجيحاً)</div>
        <div class="cs-score">{s1_score}</div>
        <div class="cs-pct">نسبة التحقق: {s1_pct:.1f}% | الأهداف المتوقعة: ({home_xg:.2f} - {away_xg:.2f})</div>
    </div>
    """, unsafe_allow_html=True)

    # عرض النتائج البديلة من 2 إلى 5
    col_a, col_b = st.columns(2)
    for idx in range(1, 5):
        sc, pr = top5[idx]
        pct = (pr / total_prob) * 100
        css_cls = "cs-top2" if idx in [1, 2] else "cs-top3"
        medal = ["🥈 الاحتمال الثاني", "🥉 الاحتمال الثالث", "4️⃣ الاحتمال الرابع", "5️⃣ الاحتمال الخامس"][idx - 1]
        target_col = col_a if idx % 2 == 1 else col_b
        with target_col:
            st.markdown(f"""
            <div class="cs-card {css_cls}">
                <div class="cs-rank">{medal}</div>
                <div class="cs-score">{sc}</div>
                <div class="cs-pct" style="color:#93c5fd;">النسبة: {pct:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

# دوال الجلب التلقائي من TheSportsDB
@st.cache_data(ttl=1800)
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None

def get_team_detailed_stats(team_id):
    data = fetch_json(f"https://thesportsdb.com{team_id}")
    if not data or not data.get("results"):
        return 1.4, 1.2, 25, 25
    scored, conceded, cs, fts, count = 0, 0, 0, 0, 0
    for m in data["results"][:5]:
        hs = m.get("intHomeScore")
        as_ = m.get("intAwayScore")
        if hs is not None and as_ is not None:
            hs, as_ = int(hs), int(as_)
            if str(m.get("idHomeTeam")) == str(team_id):
                team_s, team_c = hs, as_
            else:
                team_s, team_c = as_, hs
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

tab_auto, tab_manual = st.tabs(["⚡ جلب تلقائي للمباريات", "✍️ إدخال يدوي دقيق"])

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
    events_data = fetch_json(f"https://thesportsdb.com{leagues[selected_league]}")
    events = events_data.get("events") if events_data else None

    if events:
        match_options = {f"{e['strHomeTeam']} 🆚 {e['strAwayTeam']} ({e['dateEvent']})": e for e in events[:15]}
