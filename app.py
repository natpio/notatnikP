import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# Konfiguracja SQM
st.set_page_config(page_title="SQM Notatnik Logistyka", page_icon="🤠", layout="wide")

# ZAAWANSOWANY STYL COUNTRY
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Lora:wght@400;700&display=swap');
    
    /* Główne tło */
    .stApp { 
        background-color: #f4ece2; 
        color: #3e2723; 
    }
    
    /* Nagłówki */
    h1, h2, h3 { 
        font-family: 'Special+Elite', serif; 
        color: #5d4037 !important; 
        text-align: center;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }

    /* Stylizacja kart */
    div[data-testid="stVerticalBlock"] > div.stVerticalBlock {
        background-color: #ffffff77;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #d7ccc8;
    }

    /* Przyciski */
    .stButton>button { 
        width: 100%;
        background-color: #8d6e63 !important; 
        color: #ffffff !important; 
        border: none !important;
        font-family: 'Lora', serif; 
        padding: 10px;
        font-weight: bold;
        border-radius: 8px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton>button:hover {
        background-color: #5d4037 !important;
        transform: translateY(-2px);
    }

    /* Kalendarz */
    .fc { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border: 2px solid #8d6e63;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    }

    /* Wygląd zakładek */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #d7ccc8;
        border-radius: 5px 5px 0 0;
        padding: 10px 20px;
        color: #5d4037;
    }
    .stTabs [aria-selected="true"] {
        background-color: #8d6e63 !important;
        color: white !important;
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

# Ładowanie danych
try:
    df = load_data()
    if "ID" not in df.columns:
        df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
except:
    df = pd.DataFrame(columns=["Date", "Note", "Type", "ID"])

# --- INTERFEJS ---

st.title("🤠 SQM: Logistyka i Plany")
st.markdown("<p style='text-align: center; font-style: italic;'>Zarządzanie transportem w starym dobrym stylu</p>", unsafe_allow_html=True)

# Przygotowanie zdarzeń
calendar_events = []
if not df.empty:
    for _, row in df.iterrows():
        if pd.notna(row['Date']) and str(row['Date']).strip() != "":
            # Różne kolory dla typów (opcjonalnie)
            event_color = "#8d6e63"
            if "Type" in df.columns:
                if row['Type'] == "Załadunek": event_color = "#455a64"
                if row['Type'] == "Slot": event_color = "#6d4c41"

            calendar_events.append({
                "title": f"[{row.get('Type', 'Notatka')}] {row['Note']}",
                "start": str(row['Date']),
                "id": str(row['ID']),
                "color": event_color
            })

# Układ główny
col_cal, col_side = st.columns([2.5, 1], gap="large")

with col_cal:
    st.markdown("### 📅 Harmonogram")
    state = calendar(
        events=calendar_events,
        options={
            "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
            "firstDay": 1,
            "locale": "pl",
            "height": 650
        },
        key="sqm_calendar_pro"
    )
    
    if state.get("dateClick"):
        st.session_state["clicked_date"] = state["dateClick"]["date"].split("T")[0]

with col_side:
    st.markdown("### 🛠️ Panel Akcji")
    
    tab_add, tab_edit = st.tabs(["🆕 Dodaj", "✏️ Edycja"])
    
    with tab_add:
        with st.container():
            def_date = st.session_state.get("clicked_date", datetime.now().strftime("%Y-%m-%d"))
            d_val = st.date_input("Data zdarzenia", value=datetime.strptime(def_date, "%Y-%m-%d"))
            t_val = st.selectbox("Typ", ["Notatka", "Załadunek", "Rozładunek", "Slot", "Serwis"])
            n_val = st.text_area("Szczegóły (np. nr naczepy, kierowca)", placeholder="Wpisz tutaj...")
            
            if st.button("➕ ZAPISZ W SYSTEMIE"):
                new_entry = pd.DataFrame([{
                    "Date": d_val.strftime("%Y-%m-%d"), 
                    "Note": n_val, 
                    "Type": t_val,
                    "ID": str(uuid.uuid4())
                }])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success("Zapisano pomyślnie!")
                st.rerun()

    with tab_edit:
        if not df.empty:
            idx = st.selectbox("Wybierz wpis do zmiany", options=df.index, 
                               format_func=lambda x: f"{df.at[x, 'Date']} - {str(df.at[x, 'Note'])[:15]}...")
            
            e_type = st.selectbox("Zmień Typ", ["Notatka", "Załadunek", "Rozładunek", "Slot", "Serwis"], 
                                  index=["Notatka", "Załadunek", "Rozładunek", "Slot", "Serwis"].index(df.at[idx, 'Type']) if "Type" in df.columns else 0)
            e_note = st.text_area("Popraw szczegóły", value=df.at[idx, 'Note'])
            
            col_u, col_d = st.columns(2)
            with col_u:
                if st.button("💾 ZMIEŃ"):
                    df.at[idx, 'Note'] = e_note
                    df.at[idx, 'Type'] = e_type
                    save_data(df)
                    st.rerun()
            with col_d:
                if st.button("🗑️ USUŃ"):
                    df = df.drop(idx)
                    save_data(df)
                    st.rerun()
        else:
            st.info("Brak wpisów.")

st.markdown("---")
with st.expander("🔍 Podgląd bazy danych (Raw Data)"):
    st.dataframe(df, use_container_width=True)
