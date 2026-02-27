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

# --- DESIGN: THE ULTIMATE CENTRAL PERK & MONICA'S APARTMENT EXPERIENCE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&family=Montserrat:wght@800&display=swap');

    /* Globalne tło - fiolet Moniki + tekstura cegieł z Central Perk */
    .stApp {
        background-color: #6a5acd;
        background-image: 
            linear-gradient(rgba(106, 90, 205, 0.9), rgba(106, 90, 205, 0.9)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* NEONOWY NAGŁÓWEK CENTRAL PERK */
    .central-perk-neon {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: #fff;
        text-shadow: 
            0 0 5px #fff,
            0 0 10px #fff,
            0 0 20px #2e7d32, /* Zielony neon kawiarni */
            0 0 40px #2e7d32;
        margin-bottom: 5px;
        letter-spacing: 5px;
    }

    .sub-header {
        font-family: 'Varela Round', sans-serif;
        text-align: center;
        font-size: 1.2rem;
        letter-spacing: 10px;
        color: #f1c40f;
        text-transform: uppercase;
        margin-bottom: 40px;
    }

    /* KARTA NOTATKI: TABLICA KREDOWA Z KAWIARNI */
    .chalkboard-note {
        background-color: #1a1a1a;
        border: 12px solid #5d4037; /* Drewniana rama */
        border-radius: 4px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 15px 15px 30px rgba(0,0,0,0.6);
        position: relative;
        font-family: 'Kalam', cursive;
    }

    .chalkboard-note::before {
        content: '☕';
        position: absolute;
        top: 10px;
        right: 15px;
        font-size: 2rem;
        opacity: 0.3;
    }

    .note-meta {
        color: #f1c40f;
        font-family: 'Permanent Marker', cursive;
        font-size: 1rem;
        border-bottom: 1px dashed #555;
        margin-bottom: 15px;
        padding-bottom: 5px;
    }

    .note-body {
        font-size: 1.6rem;
        color: #fdfdfd;
        line-height: 1.3;
    }

    /* PANEL BOCZNY I INPUTY */
    [data-testid="stSidebar"] {
        background-color: #2e7d32; /* Zielony Central Perk */
    }

    .stTextArea textarea {
        background-color: #fdf5e6 !important; /* Kolor papieru */
        border: 4px solid #f1c40f !important;
        font-family: 'Gloria Hallelujah', cursive !important;
        font-size: 1.2rem !important;
    }

    /* PRZYCISK PIVOT - ANIMOWANY */
    .stButton > button {
        width: 100% !important;
        height: 70px !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2rem !important;
        background-color: #e74c3c !important; /* Czerwień Rossa */
        color: white !important;
        border: 4px solid white !important;
        box-shadow: 5px 5px 0px #c0392b;
        transition: 0.2s;
    }

    .stButton > button:hover {
        transform: translate(-2px, -2px);
        box-shadow: 8px 8px 0px #c0392b;
        background-color: #ff4d4d !important;
    }

    /* STYLIZACJA KALENDARZA */
    .fc { background: #fff176 !important; border: 5px solid #5d4037 !important; border-radius: 15px; }
    .fc-header-toolbar { padding: 10px; }
    .fc-daygrid-day-number { color: #333 !important; font-weight: bold; }

    /* CUSTOMOWY SCROLLBAR */
    ::-webkit-scrollbar { width: 12px; }
    ::-webkit-scrollbar-track { background: #6a5acd; }
    ::-webkit-scrollbar-thumb { background: #f1c40f; border-radius: 10px; border: 3px solid #6a5acd; }
</style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA DANYCH ---
if 'edit_content' not in st.session_state: st.session_state.edit_content = ""
if 'delete_id' not in st.session_state: st.session_state.delete_id = ""

conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        data = conn.read(ttl=0)
        for col in ["Timestamp", "Date", "Note", "ID", "Category"]:
            if col not in data.columns: data[col] = ""
        return data
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category"])

df = fetch_data()

# --- LOGIKA USUWANIA (TOP LEVEL) ---
if st.session_state.delete_id:
    df = df[df['ID'].astype(str) != str(st.session_state.delete_id)]
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.delete_id = ""
    st.toast("WE WERE ON A BREAK! (Entry removed)")
    st.rerun()

# --- HEADER ---
st.markdown('<div class="central-perk-neon">Central Perk</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">S·Q·M L·O·G·I·S·T·I·C·S</div>', unsafe_allow_html=True)

# --- LAYOUT ---
col_left, col_right = st.columns([1, 1.4], gap="large")

with col_left:
    st.markdown("### 🖋️ New Script Entry")
    
    with st.form("script_form"):
        # Wybór postaci = Styl logistyki
        char = st.selectbox("Which character's energy is this?", [
            "MONICA: The Organizer (Urgent)",
            "CHANDLER: Sarcastic Admin (Routine)",
            "ROSS: The Paleontologist (Specs/Technical)",
            "JOEY: The Actor (Trucks/Deliveries)",
            "PHOEBE: The Musician (Random/Creative)"
        ])
        
        note = st.text_area("Description of the situation:", 
                            value=st.session_state.edit_content,
                            placeholder="The One Where the 24t Truck disappears...",
                            height=150)
        
        # PIVOT BUTTON
        if st.form_submit_button("PIVOT! PIVOT!"):
            if note:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Note": note,
                    "ID": str(uuid.uuid4()),
                    "Category": char
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.cache_data.clear()
                st.session_state.edit_content = ""
                st.balloons()
                st.rerun()

    st.markdown("---")
    st.markdown("### 🛋️ The Orange Sofa Calendar")
    
    cal_data = []
    for _, r in df.iterrows():
        if r['Note'] and r['Date']:
            color = "#2e7d32" # Central Perk Green
            if "MONICA" in str(r['Category']): color = "#e74c3c"
            if "ROSS" in str(r['Category']): color = "#3498db"
            
            cal_data.append({
                "title": f"☕ {str(r['Note'])[:15]}",
                "start": str(r['Date']),
                "color": color
            })
    
    calendar(events=cal_data, options={"initialView": "dayGridMonth"}, key="pro_cal")

with col_right:
    st.markdown("### 🎬 Season Highlights (Logs)")
    
    # Filtrowanie i sortowanie
    valid_logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if valid_logs.empty:
        st.warning("The script is empty. Where is Gunther?")
    else:
        for _, row in valid_logs.iterrows():
            # Ikonki dla kategorii
            icon = "☕"
            if "MONICA" in row['Category']: icon = "🧹"
            if "JOEY" in row['Category']: icon = "🍕"
            if "CHANDLER" in row['Category']: icon = "💻"
            
            st.markdown(f"""
            <div class="chalkboard-note">
                <div class="note-meta">
                    {icon} {row['Category']} | SEASON {row['Date'][:4]} | EP: {row['Timestamp']}
                </div>
                <div class="note-body">
                    "{row['Note']}"
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Przyciski
            c1, c2, c3 = st.columns([1, 1, 1])
            with c1:
                if st.button("Rewind (Edit)", key=f"e_{row['ID']}"):
                    st.session_state.edit_content = row['Note']
                    st.rerun()
            with c2:
                if st.button("Cancel Show (Del)", key=f"d_{row['ID']}"):
                    st.session_state.delete_id = row['ID']
                    st.rerun()
            with c3:
                if st.button("UNAGI!", key=f"u_{row['ID']}"):
                    st.snow()
                    st.toast("Total state of awareness!")

# --- STOPKA ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6; font-family: 'Varela Round';">
    SQM Multimedia Solutions & Friends - All Rights Reserved 2026 <br>
    <i>"I'll be there for you (when the truck arrives)"</i>
</div>
""", unsafe_allow_html=True)
