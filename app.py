import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SQM LOGISTICS: THE ORANGE SOFA EDITION", 
    page_icon="🛋️", 
    layout="wide"
)

# --- THE ULTIMATE FRIENDS STYLE (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&display=swap');

    /* Tło mieszkania Moniki i cegły Central Perk */
    .stApp {
        background-color: #6a5acd;
        background-image: 
            linear-gradient(rgba(106, 90, 205, 0.85), rgba(106, 90, 205, 0.85)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* Neon Central Perk */
    .neon-header {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #fff, 0 0 20px #2e7d32, 0 0 40px #2e7d32;
        margin-bottom: 0px;
    }

    /* Kontener Kanapy */
    .sofa-box {
        text-align: center;
        margin-top: -20px;
        margin-bottom: 30px;
    }
    .sofa-img {
        width: 350px;
        filter: drop-shadow(0px 15px 20px rgba(0,0,0,0.6));
        transition: transform 0.3s ease;
    }
    .sofa-img:hover {
        transform: scale(1.05) rotate(-2deg);
    }

    /* Tablica kredowa (Notatka) */
    .chalkboard-card {
        background-color: #1a1a1a;
        border: 10px solid #5d4037; /* Drewniana rama */
        border-radius: 5px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 12px 12px 0px rgba(0,0,0,0.5);
        position: relative;
    }

    /* Specjalny styl dla UNAGI (Total Awareness) */
    .unagi-gold-frame {
        border-color: #f1c40f !important;
        box-shadow: 0 0 20px #f1c40f !important;
        background-image: radial-gradient(circle, #2e7d32, #1a1a1a);
    }

    .note-header {
        color: #f1c40f;
        font-family: 'Permanent Marker', cursive;
        font-size: 1rem;
        border-bottom: 1px dashed #444;
        margin-bottom: 12px;
        padding-bottom: 5px;
    }

    .note-body {
        font-family: 'Kalam', cursive;
        font-size: 1.6rem;
        color: #fff;
        line-height: 1.3;
    }

    /* Wielki przycisk PIVOT */
    .pivot-btn button {
        background: linear-gradient(45deg, #e74c3c, #f1c40f, #3498db) !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2.2rem !important;
        height: 90px !important;
        width: 100% !important;
        border: 4px solid white !important;
        color: white !important;
        text-shadow: 2px 2px #000;
        margin-top: 10px;
    }

    /* Inputy w stylu Central Perk */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        border: 3px solid #f1c40f !important;
        font-family: 'Gloria Hallelujah', cursive !important;
        color: #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        data = conn.read(ttl=0)
        # Upewnienie się, że wszystkie kolumny istnieją
        required = ["Timestamp", "Date", "Note", "ID", "Category", "Status"]
        for col in required:
            if col not in data.columns:
                data[col] = ""
        return data.fillna("") # Kluczowe zabezpieczenie przed TypeError
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category", "Status"])

# --- ZARZĄDZANIE STANEM SESJI ---
if 'edit_val' not in st.session_state: st.session_state.edit_val = ""
if 'del_target' not in st.session_state: st.session_state.del_target = ""
if 'unagi_target' not in st.session_state: st.session_state.unagi_target = ""

df = fetch_data()

# --- LOGIKA OPERACJI (TOP-LEVEL) ---
# 1. Usuwanie
if st.session_state.del_target:
    df = df[df['ID'].astype(str) != str(st.session_state.del_target)]
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.del_target = ""
    st.rerun()

# 2. Aktywacja UNAGI
if st.session_state.unagi_target:
    df.loc[df['ID'].astype(str) == str(st.session_state.unagi_target), 'Status'] = "UNAGI"
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.unagi_target = ""
    st.toast("UNAGI! Total state of awareness!")
    st.snow()
    st.rerun()

# --- INTERFEJS UŻYTKOWNIKA ---

# Header Neonowy
st.markdown('<div class="neon-header">Central Perk</div>', unsafe_allow_html=True)

# Słynna Kanapa
st.markdown("""
<div class="sofa-box">
    <img src="https://images.ctfassets.net/4cd45et68cgf/4p9vF4p8y4mY6YQ6mY2w6e/6b8e8b5e5e6e8e8e8e8e8e8e8e8e8e8e/Friends_Sofa.png?w=400" class="sofa-img">
    <p style="font-family: 'Varela Round'; letter-spacing: 10px; color: #f1c40f; font-weight: bold; font-size: 1.2rem; margin-top: 10px;">S·Q·M L·O·G·I·S·T·I·C·S</p>
</div>
""", unsafe_allow_html=True)



col_left, col_right = st.columns([1, 1.4], gap="large")

with col_left:
    st.markdown("### 🖋️ Today's Script Entry")
    with st.form("perk_form", clear_on_submit=True):
        # Wybór postaci
        char_cat = st.selectbox("Who's energy is this?", [
            "MONICA (Urgent/Cleanup)", 
            "ROSS (Specs/Technical)", 
            "CHANDLER (Office/Routine)", 
            "JOEY (Trucks/Logistics)", 
            "PHOEBE (Random/Smelly Cat)"
        ])
        
        note_txt = st.text_area("The One With...", value=st.session_state.edit_val, height=180)
        
        st.markdown('<div class="pivot-btn">', unsafe_allow_html=True)
        pivot_clicked = st.form_submit_button("PIVOT! PIVOT!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if pivot_clicked and note_txt:
            new_entry = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Note": note_txt,
                "ID": str(uuid.uuid4()),
                "Category": char_cat,
                "Status": "Active"
            }])
            df = pd.concat([df, new_entry], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            st.session_state.edit_val = ""
            st.rerun()

    st.markdown("---")
    st.markdown("### ☕ Scheduling Table")
    
    # Kalendarz Central Perk
    cal_events = []
    for _, row in df.iterrows():
        if row['Note'] and row['Date']:
            cal_events.append({
                "title": f"☕ {str(row['Note'])[:15]}",
                "start": str(row['Date']),
                "color": "#2e7d32" if row['Status'] != "UNAGI" else "#f1c40f"
            })
    calendar(events=cal_events, options={"initialView": "dayGridMonth"}, key="central_cal_v3")

with col_right:
    st.markdown("### 🎬 Season Timeline (Notes)")
    
    # Filtrujemy puste rekordy
    valid_logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if valid_logs.empty:
        st.info("No episodes recorded yet. Is Gunther on break?")
    else:
        for _, row in valid_logs.iterrows():
            # Sprawdzenie statusu UNAGI dla stylu karty
            unagi_class = "unagi-gold-frame" if str(row.get('Status')) == "UNAGI" else ""
            
            # Ikony kategorii (Safe Get)
            cat_name = str(row.get('Category', '')).upper()
            icon = "☕"
            if "MONICA" in cat_name: icon = "🧹"
            elif "ROSS" in cat_name: icon = "🦖"
            elif "JOEY" in cat_name: icon = "🍕"
            elif "PHOEBE" in cat_name: icon = "🎸"
            
            st.markdown(f"""
            <div class="chalkboard-card {unagi_class}">
                <div class="note-header">
                    {icon} {row['Category']} | {row['Date']} @ {row['Timestamp']}
                </div>
                <div class="note-body">
                    "{row['Note']}"
                </div>
                { '<div style="color: #f1c40f; font-weight: bold; margin-top: 10px; font-size: 1.1rem;">✨ STATUS: UNAGI ✨</div>' if unagi_class else '' }
            </div>
            """, unsafe_allow_html=True)
            
            # Przyciski sterujące
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("Rewind (Edytuj)", key=f"ed_{row['ID']}"):
                    st.session_state.edit_val = row['Note']
                    st.rerun()
            with b2:
                if st.button("Cancel (Usuń)", key=f"de_{row['ID']}"):
                    st.session_state.del_target = row['ID']
                    st.rerun()
            with b3:
                # Przycisk UNAGI - Zmienia status notatki
                if st.button("👉 UNAGI!", key=f"un_{row['ID']}"):
                    st.session_state.unagi_target = row['ID']
                    st.rerun()

# --- STOPKA ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6; font-family: 'Varela Round'; font-size: 0.8rem;">
    S·Q·M Multimedia Solutions Logistics Center | Central Perk Studio v5.0 | 2026 <br>
    <i>"I'll be there for you (as long as the slot is confirmed)"</i>
</div>
""", unsafe_allow_html=True)
