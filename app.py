import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SQM: LOGISTIC PERK Hub",
    page_icon="🛋️",
    layout="wide"
)

# --- THE ULTIMATE FRIENDS STYLE (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&display=swap');

    /* Globalne tło i KURSOR */
    .stApp {
        background-color: #6a5acd;
        background-image:
            linear-gradient(rgba(106, 90, 205, 0.85), rgba(106, 90, 205, 0.85)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }
    
    /* Zmiana kursora na filiżankę kawy przy najechaniu na interaktywne elementy */
    a, button, input, select, textarea, .stButton>button {
        cursor: url('https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/2615.png'), auto !important;
    }

    /* LOGO: LOGISTIC PERK W STYLU FRIENDS z efektem migotania */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: white;
        text-shadow: 3px 3px 0px #000;
        margin-bottom: 0px;
        animation: flicker 4s infinite; /* Efekt migotania neonu */
    }
    .dot-red { color: #e74c3c; }
    
    @keyframes flicker {
        0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
            opacity: 1;
            text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #e74c3c, 0 0 70px #e74c3c;
        }
        20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
            opacity: 0.4;
            text-shadow: none;
        }
    }

    /* Kontener Kanapy */
    .sofa-box {
        text-align: center;
        margin-top: -10px;
        margin-bottom: 30px;
    }
    .sofa-img {
        width: 380px;
        filter: drop-shadow(0px 15px 20px rgba(0,0,0,0.6));
    }

    /* FIOLETOWE NOTATKI z GRUBĄ ŻÓŁTĄ RAMKĄ (Monica style) */
    .chalkboard-card {
        background-color: #6a5acd; /* Kolor fioletowy drzwi Moniki */
        border: 15px solid #f1c40f; /* Gruba żółta ozdobna rama */
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 15px 15px 0px rgba(0,0,0,0.5);
        position: relative;
    }

    /* Efekt wizjera z pary unoszącej się nad kawą */
    .chalkboard-card::before {
        content: '☕';
        position: absolute;
        top: -20px;
        right: 20px;
        font-size: 3rem;
        opacity: 0.8;
    }

    .unagi-gold-frame {
        border-color: #fff !important; /* Biała rama dla UNAGI */
        box-shadow: 0 0 25px #f1c40f !important;
        background-color: #2e7d32 !important; /* Zielony kolor Central Perk */
    }

    .note-header {
        color: #f1c40f;
        font-family: 'Permanent Marker', cursive;
        border-bottom: 2px dashed #f1c40f;
        margin-bottom: 12px;
        padding-bottom: 5px;
        font-size: 1.1rem;
    }

    .note-body {
        font-family: 'Gloria Hallelujah', cursive; /* Nowa czcionka odręczna markerem */
        font-size: 1.9rem;
        line-height: 1.3;
        padding: 10px 0;
        color: #fff;
    }

    /* PRZYCISKI: ŻÓŁTA RAMKA MONIKI z animacją pary */
    div.stButton > button {
        background-color: #fff !important;
        color: #333 !important;
        font-family: 'Varela Round', sans-serif !important;
        font-weight: bold !important;
        border: 5px solid #f1c40f !important;
        border-radius: 15px !important;
        box-shadow: 4px 4px 0px rgba(0,0,0,0.3) !important;
        transition: all 0.2s ease !important;
        height: 55px !important;
        width: 100% !important;
    }

    div.stButton > button:hover {
        background-color: #f1c40f !important;
        color: white !important;
        transform: translateY(-3px) scale(1.05);
        box-shadow: 6px 6px 0px rgba(0,0,0,0.4) !important;
    }

    /* PIVOT BUTTON - Shaking effect */
    .pivot-btn div.stButton > button {
        background: linear-gradient(45deg, #e74c3c, #f1c40f, #3498db) !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2.8rem !important;
        height: 100px !important;
        color: white !important;
        border: 6px solid white !important;
        text-shadow: 2px 2px 4px #000;
        margin-top: 15px;
        animation: pivot_shake 0.5s infinite;
        animation-play-state: paused;
    }
    
    .pivot-btn div.stButton > button:hover {
        animation-play-state: running;
    }
    
    @keyframes pivot_shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        50% { transform: translate(-1px, 2px) rotate(1deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }
    
    /* Input Style */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        border: 4px solid #f1c40f !important;
        border-radius: 15px !important;
        font-family: 'Gloria Hallelujah', cursive !important;
        color: #333 !important;
        font-size: 1.3rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE I DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        data = conn.read(ttl=0)
        required = ["Timestamp", "Date", "Note", "ID", "Status"]
        for col in required:
            if col not in data.columns: data[col] = ""
        return data.fillna("")
    except Exception as e:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Status"])

if 'edit_val' not in st.session_state: st.session_state.edit_val = ""
if 'del_target' not in st.session_state: st.session_state.del_target = ""
if 'unagi_target' not in st.session_state: st.session_state.unagi_target = ""

df = fetch_data()

# --- LOGIKA OPERACJI ---
if st.session_state.del_target:
    df = df[df['ID'].astype(str) != str(st.session_state.del_target)]
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.del_target = ""
    st.rerun()

if st.session_state.unagi_target:
    df.loc[df['ID'].astype(str) == str(st.session_state.unagi_target), 'Status'] = "UNAGI"
    conn.update(data=df)
    st.cache_data.clear()
    st.session_state.unagi_target = ""
    st.toast("UNAGI! TOTAL AWARENESS ACHIEVED! 🍣")
    st.snow()
    st.rerun()

# --- INTERFEJS ---

# NOWE LOGO W STYLU FRIENDS (migoczący neon)
st.markdown("""
    <div class="friends-logo">
        L O G I S T I C<span class="dot-red">.</span>P E R K
    </div>
""", unsafe_allow_html=True)

# KANAPA
st.markdown("""
<div class="sofa-box">
    <img src="https://images.ctfassets.net/4cd45et68cgf/4p9vF4p8y4mY6YQ6mY2w6e/6b8e8b5e5e6e8e8e8e8e8e8e8e8e8e8e/Friends_Sofa.png?w=450" class="sofa-img">
    <p style="font-family: 'Varela Round'; letter-spacing: 10px; color: #f1c40f; font-weight: bold; margin-top: 10px; font-size: 1.3rem;">SQM MULTIMEDIA SOLUTIONS</p>
</div>
""", unsafe_allow_html=True)

# ZAMIANA STRON: LEWA (TIMELINE), PRAWA (FORMULARZ I KALENDARZ)
col_timeline, col_tools = st.columns([1.5, 1], gap="large")

with col_timeline:
    st.markdown("### 🎬 Logistics Timeline")
    logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if logs.empty:
        st.info("No logs found. Add your first slot on the right! ☕")
    else:
        for _, row in logs.iterrows():
            is_unagi = str(row.get('Status')) == "UNAGI"
            card_style = "unagi-gold-frame" if is_unagi else ""
            
            st.markdown(f"""
                <div class="chalkboard-card {card_style}">
                    <div class="note-header">📅 {row['Date']} | ⏰ {row['Timestamp']}</div>
                    <div class="note-body">"{row['Note']}"</div>
                    { '<div style="color: #f1c40f; font-weight: bold; margin-top: 15px; font-family: Permanent Marker; font-size: 1.2rem; text-align: center;">✨ STATUS: UNAGI ✨ (Total Awareness)</div>' if is_unagi else '' }
                </div>
            """, unsafe_allow_html=True)
            
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("⏪ Rewind", key=f"ed_{row['ID']}"):
                    st.session_state.edit_val = row['Note']
                    st.rerun()
            with b2:
                if st.button("❌ Cancel", key=f"de_{row['ID']}"):
                    st.session_state.del_target = row['ID']
                    st.rerun()
            with b3:
                # Przycisk UNAGI
                if st.button("🍣 UNAGI!", key=f"un_{row['ID']}"):
                    st.session_state.unagi_target = row['ID']
                    st.rerun()

with col_tools:
    st.markdown("### 🖋️ The One with the New Script")
    with st.form("entry_form", clear_on_submit=True):
        note = st.text_area("Script Details:", value=st.session_state.edit_val, height=220, placeholder="The One Where Düsseldorf gets ready...")
        
        st.markdown('<div class="pivot-btn">', unsafe_allow_html=True)
        if st.form_submit_button("PIVOT! PIVOT!"):
            if note:
                new_row = pd.DataFrame([{
                    "Timestamp": datetime.now().strftime("%H:%M:%S"),
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Note": note,
                    "ID": str(uuid.uuid4()),
                    "Status": "Active"
                }])
                df = pd.concat([df, new_row], ignore_index=True)
                conn.update(data=df)
                st.cache_data.clear()
                st.session_state.edit_val = ""
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📅 Scheduling Board")
    calendar_events = []
    for _, r in df.iterrows():
        if r['Note'] and r['Date']:
            calendar_events.append({
                "title": f"☕ {str(r['Note'])[:15]}...",
                "start": str(r['Date']),
                "color": "#2e7d32" if r['Status'] != "UNAGI" else "#f1c40f"
            })
    
    calendar(events=calendar_events, options={"initialView": "dayGridMonth", "firstDay": 1}, key="cal_v8")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.7; font-family: Varela Round; font-size: 0.9rem;'>Logistic Perk Hub v8.0 | SQM Multimedia Solutions | 2026<br>\"I'll be there for you (when the truck arrives)\"</p>", unsafe_allow_html=True)
