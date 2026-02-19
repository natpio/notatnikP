import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Sheriff Office", page_icon="🤠", layout="wide")

# --- DESIGN: FRONTIER TERMINAL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Rye&family=Courier+Prime&display=swap');

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
        margin-bottom: 20px;
        border: 4px double #d4af37;
        padding: 20px;
    }

    /* Kartki zwykłe i PILNE (WANTED) */
    .note-paper {
        background-color: #e2cfb6;
        background-image: url("https://www.transparenttextures.com/patterns/paper-fibers.png");
        color: #2b1d12;
        padding: 25px;
        margin: 15px 0px;
        border-radius: 2px;
        box-shadow: 8px 8px 15px rgba(0,0,0,0.6);
        font-family: 'Special Elite', cursive;
        position: relative;
        border: 1px solid #c0a080;
    }

    .note-urgent {
        background-color: #b71c1c !important;
        color: #ffffff !important;
        border: 3px solid #d4af37 !important;
    }

    .note-paper::before {
        content: '';
        position: absolute;
        top: 10px;
        left: 50%;
        width: 14px;
        height: 14px;
        background: #333;
        border-radius: 50%;
        transform: translateX(-50%);
        box-shadow: 1px 1px 3px #000;
    }

    /* Stylizacja wejścia */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        font-family: 'Special Elite', cursive !important;
        color: #1a1a1a !important;
    }

    /* Przyciski telegrafu */
    .telegraph-btn {
        background-color: #5d4037 !important;
        border: 1px solid #d4af37 !important;
        color: #d4af37 !important;
        font-family: 'Rye', cursive !important;
        margin-bottom: 5px;
    }

    .fc { background: #fdf5e6 !important; color: #2b1d12 !important; border: 5px solid #5d4037; }
</style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA STANU ---
if 'edit_content' not in st.session_state: st.session_state['edit_content'] = ""

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)
def load_data():
    try:
        df = conn.read(ttl="1s")
        if "Priority" not in df.columns: df["Priority"] = "Normal"
        return df
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "Priority", "ID"])

df = load_data()

# --- NAGŁÓWEK ---
st.markdown('<div class="wanted-header">SQM LOGISTICS: SHERIFF OFFICE</div>', unsafe_allow_html=True)

col_input, col_display = st.columns([1, 1.2], gap="large")

with col_input:
    # 1. TELEGRAF (Szybkie szablony)
    st.markdown("### 📟 Telegraf (Szybkie akcje)")
    t1, t2, t3 = st.columns(3)
    with t1:
        if st.button("🚛 Transport OK"): st.session_state['edit_content'] = "TRANSPORT W DRODZE: "
    with t2:
        if st.button("⏱️ Slot Potwierdzony"): st.session_state['edit_content'] = "SLOT POTWIERDZONY: "
    with t3:
        if st.button("⚠️ Opóźnienie"): st.session_state['edit_content'] = "⚠️ OPÓŹNIENIE: "

    # 2. FORMULARZ ZAPISU
    with st.form("sheriff_form", clear_on_submit=True):
        note_txt = st.text_area("Meldunek:", value=st.session_state['edit_content'], height=150)
        prio = st.checkbox("🔥 PILNE (WANTED)")
        if st.form_submit_button("PRZYBIJ DO ŚCIANY"):
            if note_txt:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Note": note_txt,
                    "Priority": "High" if prio else "Normal",
                    "ID": str(uuid.uuid4())
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.cache_data.clear()
                st.session_state['edit_content'] = ""
                st.rerun()

    # 3. SZUKAJ W AKTACH
    st.markdown("---")
    search_query = st.text_input("🔍 Przeszukaj akta szeryfa:", placeholder="Wpisz np. Berlin, Nazwisko, Nr...")

    # 4. TABLICA OGŁOSZEŃ
    st.subheader("📜 Tablica Ogłoszeń")
    if not df.empty:
        display_df = df.copy()
        if search_query:
            display_df = display_df[display_df['Note'].str.contains(search_query, case=False, na=False)]
        
        for i, row in display_df.sort_values(by=['Date', 'Timestamp'], ascending=False).iterrows():
            prio_class = "note-urgent" if row.get('Priority') == "High" else ""
            st.markdown(f"""
            <div class="note-paper {prio_class}">
                <div style="font-size: 0.8rem; border-bottom: 1px solid rgba(0,0,0,0.2); margin-bottom: 8px;">
                    📅 {row['Date']} | ⏰ {row['Timestamp']} { ' | 🚨 WANTED' if row.get('Priority') == 'High' else ''}
                </div>
                <div style="font-size: 1.1rem; line-height: 1.3;">{row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"✏️ Edytuj", key=f"ed_{row['ID']}"):
                    st.session_state['edit_content'] = row['Note']
                    st.rerun()
            with b2:
                if st.button(f"🔥 Spal", key=f"sp_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.rerun()

with col_display:
    st.subheader("📅 Mapa Czasu")
    events = []
    if not df.empty:
        for _, row in df.iterrows():
            events.append({
                "title": f"{row['Timestamp']} - {row['Note'][:20]}",
                "start": str(row['Date']),
                "color": "#b71c1c" if row.get('Priority') == "High" else "#5d4037"
            })
    calendar(events=events, options={"initialView": "dayGridMonth", "locale": "pl", "height": 600}, key="sheriff_cal")
    
    st.markdown("---")
    st.markdown("### 🏜️ SQM Logistics Status")
    st.write("Wszystkich notatek w archiwum:", len(df))
