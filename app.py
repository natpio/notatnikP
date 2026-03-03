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

# --- THE ULTIMATE FRIENDS STYLE (CSS) V2.0 ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&family=Indie+Flower&display=swap');

    /* Globalne tło i tekstury */
    .stApp {
        background-color: #6a5acd; /* Fiolet Moniki */
        background-image: 
            linear-gradient(rgba(106, 90, 205, 0.8), rgba(106, 90, 205, 0.8)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* Stylizacja Scrollbara */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #483d8b; }
    ::-webkit-scrollbar-thumb { background: #f1c40f; border-radius: 5px; }

    /* LOGO: LOGISTIC PERK */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5.5rem;
        text-align: center;
        color: white;
        text-shadow: 4px 4px 0px #000;
        margin-bottom: -10px;
        letter-spacing: 5px;
    }
    .dot-red { color: #e74c3c; text-shadow: 0 0 15px #e74c3c; }
    .dot-blue { color: #3498db; text-shadow: 0 0 15px #3498db; }
    .dot-yellow { color: #f1c40f; text-shadow: 0 0 15px #f1c40f; }

    /* Sofa i Podpis SQM */
    .sofa-box { text-align: center; margin-bottom: 40px; }
    .sofa-img { width: 350px; filter: drop-shadow(0px 15px 15px rgba(0,0,0,0.5)); }

    /* KARTY ZADAŃ: Styl Tablicy Magnadoodle / Chalkboard */
    .chalkboard-card {
        background-color: #222;
        border: 10px solid #f1c40f; /* Żółta ramka wizjera */
        border-image: none;
        border-radius: 20px 5px 20px 5px;
        padding: 30px;
        margin-bottom: 30px;
        box-shadow: 15px 15px 0px rgba(0,0,0,0.4);
        position: relative;
        transition: transform 0.3s ease;
    }
    .chalkboard-card:hover {
        transform: scale(1.02);
    }

    /* Prawdziwy font "odręczny" dla notatek */
    .note-body {
        font-family: 'Indie Flower', cursive;
        font-size: 2.1rem;
        line-height: 1.2;
        color: #f0f0f0;
        margin-top: 15px;
    }

    .note-header {
        font-family: 'Varela Round', sans-serif;
        text-transform: uppercase;
        font-size: 0.9rem;
        color: #f1c40f;
        letter-spacing: 2px;
        border-bottom: 2px solid #444;
    }

    /* Status UNAGI - Neonowy Zielony */
    .unagi-card {
        border-color: #2ecc71 !important;
        background-color: #1a3c26 !important;
        box-shadow: 0 0 30px rgba(46, 204, 113, 0.4) !important;
    }

    /* PRZYCISKI */
    div.stButton > button {
        border-radius: 0px !important;
        border: 3px solid black !important;
        font-family: 'Permanent Marker', cursive !important;
        background-color: #f1c40f !important;
        color: black !important;
        box-shadow: 5px 5px 0px black !important;
        transition: 0.1s !important;
    }
    div.stButton > button:active {
        box-shadow: 1px 1px 0px black !important;
        transform: translate(4px, 4px);
    }

    /* PRZYCISK PIVOT - Legenda */
    .pivot-container div.stButton > button {
        height: 100px !important;
        font-size: 3rem !important;
        background: #e74c3c !important;
        color: white !important;
        width: 100% !important;
    }
    .pivot-container div.stButton > button:hover {
        background: #c0392b !important;
        animation: shake 0.5s infinite;
    }

    @keyframes shake {
        0% { transform: rotate(0deg); }
        25% { transform: rotate(1deg); }
        75% { transform: rotate(-1deg); }
        100% { transform: rotate(0deg); }
    }

    /* Styl dla inputów */
    .stTextArea textarea {
        background-color: #eee !important;
        border-radius: 10px !important;
        font-family: 'Indie Flower', cursive !important;
        font-size: 1.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- DANE I POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        data = conn.read(ttl=0)
        required = ["Timestamp", "Date", "Note", "ID", "Status"]
        for col in required:
            if col not in data.columns: data[col] = ""
        return data.fillna("")
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Status"])

# Session State
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
    st.toast("UNAGI! State of total awareness! 🍣")
    st.snow()
    st.rerun()

# --- UI INTERFEJS ---

# Nagłówek w stylu czołówki
st.markdown("""
<div class="friends-logo">
    L<span class="dot-red">.</span>O<span class="dot-blue">.</span>G<span class="dot-yellow">.</span>I<span class="dot-red">.</span>S<span class="dot-blue">.</span>T<span class="dot-yellow">.</span>I<span class="dot-red">.</span>C
    <br>
    P<span class="dot-blue">.</span>E<span class="dot-yellow">.</span>R<span class="dot-red">.</span>K
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sofa-box">
    <img src="https://images.ctfassets.net/4cd45et68cgf/4p9vF4p8y4mY6YQ6mY2w6e/6b8e8b5e5e6e8e8e8e8e8e8e8e8e8e8e/Friends_Sofa.png?w=400" class="sofa-img">
    <p style="font-family: 'Varela Round'; letter-spacing: 5px; color: #f1c40f; font-weight: bold; margin-top: 10px;">SQM LOGISTICS & TRANSPORT DEPT.</p>
</div>
""", unsafe_allow_html=True)

left_col, right_col = st.columns([1.4, 1], gap="large")

with left_col:
    st.markdown("### 🎬 Active Scripts (Live Tasks)")
    
    # Filtrowanie i sortowanie
    active_logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    for _, row in active_logs.iterrows():
        is_unagi = str(row.get('Status')) == "UNAGI"
        card_style = "unagi-card" if is_unagi else ""
        
        st.markdown(f"""
            <div class="chalkboard-card {card_style}">
                <div class="note-header">📍 SLOT: {row['Date']} | {row['Timestamp']}</div>
                <div class="note-body">{row['Note']}</div>
                { '<div style="color: #2ecc71; font-family: Permanent Marker; margin-top: 15px; font-size: 1.2rem;">🍣 STATUS: FULL UNAGI</div>' if is_unagi else '' }
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⏪ REWIND", key=f"ed_{row['ID']}"):
                st.session_state.edit_val = row['Note']
                st.rerun()
        with c2:
            if st.button("❌ CUT SCENE", key=f"de_{row['ID']}"):
                st.session_state.del_target = row['ID']
                st.rerun()
        with c3:
            if st.button("🍣 UNAGI", key=f"un_{row['ID']}"):
                st.session_state.unagi_target = row['ID']
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

with right_col:
    st.markdown("### 🖋️ Add New Scenario")
    with st.container(border=True):
        with st.form("entry_form"):
            note_input = st.text_area("Logistics Details (Trucks, Slots, Deadlines):", 
                                     value=st.session_state.edit_val, 
                                     placeholder="e.g., Urbanek Serbia - empty cases for disassembly...",
                                     height=150)
            
            st.markdown('<div class="pivot-container">', unsafe_allow_html=True)
            submitted = st.form_submit_button("PIVOT!")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if submitted:
                if note_input:
                    new_entry = pd.DataFrame([{
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Note": note_input,
                        "ID": str(uuid.uuid4()),
                        "Status": "Active"
                    }])
                    df = pd.concat([df, new_entry], ignore_index=True)
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.session_state.edit_val = ""
                    st.success("Scene added! Pivot, pivot, pivot!")
                    st.rerun()

    st.markdown("---")
    st.markdown("### 📅 Logistics Calendar")
    
    # Przygotowanie eventów do kalendarza
    cal_events = []
    for _, r in df.iterrows():
        if r['Note']:
            color = "#2ecc71" if r['Status'] == "UNAGI" else "#e74c3c"
            cal_events.append({
                "title": f"🚚 {str(r['Note'])[:20]}...",
                "start": str(r['Date']),
                "backgroundColor": color,
                "borderColor": color
            })
            
    calendar(events=cal_events, options={
        "initialView": "dayGridMonth",
        "headerToolbar": {"left": "prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"},
        "selectable": True,
    }, key="friends_calendar_v10")

st.markdown("""
    <hr style="border: 1px solid #f1c40f; opacity: 0.3;">
    <p style='text-align: center; font-family: Varela Round; opacity: 0.7;'>
        SQM MULTIMEDIA SOLUTIONS | Transport Logistics Dashboard v9.0 | 2026
    </p>
""", unsafe_allow_html=True)
