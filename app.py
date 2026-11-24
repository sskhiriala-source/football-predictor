import streamlit as st
import math

st.set_page_config(page_title="متنبئ المباريات الاحترافي", page_icon="⚽", layout="centered")

# تنسيق CSS لدعم العربية والتلوين الشرطي للبطاقات
st.markdown("""
<style>
    .stApp { direction: rtl; text-align: right; }
    .metric-card {
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.08);
    }
    .high-prob { background-color: #d4edda; color: #155724; border: 2px solid #28a745; }
    .med-prob { background-color: #fff3cd; color: #856404; border: 2px solid #ffc107; }
    .low-prob { background-color: #f8d7da; color: #721c24; border: 2px solid #dc3545; }
    .card-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; }
    .card-value { font-size: 26px; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

st.title("⚽ محلل وتوقعات المباريات")
st.write("أدخل إحصائيات الفريقين للحصول على تحليل شامل بالتلوين الشرطي")

def poisson_probability(actual, mean):
    return (math.pow(mean, actual) * math.exp(-mean)) / math.factorial(actual)

# دالة التلوين الشرطي حسب النسبة المئوية
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

# إدخال بيانات الفريقين
col1, col2 = st.columns(2)

with col1:
    st.subheader("🏠 الفريق المضيف")
    home_team = st.text_input("اسم الفريق 1", "ريال مدريد")
    home_scored = st.number_input("معدل أهدافه المسجلة", min_value=0.1, max_value=5.0, value=2.1, step=0.1)
    home_conceded = st.number_input("معدل الأهداف المستقبلة", min_value=0.1, max_value=5.0, value=0.9, step=0.1)

with col2:
    st.subheader("✈️ الفريق الضيف")
    away_team = st.text_input("اسم الفريق 2", "برشلونة")
    away_scored = st.number_input("معدل أهدافه المسجلة ", min_value=0.1, max_value=5.0, value=1.9, step=0.1)
    away_conceded = st.number_input("معدل الأهداف المستقبلة ", min_value=0.1, max_value=5.0, value=1.1, step=0.1)

# خيار أفضلية الأرض
home_adv = st.checkbox("إضافة أفضلية الأرض والجمهور للفريق المضيف (+10%)", value=True)

if st.button("🔍 تحليل المباراة وحساب التوقعات", use_container_width=True):
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
    st.subheader("🏆 نتيجة المباراة (1X2)")
    c1, c2, c3 = st.columns(3)
    with c1: render_card(f"فوز {home_team}", home_win_pct)
    with c2: render_card("التعادل", draw_pct)
    with c3: render_card(f"فوز {away_team}", away_win_pct)

    st.subheader("⚽ توقعات الأهداف")
    g1, g2 = st.columns(2)
    with g1: render_card("أكثر من 2.5 هدف", over_25_pct)
    with g2: render_card("أقل من 2.5 هدف", under_25_pct)

    g3, g4 = st.columns(2)
    with g3: render_card("كلا الفريقين يسجل (نعم)", btts_yes_pct)
    with g4: render_card("كلا الفريقين يسجل (لا)", btts_no_pct)

    st.subheader("🎯 أكثر 3 نتائج دقيقة متوقعة")
    top_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:3]
    s1, s2, s3 = st.columns(3)
    for idx, (score, prob) in enumerate(top_scores):
        score_pct = (prob / total) * 100
        with [s1, s2, s3][idx]:
            st.info(f"**النتيجة: {score}**\n\nالاحتمال: **{score_pct:.1f}%**")
