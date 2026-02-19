import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Country Terminal", page_icon="🤠", layout="wide")

# --- DESIGN: DEEP COUNTRY (WOOD & PAPER) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Courier+Prime:wght@400;700&display=swap');

    /* Tło - efekt drewnianego blatu */
    .stApp {
        background-color: #3e2723;
        background-image: url("https://www.transparenttextures.com/patterns/wood-pattern.png");
        color: #efebe9;
    }

    /* Kartki z notatkami (Stary papier) */
    .note-paper {
        background-color: #fff9c4;
        background-image: url("https://www.transparenttextures.com/patterns/beige-paper.png");
        color: #3e2723;
        padding: 20px;
        margin-bottom: 15px;
        border-radius: 2px;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
        font-family: 'Special Elite', cursive;
        border-left: 10px solid #8d6e63;
        transform: rotate(-1deg);
    }

    /* Stylizacja pól tekstowych */
    .stTextArea textarea {
        background-color: #efebe9 !important;
        font-family: 'Courier Prime', monospace !important;
        border: 3px solid #5d4037 !important;
        color: #3e2723 !important;
    }

    /* Nagłówki */
    h1, h2, h3 {
        font-family: 'Special Elite', cursive !important;
        color: #d7ccc8 !important;
        text-shadow: 2px 2px #1a1a1a;
    }

    /* Przycisk - wypalane drewno */
    .stButton>button {
        background-color: #5d4037 !important;
        color: #d7ccc8 !important;
        border: 2px solid #8d6e63 !important;
        font-family: 'Special Elite', cursive !important;
        padding: 10px 20px !important;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #8d6e63 !important;
        color: #ffffff !important;
        transform: scale(1.02);
    }

    /* Kalendarz */
    .fc { 
        background: #efebe9 !important; 
        color: #3e2723 !important; 
        padding: 15px; 
        border-radius: 5px;
        font-family: 'Courier Prime', monospace;
    }
</style>
""", unsafe_allow_html=True)

# --- SILNIK DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    return conn.read(ttl="0s")

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

df = load_data()

# --- UKŁAD ---
st.markdown("# 🤠 SQM LOGISTICS: COUNTRY NOTES")

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.subheader("📝 Szybka Notatka (Dzwonią / Piszą)")
    
    # Formularz - zapobiega mruganiu podczas pisania
    with st.form("country_form", clear_on_submit=True):
        txt = st.text_area("", height=150, placeholder="Pisz tutaj... (np. WhatsApp od kierowcy)")
        submitted = st.form_submit_button("PRZYBIJ DO TABLICY (ENTER)")
        
        if submitted and txt:
            now = datetime.now()
            new_note = pd.DataFrame([{
                "Timestamp": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Note": txt,
                "ID": str(uuid.uuid4())
            }])
            df = pd.concat([df, new_note], ignore_index=True)
            save_data(df)
            st.rerun()

    st.markdown("---")
    st.subheader("📌 Ostatnie na blacie")
    
    if not df.empty:
        # Pokazujemy 3 ostatnie notatki w stylu "kartek"
        recent = df.tail(3).iloc[::-1]
        for _, row in recent.iterrows():
            st.markdown(f"""
            <div class="note-paper">
                <small>GODZ: {row['Timestamp']} | DATA: {row['Date']}</small><br>
                <div style="font-size: 1.2rem; margin-top: 10px;">{row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)

with col_right:
    st.subheader("📅 Rejestr")
    
    events = []
    if not df.empty:
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                events.append({
                    "title": f"{row['Timestamp']} - {row['Note'][:30]}",
                    "start": str(row['Date']),
                    "color": "#5d4037"
                })

    calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "firstDay": 1,
            "locale": "pl",
            "height": 550,
            "selectable": False
        },
        key="country_calendar"
    )

    with st.expander("📂 Archiwum i Usuwanie"):
        if not df.empty:
            st.dataframe(df.sort_values(by=['Date', 'Timestamp'], ascending=False), use_container_width=True)
            to_del = st.selectbox("Wybierz wpis do spalenia", options=df.index, format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:20]}")
            if st.button("USUŃ WPIS"):
                df = df.drop(to_del)
                save_data(df)
                st.rerun()
