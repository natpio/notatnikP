import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA STRONY ---
st.set_page_config(
    page_title="SQM: LOGISTIC PERK Hub",
    page_icon="☕",
    layout="wide"
)

# --- THE ULTIMATE FRIENDS STYLE (CSS) V10.0 - NEON & CURSOR ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Indie+Flower&display=swap');

    /* Tło: Fioletowe cegły góra (Mieszkanie Moniki), Brązowe dół (Central Perk) */
    .stApp {
        background-image: 
            url("https://www.transparenttextures.com/patterns/brick-wall.png"),
            linear-gradient(to bottom, 
                #6a5acd 0%, #6a5acd 50%, 
                #8b4513 50%, #8b4513 100%
            );
        background-attachment: fixed;
        background-size: auto, 100% 100%;
        color: white;
    }

    /* Stylizacja Scrollbara */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #483d8b; }
    ::-webkit-scrollbar-thumb { background: #f1c40f; border-radius: 5px; }

    /* LOGO: LOGISTIC PERK */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        text-shadow: 4px 4px 0px #000;
        line-height: 1.1;
        margin-bottom: 10px;
        transition: all 0.3s ease;
    }
    .dot-red { color: #e74c3c; } .dot-blue { color: #3498db; } .dot-yellow { color: #f1c40f; }

    /* EFEKT NEONU (Mruganie) */
    .neon-flicker {
        animation: flicker 2s infinite;
    }

    @keyframes flicker {
        0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100% {
            opacity: 1;
            text-shadow: 0 0 10px #fff, 0 0 20px #fff, 0 0 30px #fff, 0 0 40px #e74c3c, 0 0 70px #e74c3c, 4px 4px 0px #000;
        }
        20%, 21.999%, 63%, 63.999%, 65%, 69.999% {
            opacity: 0.4;
            text-shadow: 4px 4px 0px #000;
        }
    }

    /* KARTY ZADAŃ */
    .chalkboard-card {
        background-color: rgba(34, 34, 34, 0.9);
        border: 8px solid #f1c40f; 
        border-radius: 15px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.4);
    }

    .note-body {
        font-family: 'Indie Flower', cursive;
        font-size: 2rem;
        line-height: 1.2;
        color: #f0f0f0;
    }

    .unagi-card {
        border-color: #2ecc71 !important;
        background-color: rgba(26, 60, 38, 0.9) !important;
        box-shadow: 0 0 20px rgba(46, 204, 113, 0.3) !important;
    }

    /* KURSOR FILIŻANKA - Zmienia się po najechaniu na pole tekstowe */
    .stTextArea textarea {
        background-color: #fdf5e6 !important;
        font-family: 'Indie Flower', cursive !important;
        font-size: 1.5rem !important;
        color: #333 !important;
        border: 3px solid #f1c40f !important;
        cursor: url('https://img.icons8.com/color/32/central-perk.png'), auto !important;
    }

    /* PRZYCISKI */
    div.stButton > button {
        font-family: 'Permanent Marker', cursive !important;
        background-color: #f1c40f !important;
        color: black !important;
        width: 100%;
        border: 3px solid black !important;
        box-shadow: 4px 4px 0px black !important;
    }
    
    div.stButton > button:active {
        box-shadow: 1px 1px 0px black !important;
        transform: translate(3px, 3px);
    }

    /* PIVOT BUTTON */
    .pivot-container div.stButton > button {
        height: 80px !important;
        font-size: 2.5rem !important;
        background: #e74c3c !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE I DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    try:
        data = conn.read(ttl=0)
        # Gwarancja kolumn w Twoim układzie z arkusza
        cols = ["Date", "Note", "ID", "Timestamp", "Category", "Status"]
        for col in cols:
            if col not in data.columns:
                data[col] = "Active" if col == "Status" else ""
        return data[cols].fillna("")
    except Exception:
        return pd.DataFrame(columns=["Date", "Note", "ID", "Timestamp", "Category", "Status"])

def safe_update(data_to_save):
    """Pancerny bezpiecznik SQM - blokuje zapis jeśli dane są puste"""
    if not data_to_save.empty:
        try:
            conn.update(data=data_to_save)
            st.cache_data.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Błąd zapisu: {e}")
    else:
        st.warning("PIVOT! Zapis zablokowany - arkusz nie może być pusty.")

# Inicjalizacja
df = fetch_data()
if 'edit_val' not in st.session_state: st.session_state.edit_val = ""

# --- LOGIKA OPERACJI ---

# Usuwanie
if 'del_target' in st.session_state and st.session_state.del_target:
    target_id = str(st.session_state.del_target)
    df = df[df['ID'].astype(str) != target_id]
    st.session_state.del_target = None
    safe_update(df)

# Status UNAGI
if 'unagi_target' in st.session_state and st.session_state.unagi_target:
    target_id = str(st.session_state.unagi_target)
    mask = df['ID'].astype(str) == target_id
    if mask.any():
        df.loc[mask, 'Status'] = "UNAGI"
        st.snow()
        st.toast("UNAGI! Total awareness achieved! 🍣")
    st.session_state.unagi_target = None
    safe_update(df)

# --- UI INTERFEJS ---

# Pstryczek do neonu (Widget na górze)
col_switch, _ = st.columns([1, 4])
with col_switch:
    neon_on = st.toggle("Uruchom Neon ⚡", key="neon_switch")

neon_class = "neon-flicker" if neon_on else ""

# Nagłówek z mrugającym logo
st.markdown(f"""
<div class="friends-logo {neon_class}">
    L<span class="dot-red">.</span>O<span class="dot-blue">.</span>G<span class="dot-yellow">.</span>I<span class="dot-red">.</span>S<span class="dot-blue">.</span>T<span class="dot-yellow">.</span>I<span class="dot-red">.</span>C P<span class="dot-blue">.</span>E<span class="dot-yellow">.</span>R<span class="dot-red">.</span>K
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align:center; color:#f1c40f; font-weight:bold; letter-spacing:3px;'>PIOTR DUKIEL  | LOGISTICS HUB</p>", unsafe_allow_html=True)

l_col, r_col = st.columns([1.5, 1], gap="large")

with l_col:
    st.markdown("### 🎬 Logistics Scripts")
    
    # Wyświetlamy tylko wiersze z treścią, posortowane od najnowszych
    display_df = df[df['Note'].astype(str).str.strip() != ""].sort_values(by=['Date', 'Timestamp'], ascending=False)
    
    if display_df.empty:
        st.info("Brak aktywnych zadań. Czas na kawę? ☕")
    
    for _, row in display_df.iterrows():
        is_unagi = str(row['Status']).strip().upper() == "UNAGI"
        
        st.markdown(f"""
            <div class="chalkboard-card {'unagi-card' if is_unagi else ''}">
                <div style="font-size:0.8rem; color:#f1c40f; font-family:Varela Round;">📅 {row['Date']} | ⏰ {row['Timestamp']}</div>
                <div class="note-body">"{row['Note']}"</div>
                { '<div style="color:#2ecc71; font-family:Permanent Marker; margin-top:10px;">🍣 STATUS: UNAGI</div>' if is_unagi else '' }
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("⏪ EDIT", key=f"ed_{row['ID']}"):
                st.session_state.edit_val = row['Note']
                st.rerun()
        with c2:
            if st.button("❌ CUT", key=f"de_{row['ID']}"):
                st.session_state.del_target = row['ID']
                st.rerun()
        with c3:
            if st.button("🍣 UNAGI", key=f"un_{row['ID']}"):
                st.session_state.unagi_target = row['ID']
                st.rerun()

with r_col:
    st.markdown("### 🖋️ New Scenario")
    with st.container(border=True):
        with st.form("new_entry", clear_on_submit=True):
            # Tu zadziała kursor-filiżanka!
            txt = st.text_area("Slot & Transport Details:", value=st.session_state.edit_val, height=180, help="Kursor zmieni się w kawę po najechaniu!")
            st.markdown('<div class="pivot-container">', unsafe_allow_html=True)
            if st.form_submit_button("PIVOT!"):
                if txt:
                    new_row = pd.DataFrame([{
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Note": txt,
                        "ID": str(uuid.uuid4()),
                        "Timestamp": datetime.now().strftime("%H:%M:%S"),
                        "Category": "General",
                        "Status": "Active"
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    st.session_state.edit_val = ""
                    safe_update(df)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📅 Logistics Calendar")
    
    events = []
    for _, r in df.iterrows():
        if r['Note']:
            color = "#2ecc71" if str(r['Status']).upper() == "UNAGI" else "#e74c3c"
            events.append({
                "title": f"🚚 {str(r['Note'])[:15]}...",
                "start": str(r['Date']),
                "color": color
            })
    
    calendar(events=events, options={"initialView": "dayGridMonth", "firstDay": 1}, key="friends_cal_v10")

st.markdown("<p style='text-align:center; opacity:0.4; margin-top:50px;'>Logistics Perk v10.0 | PIOTR DUKIEL | 2026</p>", unsafe_allow_html=True)
