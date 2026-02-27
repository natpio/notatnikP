import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
import random
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SQM LOGISTICS: THE ONE WITH THE TRUCKS", 
    page_icon="☕", 
    layout="wide"
)

# --- SYSTEM DESIGNU (FRIENDS ULTRA) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Gloria+Hallelujah&display=swap');

    /* Tło - mieszkanie Moniki */
    .stApp {
        background-color: #6a5acd;
        background-image: url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* Logo Serialu */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5.5rem;
        text-align: center;
        color: white;
        text-shadow: 
            0 0 10px #fff,
            4px 4px #e74c3c, 
            8px 8px #f1c40f, 
            12px 12px #3498db;
        margin-bottom: 30px;
    }

    /* Notatka jako fioletowe drzwi */
    .door-card {
        background-color: #7b68ee;
        border: 10px solid #f1c40f; /* Żółta ramka wizjera */
        border-radius: 12px;
        padding: 30px;
        margin-bottom: 25px;
        box-shadow: 15px 15px 0px rgba(0,0,0,0.4);
        position: relative;
    }

    .peephole {
        position: absolute;
        top: 15px;
        left: 50%;
        transform: translateX(-50%);
        width: 35px;
        height: 35px;
        background: #333;
        border: 4px solid #f1c40f;
        border-radius: 50%;
    }

    .note-content {
        font-family: 'Gloria Hallelujah', cursive;
        font-size: 1.5rem;
        color: #fff;
        margin-top: 20px;
        line-height: 1.4;
    }

    /* Wielki przycisk PIVOT */
    .pivot-btn button {
        background: linear-gradient(45deg, #e74c3c, #f1c40f, #3498db) !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2.2rem !important;
        height: 80px !important;
        width: 100% !important;
        border: 4px solid white !important;
        color: white !important;
        transition: 0.3s;
    }
    
    .pivot-btn button:hover {
        transform: scale(1.02) rotate(-1deg);
    }

    /* Kalendarz */
    .fc { background: white !important; color: black !important; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA STANU SESJI ---
if 'delete_id' not in st.session_state:
    st.session_state.delete_id = ""
if 'edit_content' not in st.session_state:
    st.session_state.edit_content = ""

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl=0 zapewnia brak opóźnień w odświeżaniu przy usuwaniu
        data = conn.read(ttl=0)
        # Naprawa struktury tabeli (The One with the Missing Columns)
        required = ["Timestamp", "Date", "Note", "ID", "Category"]
        for col in required:
            if col not in data.columns:
                data[col] = ""
        return data
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category"])

df = load_data()

# --- LOGIKA USUWANIA (Triggerowana przed renderowaniem UI) ---
if st.session_state.delete_id != "":
    target = st.session_state.delete_id
    # Filtrujemy DataFrame
    df = df[df['ID'].astype(str) != str(target)]
    # Wysyłamy do Google Sheets
    conn.update(data=df)
    # Czyścimy cache i stan
    st.cache_data.clear()
    st.session_state.delete_id = ""
    st.toast("WE WERE ON A BREAK! (Notatka usunięta)")
    st.rerun()

# --- NAGŁÓWEK ---
st.markdown('<div class="friends-logo">F·R·I·E·N·D·S LOGS</div>', unsafe_allow_html=True)

col_input, col_view = st.columns([1, 1.4], gap="large")

with col_input:
    st.markdown("### 🎬 New Episode Details")
    
    with st.form("main_form", clear_on_submit=True):
        category = st.selectbox("Category (The Energy of...)", [
            "MONICA (Critical/Urgent)", 
            "CHANDLER (Sarcastic/Office)", 
            "ROSS (Specs/Technical)", 
            "JOEY (Trucks/Drivers)", 
            "PHOEBE (Random Stuff)"
        ])
        
        note_text = st.text_area("The One With...", value=st.session_state.edit_content, height=150)
        
        st.markdown('<div class="pivot-btn">', unsafe_allow_html=True)
        submitted = st.form_submit_button("PIVOT!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if submitted and note_text:
            new_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Note": note_text,
                "ID": str(uuid.uuid4()),
                "Category": category
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            st.session_state.edit_content = ""
            st.rerun()

    st.markdown("---")
    st.markdown("### 📅 Central Perk Master Plan")
    
    cal_events = []
    # Bezpieczne parsowanie danych do kalendarza
    for _, row in df.iterrows():
        n = str(row.get('Note', ''))
        d = str(row.get('Date', ''))
        if n and d:
            cal_events.append({
                "title": f"☕ {n[:20]}...",
                "start": d,
                "color": "#e74c3c" if "MONICA" in str(row.get('Category', '')).upper() else "#3498db"
            })

    calendar(events=cal_events, options={"initialView": "dayGridMonth"}, key="friends_calendar")

with col_view:
    st.markdown("### 📺 Previously on SQM Logistics...")
    
    # Filtrujemy tylko wiersze, które faktycznie coś mają
    valid_notes = df[df['Note'].astype(str).str.strip() != ""]
    
    if valid_notes.empty:
        st.info("No episodes recorded. Central Perk is empty.")
    else:
        # Najnowsze na górze
        sorted_notes = valid_notes.sort_values(by=['Date', 'Timestamp'], ascending=False)
        
        for idx, row in sorted_notes.iterrows():
            # Karta notatki
            st.markdown(f"""
            <div class="door-card">
                <div class="peephole"></div>
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 5px;">
                    <span style="color: #f1c40f; font-weight: bold; font-family: 'Varela Round';">{row['Category']}</span>
                    <span style="opacity: 0.7; font-size: 0.8rem;">{row['Date']} | {row['Timestamp']}</span>
                </div>
                <div class="note-content">"{row['Note']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Przyciski akcji
            btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])
            with btn_col1:
                if st.button("Rewind (Edytuj)", key=f"edit_{row['ID']}"):
                    st.session_state.edit_content = row['Note']
                    st.rerun()
            with btn_col2:
                # System usuwania przez stan sesji
                if st.button("Cancel (Usuń)", key=f"del_{row['ID']}"):
                    st.session_state.delete_id = row['ID']
                    st.rerun()
            with btn_col3:
                if st.button("Unagi!", key=f"unagi_{row['ID']}"):
                    st.toast("Total Awareness achieved.")

# --- STOPKA ---
st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>SQM Multimedia Solutions - Logistics Master System v4.0 (Friends Edition)</p>", unsafe_allow_html=True)
