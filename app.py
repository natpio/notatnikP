import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Country Log", page_icon="🤠", layout="wide")

# --- DESIGN: EXTREME COUNTRY ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Rye&family=Permanent+Marker&display=swap');

    /* Tło - Ciemne, surowe drewno */
    .stApp {
        background-color: #2b1d12;
        background-image: url("https://www.transparenttextures.com/patterns/dark-wood.png");
        color: #d7ccc8;
    }

    /* Nagłówek w stylu Wanted Poster */
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

    /* Kartki notatek - "przybite" do drewna */
    .note-paper {
        background-color: #e2cfb6;
        background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png");
        color: #2b1d12;
        padding: 25px;
        margin: 20px 10px;
        border-radius: 2px;
        box-shadow: 10px 10px 20px rgba(0,0,0,0.6);
        font-family: 'Special Elite', cursive;
        position: relative;
        border: 1px solid #c0a080;
    }

    /* Efekt gwoździa */
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

    /* Formularz */
    .stForm {
        background: rgba(0,0,0,0.3);
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #5d4037;
    }

    .stTextArea textarea {
        background-color: #f5f5f5 !important;
        font-family: 'Special Elite', cursive !important;
        font-size: 1.1rem !important;
    }

    /* Przyciski - żeliwny styl */
    .stButton>button {
        background-color: #4e342e !important;
        color: #d4af37 !important;
        font-family: 'Rye', cursive !important;
        font-size: 1.2rem !important;
        border: 2px solid #d4af37 !important;
        border-radius: 0px !important;
        box-shadow: 4px 4px 0px #000;
    }

    .stButton>button:hover {
        background-color: #d4af37 !important;
        color: #2b1d12 !important;
    }

    /* Kalendarz na starej tablicy */
    .fc { 
        background: #fdf5e6 !important; 
        color: #2b1d12 !important; 
        padding: 10px; 
        border: 5px solid #5d4037;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0s")

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

df = load_data()

# --- INTERFEJS ---
st.markdown('<div class="wanted-header">NOTES</div>', unsafe_allow_html=True)

col_input, col_display = st.columns([1, 1.2], gap="large")

with col_input:
    st.subheader("🤠 Rzuć notatkę na stół")
    
    with st.form("hard_country_form", clear_on_submit=True):
        note_txt = st.text_area("Co się dzieje?", height=180, placeholder="Np. WhatsApp od klienta: Transport potwierdzony na 8:00...")
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
            save_data(df)
            st.rerun()

    st.markdown("---")
    st.subheader("📜 Ostatnie meldunki")
    
    if not df.empty:
        # 3 najświeższe "przypięte" kartki
        recent = df.tail(3).iloc[::-1]
        for i, row in recent.iterrows():
            st.markdown(f"""
            <div class="note-paper">
                <div style="text-align:right; font-size:0.7rem; color:#555;">ID: {row['ID'][:8]}</div>
                <div style="font-size: 0.9rem; border-bottom: 1px solid #999; margin-bottom: 10px;">
                    📅 {row['Date']} | ⏰ {row['Timestamp']}
                </div>
                <div style="font-size: 1.2rem; line-height: 1.4;">{row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)

with col_display:
    st.subheader("📅 Kalendarz Szeryfa")
    
    calendar_events = []
    if not df.empty:
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                calendar_events.append({
                    "title": f"🕒 {row['Timestamp']} - {row['Note'][:25]}...",
                    "start": str(row['Date']),
                    "color": "#4e342e"
                })

    calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "firstDay": 1,
            "locale": "pl",
            "height": 580,
            "selectable": False
        },
        key="ultra_country_cal"
    )

    with st.expander("🛠️ Zarządzaj archiwum (Usuń/Edytuj)"):
        if not df.empty:
            st.dataframe(df.sort_values(by=['Date', 'Timestamp'], ascending=False), use_container_width=True)
            to_burn = st.selectbox("Wybierz wpis do usunięcia", options=df.index, format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:30]}")
            if st.button("SPAL NOTATKĘ"):
                df = df.drop(to_burn)
                save_data(df)
                st.rerun()
