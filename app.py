import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
import random
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(
    page_title="SQM: Central Perk Logistics", 
    page_icon="☕", 
    layout="wide"
)

# --- DESIGN: THE ULTIMATE CENTRAL PERK EXPERIENCE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&display=swap');

    /* Tło - mieszkanie Moniki + cegły Central Perk */
    .stApp {
        background-color: #6a5acd;
        background-image: 
            linear-gradient(rgba(106, 90, 205, 0.85), rgba(106, 90, 205, 0.85)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* NEONOWY NAGŁÓWEK */
    .central-perk-neon {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 5px #fff, 0 0 10px #fff, 0 0 20px #2e7d32, 0 0 40px #2e7d32;
        margin-bottom: 0px;
    }

    .sub-header {
        font-family: 'Varela Round', sans-serif;
        text-align: center;
        font-size: 1rem;
        letter-spacing: 8px;
        color: #f1c40f;
        margin-bottom: 40px;
    }

    /* KARTA: TABLICA KREDOWA */
    .chalkboard-note {
        background-color: #1a1a1a;
        border: 10px solid #5d4037;
        border-radius: 5px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 12px 12px 0px rgba(0,0,0,0.4);
        position: relative;
    }

    .note-meta {
        color: #f1c40f;
        font-family: 'Permanent Marker', cursive;
        font-size: 0.9rem;
        border-bottom: 1px dashed #444;
        margin-bottom: 15px;
        padding-bottom: 5px;
    }

    .note-body {
        font-family: 'Kalam', cursive;
        font-size: 1.5rem;
        color: #fff;
        line-height: 1.3;
    }

    /* PRZYCISK PIVOT */
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2rem !important;
        background-color: #e74c3c !important;
        color: white !important;
        border: 3px solid white !important;
        transition: 0.2s;
    }

    .stButton > button:hover {
        transform: scale(1.02);
        background-color: #ff4d4d !important;
    }

    /* INPUTY */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        border: 3px solid #f1c40f !important;
        font-family: 'Gloria Hallelujah', cursive !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNKCJE DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl=0)
        # Naprawa struktury i usuwanie None (Fix dla TypeError)
        required_cols = ["Timestamp", "Date", "Note", "ID", "Category"]
        for col in required_cols:
            if col not in data.columns:
                data[col] = ""
        # Zamiana wszystkich wartości None na puste ciągi znaków
        data = data.fillna("")
        return data
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category"])

# --- ZARZĄDZANIE STANEM SESJI ---
if 'edit_content' not in st.session_state: st.session_state.edit_content = ""
if 'delete_id' not in st.session_state: st.session_state.delete_id = ""

df = load_data()

# --- LOGIKA USUWANIA (The One with the Break) ---
if st.session_state.delete_id:
    df = df[df['ID'].astype(str) != str(st.session_state.delete_id)]
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.delete_id = ""
    st.toast("WE WERE ON A BREAK! (Usunięto)")
    st.rerun()

# --- HEADER ---
st.markdown('<div class="central-perk-neon">Central Perk</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">S·Q·M L·O·G·I·S·T·I·C·S</div>', unsafe_allow_html=True)

col_input, col_logs = st.columns([1, 1.4], gap="large")

with col_input:
    st.markdown("### 🖋️ Today's Script")
    with st.form("main_form", clear_on_submit=True):
        cat = st.selectbox("Who is responsible?", [
            "MONICA (Urgent/Cleanup)", 
            "CHANDLER (Sarcastic/Office)", 
            "ROSS (Technical/The Geller Cup)", 
            "JOEY (Trucks/Deliveries)", 
            "PHOEBE (Random/Smelly Cat)"
        ])
        
        note = st.text_area("The One With...", value=st.session_state.edit_content, height=150)
        
        if st.form_submit_button("PIVOT! PIVOT!"):
            if note:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Note": note,
                    "ID": str(uuid.uuid4()),
                    "Category": cat
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.cache_data.clear()
                st.session_state.edit_content = ""
                st.rerun()

    st.markdown("---")
    # Kalendarz
    cal_events = []
    for _, r in df.iterrows():
        if r['Note'] and r['Date']:
            cal_events.append({
                "title": f"☕ {str(r['Note'])[:15]}",
                "start": str(r['Date']),
                "color": "#2e7d32"
            })
    calendar(events=cal_events, options={"initialView": "dayGridMonth"}, key="central_cal")

with col_logs:
    st.markdown("### 🎬 Season Highlights")
    
    # Filtrujemy tylko realne wpisy
    display_df = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if display_df.empty:
        st.info("No logs found. Gunther is waiting.")
    else:
        for _, row in display_df.iterrows():
            # BEZPIECZNE POBIERANIE KATEGORII (Fix dla TypeError)
            cat_val = str(row.get('Category', '')).upper()
            icon = "☕"
            if "MONICA" in cat_val: icon = "🧹"
            elif "JOEY" in cat_val: icon = "🍕"
            elif "CHANDLER" in cat_val: icon = "💻"
            elif "ROSS" in cat_val: icon = "🦖"
            
            st.markdown(f"""
            <div class="chalkboard-note">
                <div class="note-meta">
                    {icon} {row['Category']} | {row['Date']} {row['Timestamp']}
                </div>
                <div class="note-body">"{row['Note']}"</div>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Rewind (Edytuj)", key=f"e_{row['ID']}"):
                    st.session_state.edit_content = row['Note']
                    st.rerun()
            with c2:
                if st.button("Cancel (Usuń)", key=f"d_{row['ID']}"):
                    st.session_state.delete_id = row['ID']
                    st.rerun()
            with c3:
                if st.button("UNAGI!", key=f"u_{row['ID']}"):
                    st.toast("Total state of awareness!")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>SQM Logistics Edition 2026. I'll be there for you.</p>", unsafe_allow_html=True)
