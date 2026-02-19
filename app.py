import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Country Log", page_icon="🤠", layout="wide")

# --- DESIGN: EXTREME COUNTRY (Wszystkie notatki na kartkach) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Rye&display=swap');

    .stApp {
        background-color: #2b1d12;
        background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
        color: #d7ccc8;
    }

    .wanted-header {
        font-family: 'Rye', cursive;
        font-size: 3.5rem;
        color: #d4af37;
        text-align: center;
        text-shadow: 3px 3px 0px #000;
        margin-bottom: 30px;
        border: 4px double #d4af37;
        padding: 20px;
    }

    /* Styl kartki przybitej do drewna */
    .note-paper {
        background-color: #e2cfb6;
        background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png");
        color: #2b1d12;
        padding: 25px;
        margin: 20px 0px;
        border-radius: 2px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.6);
        font-family: 'Special Elite', cursive;
        position: relative;
        border: 1px solid #c0a080;
        min-height: 100px;
    }

    /* Gwóźdź */
    .note-paper::before {
        content: '';
        position: absolute;
        top: 10px;
        left: 50%;
        width: 15px;
        height: 15px;
        background: #444;
        border-radius: 50%;
        box-shadow: inset 2px 2px 5px #000;
        transform: translateX(-50%);
    }

    .stTextArea textarea {
        background-color: #f5f5f5 !important;
        font-family: 'Special Elite', cursive !important;
    }

    .stButton>button {
        background-color: #4e342e !important;
        color: #d4af37 !important;
        font-family: 'Rye', cursive !important;
        border: 2px solid #d4af37 !important;
        width: 100%;
    }

    .fc { background: #fdf5e6 !important; color: #2b1d12 !important; border: 5px solid #5d4037; }
</style>
""", unsafe_allow_html=True)

# --- BEZPIECZNE POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl="1s" stabilizuje API i zapobiega nadmiernym zapytaniom powodującym błędy
        return conn.read(ttl="1s")
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID"])

df = load_data()

# --- INTERFEJS ---
st.markdown('<div class="wanted-header">SQM LOGISTICS TERMINAL</div>', unsafe_allow_html=True)

col_input, col_display = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("🤠 Przybij nową notatkę")
    with st.form("hard_country_form", clear_on_submit=True):
        note_txt = st.text_area("", height=150, placeholder="Dzwonił kierowca... / Mail od cyryl wjazdówki...")
        submit_btn = st.form_submit_button("PRZYBIJ DO TABLICY")
        
        if submit_btn and note_txt:
            now = datetime.now()
            new_entry = pd.DataFrame([{
                "Timestamp": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Note": note_txt,
                "ID": str(uuid.uuid4())
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            st.rerun()

    st.markdown("---")
    st.subheader("📜 Tablica wszystkich notatek")
    
    if not df.empty:
        # Sortujemy od najnowszych na górze
        sorted_df = df.sort_values(by=['Date', 'Timestamp'], ascending=False)
        for i, row in sorted_df.iterrows():
            # Każda notatka jako karteczka
            st.markdown(f"""
            <div class="note-paper">
                <div style="font-size: 0.8rem; border-bottom: 1px solid #999; margin-bottom: 8px; color: #555;">
                    📅 {row['Date']} | ⏰ {row['Timestamp']} | <small>ID: {str(row['ID'])[:8]}</small>
                </div>
                <div style="font-size: 1.1rem; line-height: 1.3;">{row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Mały przycisk usuwania pod każdą kartką
            if st.button(f"Spal tę kartkę (ID: {str(row['ID'])[:8]})", key=f"del_{row['ID']}"):
                df = df[df['ID'] != row['ID']]
                conn.update(data=df)
                st.cache_data.clear()
                st.rerun()
    else:
        st.info("Tablica jest pusta.")

with col_display:
    st.subheader("📅 Kalendarz Szeryfa")
    
    calendar_events = []
    if not df.empty:
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                calendar_events.append({
                    "title": f"🕒 {row['Timestamp']} - {row['Note'][:20]}...",
                    "start": str(row['Date']),
                    "color": "#4e342e"
                })

    calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "firstDay": 1,
            "locale": "pl",
            "height": 600,
            "selectable": False
        },
        key="ultra_country_cal"
    )
