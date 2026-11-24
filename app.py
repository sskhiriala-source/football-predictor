import streamlit as st
import math, json, urllib.request
from datetime import datetime, timedelta

st.set_page_config(page_title="Correct Score PRO", page_icon="🎯", layout="centered")

st.markdown("""
<style>
@import url('https://googleapis.com');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { direction: ltr; text-align: left; background: linear-gradient(160deg, #070b14 0%, #0d192b 50%, #061714 100%); color: #f8fafc; }
header[data-testid="stHeader"] { background: transparent; }
button[data-baseweb="tab"] p, button[data-baseweb="tab"] { color: #f8fafc !important; font-weight: 700 !important; }
.hero { background: rgba(255,255,255,0.05); border: 1px solid #10b981; border-radius: 16px; padding: 16px; text-align: center; margin-bottom: 16px; }
.hero-t { font-size: 22px; font-weight: 900; color: #34d399; margin: 0; }
.team-box { background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 12px; text-align: center; margin-bottom: 10px; }
.cs-card { border-radius: 14px; padding: 14px; text-align: center; margin-bottom: 10px; }
.cs-1 { background: rgba(16,185,129,0.22); border: 2px solid #10b981; }
.cs-2 { background: rgba(59,130,246,0.18); border: 1.5px solid #3b82f6; }
.cs-3 { background: rgba(245,158,11,0.15); border: 1.5px solid #f59e0b; }
.cs-sc { font-size: 26px; font-weight: 900; color: #fff; letter-spacing: 2px; }
.s-green { background: rgba(16,185,129,0.2); border: 1.5px solid #10b981; color: #34d399; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.s-yellow { background: rgba(245,158,11,0.2); border: 1.5px solid #f59e0b; color: #fbbf24; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.s-red { background: rgba(239,68,68,0.2); border: 1.5px solid #ef4444; color: #f87171; padding: 12px; border-radius: 12px; text-align: center; font-weight: 800; margin-bottom: 12px; }
.stButton > button { background: linear-gradient(90deg, #10b981, #059669) !important; color: white !important; font-weight: 800 !important; border-radius: 12px !important; }
label, .stMarkdown p, h1, h2, h3 { color: #f1f5f9 !important; }
</style>
<div class="hero"><div class="hero-t">🎯 Correct Score Predictor PRO</div><div style="color:#94a3b8;font-size:12px;">Dixon-Coles Model • Stability Filter</div></div>
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

    top5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]
    cov = sum(x[1] for x in top5) / total * 100.0
    s1, p1 = top5[0]
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

@st.cache_data(ttl=1800)
def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=4) as r:
            return json.loads(r.read().decode())
    except Exception:
        return None

def parse_sc(val):
    if isinstance(val, dict): return int(float(val.get("value", 0)))
    try: return int(float(val))
    except Exception: return 0

@st.cache_data(ttl=1800)
def get_stats(league, tid):
    data = fetch_json(f"https://espn.com{league}/teams/{tid}/schedule")
    if not data or not isinstance(data.get("events"), list): return 1.4, 1.2, 25, 25
    done = [ev["competitions"][0] for ev in data["events"] if isinstance(ev.get("competitions"), list) and ev["competitions"] and ev["competitions"][0].get("status", {}).get("type", {}).get("completed")]
    last5 = done[-5:]
    if not last5: return 1.4, 1.2, 25, 25
    sc, con, cs, fts, cnt = 0, 0, 0, 0, 0
    for comp in last5:
        ts, tc = 0, 0
        for c in comp.get("competitors", []):
            if str(c.get("id")) == str(tid) or str(c.get("team", {}).get("id")) == str(tid): ts = parse_sc(c.get("score"))
            else: tc = parse_sc(c.get("score"))
        sc += ts; con += tc; cnt += 1
        if tc == 0: cs += 1
        if ts == 0: fts += 1
    return (round(sc/cnt, 2), round(con/cnt, 2), int(cs/cnt*100), int(fts/cnt*100)) if cnt else (1.4, 1.2, 25, 25)

tab1, tab2 = st.tabs(["⚡ Auto-Fetch Fixtures", "✍️ Manual Stats Input"])

with tab1:
    leagues = {"🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League": "eng.1", "🏆 Champions League": "uefa.champions", "🇪🇸 La Liga": "esp.1", "🇮🇹 Serie A": "ita.1", "🇩🇪 Bundesliga": "ger.1", "🇫🇷 Ligue 1": "fra.1", "🇸🇦 Saudi Pro League": "ksa.1"}
    lg_slug = leagues[st.selectbox("Select Competition:", list(leagues.keys()))]
    d1, d2 = datetime.utcnow().strftime("%Y%m%d"), (datetime.utcnow() + timedelta(days=10)).strftime("%Y%m%d")
    ev_data = fetch_json(f"https://espn.com{lg_slug}/scoreboard?dates={d1}-{d2}")
    events = ev_data.get("events") if isinstance(ev_data, dict) else None

    if events:
        matches = {}
        for ev in events:
            comps = ev.get("competitions", [])
            if comps:
                cs_list = comps[0].get("competitors", [])
                hc = next((c for c in cs_list if c.get("homeAway") == "home"), None)
                ac = next((c for c in cs_list if c.get("homeAway") == "away"), None)
                if hc and ac:
                    matches[f"{hc['team']['displayName']} vs {ac['team']['displayName']} ({ev.get('date','')[:10]})"] = (hc, ac)
        if matches:
            hc, ac = matches[st.selectbox("Select Match:", list(matches.keys()))]
            hn, an = hc["team"]["displayName"], ac["team"]["displayName"]
            hsc, hcon, hcs, hfts = get_stats(lg_slug, hc["team"]["id"])
            asc, acon, acs, afts = get_stats(lg_slug, ac["team"]["id"])
            ch, ca = st.columns(2)
            with ch: st.markdown(f'<div class="team-box"><b>🏠 {hn}</b><br><span style="color:#34d399;font-size:12px;">GF: {hsc} | GA: {hcon}<br>CS: {hcs}% | FTS: {hfts}%</span></div>', unsafe_allow_html=True)
            with ca: st.markdown(f'<div class="team-box"><b>✈️ {an}</b><br><span style="color:#60a5fa;font-size:12px;">GF: {asc} | GA: {acon}<br>CS: {acs}% | FTS: {afts}%</span></div>', unsafe_allow_html=True)
            adv1 = st.checkbox("Home Advantage (+8%)", value=True, key="a1")
            if st.button("🎯 Predict Correct Score", use_container_width=True, key="b1"):
                calculate_correct_scores(hn, an, hsc, hcon, asc, acon, hcs, hfts, acs, afts, adv1)
        else:
            st.warning("No upcoming matches found.")
    else:
        st.warning("No matches in the next 10 days. Try another league or Manual Input.")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        mh = st.text_input("Home Team", "Home Team")
        mh_sc = st.number_input("Goals Scored", 0.1, 5.0, 1.8, 0.1)
        mh_con = st.number_input("Goals Conceded", 0.1, 5.0, 0.8, 0.1)
        mh_cs = st.slider("Clean Sheet %", 0, 100, 40, key="hcs")
        mh_fts = st.slider("Failed to Score %", 0, 100, 15, key="hfts")
    with c2:
        ma = st.text_input("Away Team", "Away Team")
        ma_sc = st.number_input("Goals Scored ", 0.1, 5.0, 1.3, 0.1)
        ma_con = st.number_input("Goals Conceded ", 0.1, 5.0, 1.1, 0.1)
        ma_cs = st.slider("Clean Sheet % ", 0, 100, 25, key="acs")
        ma_fts = st.slider("Failed to Score % ", 0, 100, 25, key="afts")
    adv2 = st.checkbox("Home Advantage (+8%)", value=True, key="a2")
    if st.button("🎯 Calculate Correct Score", use_container_width=True, key="b2"):
        calculate_correct_scores(mh, ma, mh_sc, mh_con, ma_sc, ma_con, mh_cs, mh_fts, ma_cs, ma_fts, adv2)
