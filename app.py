import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime, timedelta

# --- KONFIGURACJA EKOSYSTEMU ---
st.set_page_config(page_title="SQM Control Tower", page_icon="🏗️", layout="wide")

# --- DESIGN: CYBER-RUSTIC (Nowoczesna logistyka + styl country) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto+Condensed:wght@300;700&display=swap');

    .stApp { background: linear-gradient(135deg, #e8e2d9 0%, #d7ccc8 100%); color: #2b1d12; }
    
    /* Nagłówek Tower */
    .tower-header {
        font-family: 'Bebas Neue', cursive;
        font-size: 3rem;
        letter-spacing: 4px;
        color: #3e2723;
        text-align: left;
        border-bottom: 5px solid #8d6e63;
        margin-bottom: 20px;
    }

    /* Karty Timeline */
    .timeline-card {
        background: white;
        padding: 15px;
        border-radius: 0px 15px 15px 0px;
        border-left: 10px solid #5d4037;
        margin-bottom: 10px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.05);
    }

    /* Kalendarz Szklany */
    .fc { 
        background: rgba(255, 255, 255, 0.7) !important;
        backdrop-filter: blur(10px);
        border-radius: 25px !important;
        border: 1px solid white !important;
        padding: 20px;
    }

    /* Przyciski Akcji */
    .stButton>button {
        border-radius: 0px !important;
        background: #3e2723 !important;
        color: #f4ece2 !important;
        border: 1px solid #8d6e63 !important;
        height: 50px;
        font-family: 'Bebas Neue';
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0s")

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

try:
    df = load_data()
    if "Priority" not in df.columns: df["Priority"] = "Normal"
    df['Date'] = df['Date'].astype(str)
except:
    df = pd.DataFrame(columns=["Date", "Note", "Type", "Priority", "ID"])

# --- UKŁAD STRONY ---
st.markdown('<div class="tower-header">SQM LOGISTICS CONTROL TOWER</div>', unsafe_allow_html=True)

col_timeline, col_main, col_tools = st.columns([1, 2.5, 1], gap="medium")

# --- STREFA 1: TIMELINE (Najbliższe 48h) ---
with col_timeline:
    st.subheader("⚡ NASTĘPNE 48H")
    today = datetime.now()
    tomorrow = today + timedelta(days=2)
    
    # Filtrowanie wpisów na teraz
    if not df.empty:
        df_now = df[df['Date'].between(today.strftime("%Y-%m-%d"), tomorrow.strftime("%Y-%m-%d"))]
        if df_now.empty:
            st.info("Brak pilnych zadań.")
        for _, row in df_now.sort_values('Date').iterrows():
            prio_color = "#d32f2f" if row.get('Priority') == "Wysoki" else "#5d4037"
            st.markdown(f"""
            <div class="timeline-card" style="border-left-color: {prio_color}">
                <small>{row['Date']}</small><br>
                <b>{row['Type']}</b><br>
                {row['Note']}
            </div>
            """, unsafe_allow_html=True)

# --- STREFA 2: MAIN RADAR (Kalendarz) ---
with col_main:
    st.subheader("🗺️ RADAR OPERACYJNY")
    
    events = []
    colors = {"🚛 Transport": "#3e2723", "📦 Załadunek": "#8d6e63", "⏱️ Slot": "#bf360c", "🛠️ Serwis": "#546e7a"}
    
    for _, row in df.iterrows():
        if len(str(row['Date'])) >= 10:
            events.append({
                "title": f"{row['Type']} | {row['Note']}",
                "start": str(row['Date']),
                "backgroundColor": "#d32f2f" if row.get('Priority') == "Wysoki" else colors.get(row['Type'], "#8d6e63"),
                "borderColor": "white"
            })

    calendar(events=events, options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialView": "dayGridMonth",
        "locale": "pl",
        "height": "700px"
    }, key="tower_radar")

# --- STREFA 3: COMMAND CENTER (Narzędzia) ---
with col_tools:
    st.subheader("🕹️ KOMENDY")
    
    with st.expander("🆕 NOWY TRANSPORT", expanded=True):
        with st.form("add_tower"):
            d = st.date_input("Data")
            t = st.selectbox("Typ", ["🚛 Transport", "📦 Załadunek", "⏱️ Slot", "🛠️ Serwis"])
            p = st.select_slider("Priorytet", options=["Normal", "Wysoki"])
            n = st.text_area("Notatka")
            if st.form_submit_button("WYŚLIJ"):
                new = pd.DataFrame([{"Date": d.strftime("%Y-%m-%d"), "Note": n, "Type": t, "Priority": p, "ID": str(uuid.uuid4())}])
                df = pd.concat([df, new], ignore_index=True)
                save_data(df)
                st.rerun()

    with st.expander("🗑️ USUWANIE"):
        if not df.empty:
            sel = st.selectbox("Wybierz do usunięcia", df.index, format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:15]}")
            if st.button("POTWIERDŹ USUNIĘCIE"):
                df = df.drop(sel)
                save_data(df)
                st.rerun()

    st.markdown("---")
    st.write("📊 **STATYSTYKI**")
    st.write(f"Wszystkich wpisów: {len(df)}")
    st.progress(len(df)/100) # Progres do "pełnego miesiąca" (przykład)

# --- STOPKA ---
with st.expander("📝 LOGI SYSTEMOWE (ARKUSZ)"):
    st.dataframe(df, use_container_width=True)
