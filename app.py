import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Notatnik", page_icon="📝", layout="wide")

# --- DESIGN: CLEAN & FAST ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    
    /* Stylizacja wejścia tekstowego a la komunikator */
    .stTextArea textarea {
        background-color: #f0f2f5 !important;
        border-radius: 15px !important;
        border: 1px solid #d1d7db !important;
    }

    /* Karty ostatnich notatek */
    .note-card {
        background-color: #fff9c4;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #fbc02d;
        margin-bottom: 10px;
        font-family: 'Segoe UI', sans-serif;
    }

    .stButton>button {
        border-radius: 20px !important;
        background-color: #25d366 !important; /* WhatsApp Green */
        color: white !important;
        font-weight: bold;
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df = conn.read(ttl="0s")
        return df
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID"])

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

df = load_data()

# --- UKŁAD STRONY ---
col_main, col_cal = st.columns([1, 1], gap="large")

with col_main:
    st.title("📝 SQM: Szybka Notatka")
    
    # SEKCOJA: DODAJ TERAZ
    with st.container():
        note_text = st.text_area("", placeholder="Wpisz treść (np. dzwonił kierowca z naczepą SQM 123...)", height=100)
        c1, c2 = st.columns([3, 1])
        with c2:
            if st.button("ZAPISZ ✍️"):
                if note_text:
                    new_note = pd.DataFrame([{
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Note": note_text,
                        "ID": str(uuid.uuid4())
                    }])
                    df = pd.concat([df, new_note], ignore_index=True)
                    save_data(df)
                    st.rerun()

    st.markdown("---")
    st.subheader("🕒 Ostatnie wpisy")
    
    # Wyświetlamy 5 ostatnich notatek w formie kart
    if not df.empty:
        recent_notes = df.tail(5).iloc[::-1] # Ostatnie 5 od najnowszych
        for _, row in recent_notes.iterrows():
            st.markdown(f"""
            <div class="note-card">
                <small>{row['Date']} o {row['Timestamp']}</small><br>
                {row['Note']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Brak notatek. Wpisz coś powyżej.")

with col_cal:
    st.subheader("📅 Archiwum w kalendarzu")
    
    events = []
    if not df.empty:
        for _, row in df.iterrows():
            events.append({
                "title": f"{row['Timestamp']} - {row['Note'][:30]}...",
                "start": str(row['Date']),
                "allDay": True,
                "color": "#fbc02d"
            })

    calendar(events=events, options={
        "initialView": "dayGridMonth",
        "firstDay": 1,
        "locale": "pl",
        "height": "600px"
    }, key="simple_cal")

# --- ZARZĄDZANIE ---
with st.expander("🛠️ Pełna lista / Usuwanie"):
    if not df.empty:
        st.dataframe(df.sort_values(by=['Date', 'Timestamp'], ascending=False), use_container_width=True)
        to_del = st.selectbox("Wybierz do usunięcia", df.index)
        if st.button("USUŃ WPIS"):
            df = df.drop(to_del)
            save_data(df)
            st.rerun()
