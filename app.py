import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# Konfiguracja SQM
st.set_page_config(page_title="SQM Logi-Station", page_icon="🤠", layout="wide")

# NOWY STYL: "RUSTIC MODERN DASHBOARD"
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Lora:ital,wght@0,400;1,700&display=swap');
    
    .stApp { 
        background-color: #e8e2d9; 
        color: #2b1d12; 
    }
    
    /* Pasek boczny jako centrum dowodzenia */
    section[data-testid="stSidebar"] {
        background-color: #3e2723 !important;
        color: #f4ece2 !important;
        border-right: 5px solid #8d6e63;
    }
    
    section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] p {
        color: #f4ece2 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Karty statystyk na górze */
    .metric-card {
        background-color: #ffffff99;
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #8d6e63;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        text-align: center;
    }

    /* Stylizacja Kalendarza */
    .fc { 
        background-color: #fff; 
        border-radius: 20px; 
        padding: 25px;
        border: none;
        box-shadow: 0 15px 35px rgba(0,0,0,0.1);
    }
    
    .fc-toolbar-title {
        font-family: 'Lora', serif !important;
        font-weight: bold !important;
        color: #5d4037;
    }

    /* Przyciski operacyjne */
    .stButton>button { 
        border-radius: 30px !important;
        background-color: #8d6e63 !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 2rem !important;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #a1887f !important;
        transform: scale(1.05);
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

# Inicjalizacja danych
try:
    df = load_data()
    if "Type" not in df.columns: df["Type"] = "Notatka"
    if "ID" not in df.columns: df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
except:
    df = pd.DataFrame(columns=["Date", "Note", "Type", "ID"])

# --- SIDEBAR: CENTRUM STEROWANIA ---
with st.sidebar:
    st.markdown("# 🤠 SQM LOGI\n**STATION v2.0**")
    st.markdown("---")
    
    st.subheader("➕ Nowy Wpis")
    with st.form("sidebar_form", clear_on_submit=True):
        f_date = st.date_input("Data", value=datetime.now())
        f_type = st.selectbox("Kategoria", ["🚛 Transport", "📦 Załadunek", "⏱️ Slot", "🛠️ Serwis", "📝 Inne"])
        f_note = st.text_area("Szczegóły", placeholder="Co, gdzie, kto?")
        
        if st.form_submit_button("DODAJ DO HARMONOGRAMU"):
            new_row = pd.DataFrame([{"Date": f_date.strftime("%Y-%m-%d"), "Note": f_note, "Type": f_type, "ID": str(uuid.uuid4())}])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Dodano!")
            st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Zarządzanie")
    if not df.empty:
        to_delete = st.selectbox("Usuń wpis", options=df.index, format_func=lambda x: f"{df.at[x, 'Date']} - {df.at[x, 'Type']}")
        if st.button("❌ USUŃ ZAZNACZONY"):
            df = df.drop(to_delete)
            save_data(df)
            st.warning("Usunięto.")
            st.rerun()

# --- PANEL GŁÓWNY ---

# 1. Statystyki na górze
m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f'<div class="metric-card"><h3>📅 Dzisiaj</h3><p>{datetime.now().strftime("%d %B")}</p></div>', unsafe_allow_html=True)
with m2:
    total_tasks = len(df[df['Date'] >= datetime.now().strftime("%Y-%m-%d")])
    st.markdown(f'<div class="metric-card"><h3>🚚 Nadchodzące</h3><p>{total_tasks} zadań</p></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card"><h3>🏢 Firma</h3><p>SQM Solutions</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# 2. Kalendarz (Główny punkt programu)
calendar_events = []
# Mapowanie kolorów dla typów
color_map = {
    "🚛 Transport": "#5d4037",
    "📦 Załadunek": "#8d6e63",
    "⏱️ Slot": "#4e342e",
    "🛠️ Serwis": "#a1887f",
    "📝 Inne": "#d7ccc8"
}

for _, row in df.iterrows():
    if pd.notna(row['Date']) and str(row['Date']).strip() != "":
        calendar_events.append({
            "title": f"{row.get('Type', '📝')} | {row['Note']}",
            "start": str(row['Date']),
            "id": str(row['ID']),
            "color": color_map.get(row.get('Type'), "#8d6e63"),
            "allDay": True
        })

# Wyświetlenie kalendarza
st.markdown("### 🗺️ Widok Operacyjny")
calendar(
    events=calendar_events,
    options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listMonth"},
        "initialView": "dayGridMonth",
        "firstDay": 1,
        "locale": "pl",
        "height": "700px",
    },
    key="modern_cal"
)

# 3. Dolna tabela
with st.expander("📊 Pełna Baza Danych (Arkusz)"):
    st.dataframe(df, use_container_width=True)
