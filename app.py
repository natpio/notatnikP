import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
import random
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(
    page_title="SQM: The One with the Orange Sofa", 
    page_icon="🛋️", 
    layout="wide"
)

# --- DESIGN: CENTRAL PERK ULTIMATE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&display=swap');

    .stApp {
        background-color: #6a5acd;
        background-image: 
            linear-gradient(rgba(106, 90, 205, 0.8), rgba(106, 90, 205, 0.8)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* NAGŁÓWEK NEON */
    .neon-text {
        font-family: 'Permanent Marker', cursive;
        font-size: 4.5rem;
        text-align: center;
        color: #fff;
        text-shadow: 0 0 10px #fff, 0 0 20px #2e7d32, 0 0 30px #2e7d32;
        margin-bottom: 0px;
    }

    /* SŁYNNA POMARAŃCZOWA KANAPA */
    .sofa-container {
        text-align: center;
        padding: 20px;
        margin-bottom: 20px;
    }
    .sofa-img {
        width: 300px;
        filter: drop-shadow(0px 10px 15px rgba(0,0,0,0.5));
        transition: transform 0.3s;
    }
    .sofa-img:hover {
        transform: scale(1.1) rotate(-2deg);
    }

    /* TABLICA KREDOWA */
    .chalkboard {
        background-color: #1a1a1a;
        border: 10px solid #5d4037;
        border-radius: 5px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.3);
        font-family: 'Kalam', cursive;
    }

    .unagi-active {
        border: 10px solid #f1c40f !important;
        background-color: #2e7d32 !important; /* Zielony = Odhaczone */
    }

    /* PRZYCISKI */
    .stButton > button {
        width: 100% !important;
        font-family: 'Permanent Marker', cursive !important;
        border-radius: 0px !important;
    }

    .pivot-btn button {
        background-color: #e74c3c !important;
        font-size: 2rem !important;
        height: 80px !important;
        border: 4px solid white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ŁADOWANIE DANYCH ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl=0)
        required = ["Timestamp", "Date", "Note", "ID", "Category", "Status"]
        for col in required:
            if col not in data.columns: data[col] = ""
        return data.fillna("")
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category", "Status"])

# --- SESJA ---
if 'edit_content' not in st.session_state: st.session_state.edit_content = ""
if 'delete_id' not in st.session_state: st.session_state.delete_id = ""
if 'unagi_id' not in st.session_state: st.session_state.unagi_id = ""

df = load_data()

# --- LOGIKA PRZYCISKÓW (TOP) ---
# Usuwanie
if st.session_state.delete_id:
    df = df[df['ID'].astype(str) != str(st.session_state.delete_id)]
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.delete_id = ""
    st.rerun()

# Unagi (Zmiana statusu na "Odhaczone")
if st.session_state.unagi_id:
    df.loc[df['ID'].astype(str) == str(st.session_state.unagi_id), 'Status'] = "UNAGI"
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.unagi_id = ""
    st.toast("TOTAL AWARENESS ACHIEVED!")
    st.snow()
    st.rerun()

# --- UI ---
st.markdown('<div class="neon-text">Central Perk</div>', unsafe_allow_html=True)

# WSTAWKA Z KANAPĄ
st.markdown("""
<div class="sofa-container">
    <img src="https://images.ctfassets.net/4cd45et68cgf/4p9vF4p8y4mY6YQ6mY2w6e/6b8e8b5e5e6e8e8e8e8e8e8e8e8e8e8e/Friends_Sofa.png?w=400" class="sofa-img">
    <p style="font-family: 'Varela Round'; letter-spacing: 5px; color: #f1c40f; margin-top: 10px;">S·Q·M L·O·G·I·S·T·I·C·S</p>
</div>
""", unsafe_allow_html=True)



col_form, col_display = st.columns([1, 1.3], gap="large")

with col_form:
    st.markdown("### ✍️ Register New Slot")
    with st.form("main_form", clear_on_submit=True):
        cat = st.selectbox("Assign Energy:", ["MONICA: Urgent", "CHANDLER: Routine", "ROSS: Technical", "JOEY: Transport", "PHOEBE: Random"])
        note = st.text_area("Details:", value=st.session_state.edit_content, height=120)
        
        st.markdown('<div class="pivot-btn">', unsafe_allow_html=True)
        if st.form_submit_button("PIVOT!"):
            if note:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Note": note,
                    "ID": str(uuid.uuid4()),
                    "Category": cat,
                    "Status": "Active"
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.cache_data.clear()
                st.rerun()
    
    st.markdown("---")
    # Kalendarz
    cal_events = []
    for _, r in df.iterrows():
        if r['Note'] and r['Date']:
            cal_events.append({"title": f"☕ {str(r['Note'])[:15]}", "start": str(r['Date']), "color": "#2e7d32"})
    calendar(events=cal_events, options={"initialView": "dayGridMonth"}, key="cal_v10")

with col_display:
    st.markdown("### 🎬 Logistics Timeline")
    
    logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    for _, row in logs.iterrows():
        # Jeśli status to UNAGI, dodajemy specjalną klasę CSS (żółta ramka)
        is_unagi = "unagi-active" if row['Status'] == "UNAGI" else ""
        icon = "🦖" if "ROSS" in str(row['Category']) else "☕"
        
        st.markdown(f"""
        <div class="chalkboard {is_unagi}">
            <div style="color: #f1c40f; font-family: 'Permanent Marker'; font-size: 0.9rem; margin-bottom: 10px;">
                {icon} {row['Category']} | {row['Date']} {row['Timestamp']}
            </div>
            <div style="font-size: 1.4rem;">"{row['Note']}"</div>
            { '<p style="color: #f1c40f; font-weight: bold; margin-top: 10px;">✨ UNAGI STATUS: TOTAL AWARENESS ✨</p>' if is_unagi else '' }
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Rewind", key=f"e_{row['ID']}"):
                st.session_state.edit_content = row['Note']
                st.rerun()
        with c2:
            if st.button("Delete", key=f"d_{row['ID']}"):
                st.session_state.delete_id = row['ID']
                st.rerun()
        with c3:
            # PRZYCISK UNAGI TERAZ DZIAŁA!
            if st.button("👉 UNAGI", key=f"u_{row['ID']}"):
                st.session_state.unagi_id = row['ID']
                st.rerun()

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>The One with SQM Multimedia Solutions & Logistics - 2026</p>", unsafe_allow_html=True)
