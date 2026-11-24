import streamlit as st
import math

st.set_page_config(page_title="متنبئ المباريات", page_icon="⚽", layout="centered")

st.title("⚽ مساعد توقع نتائج المباريات")
st.write("أدخل معدل الأهداف لكل فريق لحساب الاحتمالات")

def poisson_probability(actual, mean):
    return (math.pow(mean, actual) * math.exp(-mean)) / math.factorial(actual)

col1, col2 = st.columns(2)

with col1:
    st.subheader("الفريق المضيف")
    home_team = st.text_input("اسم الفريق 1", "ريال مدريد")
    home_scored = st.number_input("معدل أهدافه المسجلة", min_value=0.1, max_value=5.0, value=2.1, step=0.1)
    home_conceded = st.number_input("معدل الأهداف المستقبلة", min_value=0.1, max_value=5.0, value=0.9, step=0.1)

with col2:
    st.subheader("الفريق الضيف")
    away_team = st.text_input("اسم الفريق 2", "برشلونة")
    away_scored = st.number_input("معدل أهدافه المسجلة ", min_value=0.1, max_value=5.0, value=1.9, step=0.1)
    away_conceded = st.number_input("معدل الأهداف المستقبلة ", min_value=0.1, max_value=5.0, value=1.1, step=0.1)

if st.button("احسب التوقعات الآن", use_container_width=True):
    home_expected_goals = (home_scored + away_conceded) / 2
    away_expected_goals = (away_scored + home_conceded) / 2

    home_win_prob = 0
    draw_prob = 0
    away_win_prob = 0

    for i in range(11):
        for j in range(11):
            prob = poisson_probability(i, home_expected_goals) * poisson_probability(j, away_expected_goals)
            if i > j:
                home_win_prob += prob
            elif i == j:
                draw_prob += prob
            else:
                away_win_prob += prob

    total_prob = home_win_prob + draw_prob + away_win_prob
    home_win_pct = (home_win_prob / total_prob) * 100
    draw_pct = (draw_prob / total_prob) * 100
    away_win_pct = (away_win_prob / total_prob) * 100

    st.divider()
    st.subheader("📊 نتائج التحليل:")
    
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric(f"فوز {home_team}", f"{home_win_pct:.1f}%")
    res_col2.metric("التعادل", f"{draw_pct:.1f}%")
    res_col3.metric(f"فوز {away_team}", f"{away_win_pct:.1f}%")

