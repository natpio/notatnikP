import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SQM: LOGISTIC PERK",
    page_icon="🛋️",
    layout="wide"
)

# --- THE ULTIMATE FRIENDS STYLE (CSS) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&display=swap');

    /* Globalne tło */
    .stApp {
        background-color: #6a5acd;
        background-image:
            linear-gradient(rgba(106, 90, 205, 0.85), rgba(106, 90, 205, 0.85)),
            url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* LOGO: LOGISTIC PERK W STYLU FRIENDS */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: white;
        text-shadow: 3px 3px 0px #000;
        margin-bottom: 0px;
    }
    .dot-red { color: #e74c3c; }
    .dot-blue { color: #3498db; }
    .dot-yellow { color: #f1c40f; }

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

    /* Tablica kredowa (Notatka) */
    .chalkboard-card {
        background-color: #1a1a1a;
        border: 10px solid #5d4037;
        border-radius: 5px;
        padding: 25px;
        margin-bottom: 25px;
        box-shadow: 12px 12px 0px rgba(0,0,0,0.5);
    }

    .unagi-gold-frame {
        border-color: #f1c40f !important;
        box-shadow: 0 0 25px #f1c40f !important;
        background-image: radial-gradient(circle, #2e7d32, #1a1a1a) !important;
    }

    .note-header {
        color: #f1c40f;
        font-family: 'Permanent Marker', cursive;
        border-bottom: 1px dashed #444;
        margin-bottom: 12px;
        padding-bottom: 5px;
        font-size: 1.1rem;
    }

    .note-body {
        font-family: 'Kalam', cursive;
        font-size: 1.8rem;
        line-height: 1.3;
        padding: 10px 0;
    }

    /* PRZYCISKI: ŻÓŁTA RAMKA MONIKI */
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
        transform: translateY(-3px);
        box-shadow: 6px 6px 0px rgba(0,0,0,0.4) !important;
    }

    /* PIVOT BUTTON */
    .pivot-btn div.stButton > button {
        background: linear-gradient(45deg, #e74c3c, #f1c40f, #3498db) !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2.5rem !important;
        height: 90px !important;
        color: white !important;
        border: 5px solid white !important;
        text-shadow: 2px 2px 4px #000;
    }
    
    /* Input Style */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        border: 3px solid #f1c40f !important;
        font-family: 'Gloria Hallelujah', cursive !important;
        color: #333 !important;
        font-size: 1.2rem !important;
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
    except:
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
    st.toast("UNAGI! TOTAL AWARENESS ACHIEVED!")
    st.snow()
    st.rerun()

# --- INTERFEJS ---

# LOGO W STYLU FRIENDS
st.markdown("""
    <div class="friends-logo">
        L O G I S T I C<span class="dot-red">.</span>P E R K
    </div>
""", unsafe_allow_html=True)

# KANAPA
st.markdown("""
<div class="sofa-box">
    <img src="https://images.ctfassets.net/4cd45et68cgf/4p9vF4p8y4mY6YQ6mY2w6e/6b8e8b5e5e6e8e8e8e8e8e8e8e8e8e8e/Friends_Sofa.png?w=450" class="sofa-img">
    <p style="font-family: 'Varela Round'; letter-spacing: 8px; color: #f1c40f; font-weight: bold; margin-top: 10px;">SQM MULTIMEDIA SOLUTIONS</p>
</div>
""", unsafe_allow_html=True)

# ZAMIANA STRON: LEWA (TIMELINE), PRAWA (FORMULARZ I KALENDARZ)
col_timeline, col_tools = st.columns([1.4, 1], gap="large")

with col_timeline:
    st.markdown("### 🎬 Logistics Timeline")
    logs = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if logs.empty:
        st.info("No logs found. Add your first slot on the right!")
    else:
        for _, row in logs.iterrows():
            is_unagi = str(row.get('Status')) == "UNAGI"
            card_style = "unagi-gold-frame" if is_unagi else ""
            
            st.markdown(f"""
                <div class="chalkboard-card {card_style}">
                    <div class="note-header">☕ {row['Date']} @ {row['Timestamp']}</div>
                    <div class="note-body">"{row['Note']}"</div>
                    { '<div style="color: #f1c40f; font-weight: bold; margin-top: 10px; font-family: Permanent Marker;">✨ STATUS: UNAGI ✨</div>' if is_unagi else '' }
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
                if st.button("👉 UNAGI!", key=f"un_{row['ID']}"):
                    st.session_state.unagi_target = row['ID']
                    st.rerun()

with col_tools:
    st.markdown("### 🖋️ The One with the New Slot")
    with st.form("entry_form", clear_on_submit=True):
        note = st.text_area("Slot Details:", value=st.session_state.edit_val, height=180, placeholder="What's happening in Düsseldorf?")
        
        st.markdown('<div class="pivot-btn">', unsafe_allow_html=True)
        if st.form_submit_button("PIVOT!"):
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
    st.markdown("### ☕ Scheduling Table")
    calendar_events = []
    for _, r in df.iterrows():
        if r['Note'] and r['Date']:
            calendar_events.append({
                "title": f"☕ {str(r['Note'])[:15]}...",
                "start": str(r['Date']),
                "color": "#2e7d32" if r['Status'] != "UNAGI" else "#f1c40f"
            })
    
    calendar(events=calendar_events, options={"initialView": "dayGridMonth"}, key="cal_v7")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.6;'>Logistic Perk Hub v7.0 | SQM Multimedia Solutions | 2026</p>", unsafe_allow_html=True)
