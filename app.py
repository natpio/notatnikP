import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# Konfiguracja SQM
st.set_page_config(page_title="SQM Logi-Station", page_icon="🤠", layout="wide")

# STYL: RUSTIC MODERN DASHBOARD
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lora:ital,wght@0,400;1,700&display=swap');
    
    .stApp { background-color: #e8e2d9; color: #2b1d12; }
    
    section[data-testid="stSidebar"] {
        background-color: #3e2723 !important;
        color: #f4ece2 !important;
        border-right: 5px solid #8d6e63;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] p {
        color: #f4ece2 !important;
    }

    .metric-card {
        background-color: #ffffff99;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #8d6e63;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }

    .fc { 
        background-color: #fff; 
        border-radius: 20px; 
        padding: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    .stButton>button { 
        border-radius: 30px !important;
        background-color: #8d6e63 !important;
        color: white !important;
        border: none !important;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Połączenie
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0s")

def save_data(dataframe):
    conn.update(data=dataframe)
    st.cache_data.clear()

# Załadowanie i czyszczenie danych
try:
    df = load_data()
    # Konwersja kolumny Date na string, aby uniknąć problemów z typami
    if not df.empty:
        df['Date'] = df['Date'].astype(str)
except:
    df = pd.DataFrame(columns=["Date", "Note", "Type", "ID"])

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("# 🤠 SQM LOGI\n**STATION v2.0**")
    st.markdown("---")
    
    st.subheader("➕ Nowy Wpis")
    with st.form("sidebar_form", clear_on_submit=True):
        f_date = st.date_input("Data", value=datetime.now())
        f_type = st.selectbox("Kategoria", ["🚛 Transport", "📦 Załadunek", "⏱️ Slot", "🛠️ Serwis", "📝 Inne"])
        f_note = st.text_area("Szczegóły")
        
        if st.form_submit_button("DODAJ"):
            new_row = pd.DataFrame([{
                "Date": f_date.strftime("%Y-%m-%d"), 
                "Note": f_note, 
                "Type": f_type, 
                "ID": str(uuid.uuid4())
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.rerun()

    st.markdown("---")
    if not df.empty:
        to_del = st.selectbox("Usuń wpis", options=df.index, format_func=lambda x: f"{df.at[x, 'Date']} - {df.at[x, 'Type']}")
        if st.button("❌ USUŃ"):
            df = df.drop(to_del)
            save_data(df)
            st.rerun()

# --- PANEL GŁÓWNY ---

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card"><h3>📅 Dzisiaj</h3><p>{datetime.now().strftime("%d %B")}</p></div>', unsafe_allow_html=True)
with m2:
    # BEZPIECZNE LICZENIE ZADAŃ (Naprawa błędu TypeError)
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        if not df.empty:
            # Filtrujemy tylko wiersze, które mają poprawny format daty
            valid_dates = df[df['Date'].str.match(r'\d{4}-\d{2}-\d{2}', na=False)]
            upcoming = len(valid_dates[valid_dates['Date'] >= today_str])
        else:
            upcoming = 0
    except:
        upcoming = 0
    st.markdown(f'<div class="metric-card"><h3>🚚 Nadchodzące</h3><p>{upcoming} zadań</p></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><h3>🏢 Firma</h3><p>SQM Solutions</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Kalendarz
calendar_events = []
color_map = {
    "🚛 Transport": "#5d4037", "📦 Załadunek": "#8d6e63",
    "⏱️ Slot": "#4e342e", "🛠️ Serwis": "#a1887f", "📝 Inne": "#d7ccc8"
}

if not df.empty:
    for _, row in df.iterrows():
        # Sprawdzamy czy data nie jest pusta i ma sensowny format
        if pd.notna(row['Date']) and len(str(row['Date'])) >= 10:
            calendar_events.append({
                "title": f"{row.get('Type', '📝')} | {row['Note']}",
                "start": str(row['Date']),
                "id": str(row['ID']),
                "color": color_map.get(row.get('Type'), "#8d6e63"),
                "allDay": True
            })

st.markdown("### 🗺️ Widok Operacyjny")
calendar(
    events=calendar_events,
    options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth", "firstDay": 1, "locale": "pl", "height": "700px",
    },
    key="modern_cal"
)

with st.expander("📊 Arkusz"):
    st.dataframe(df, use_container_width=True)
