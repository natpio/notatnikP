import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
import random
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM LOGISTICS: THE FINAL SEASON", page_icon="🛋️", layout="wide")

# --- DESIGN: THE ULTIMATE FRIENDS OVERLOAD (NEON EDITION) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@700&family=Gloria+Hallelujah&display=swap');

    /* Tło - Kultowy fiolet Moniki z teksturą cegły */
    .stApp {
        background-color: #6a5acd;
        background-image: url("https://www.transparenttextures.com/patterns/brick-wall.png");
        color: white;
    }

    /* Logo z animacją pulsowania i neonem */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 6rem;
        text-align: center;
        color: white;
        text-shadow: 
            0 0 10px #fff,
            4px 4px #e74c3c, 
            8px 8px #f1c40f, 
            12px 12px #3498db;
        animation: pulse 2s infinite;
        margin-bottom: 50px;
    }

    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }

    /* Kontener notatki jako "Fioletowe Drzwi" */
    .door-note {
        background-color: #7b68ee;
        border: 10px solid #f1c40f; /* Żółta ramka */
        border-radius: 10px;
        padding: 25px;
        margin-bottom: 30px;
        box-shadow: 20px 20px 0px rgba(0,0,0,0.5);
        position: relative;
        transition: transform 0.3s;
    }
    
    .door-note:hover {
        transform: rotate(-1deg) scale(1.02);
    }

    .peephole {
        position: absolute;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        width: 30px;
        height: 30px;
        background: #444;
        border-radius: 50%;
        border: 4px solid #f1c40f;
    }

    .note-text {
        font-family: 'Gloria Hallelujah', cursive;
        font-size: 1.4rem;
        color: #fff;
        margin-top: 25px;
        line-height: 1.4;
    }

    /* PIVOT BUTTON - Shaking effect */
    .pivot-button button {
        background: linear-gradient(45deg, #e74c3c, #f1c40f, #3498db) !important;
        font-family: 'Permanent Marker', cursive !important;
        font-size: 2.5rem !important;
        height: 100px !important;
        border: 5px solid white !important;
        color: white !important;
        text-shadow: 2px 2px #000;
        animation: shake 0.5s infinite;
        animation-play-state: paused;
        width: 100%;
    }

    .pivot-button button:hover {
        animation-play-state: running;
    }

    @keyframes shake {
        0% { transform: translate(1px, 1px) rotate(0deg); }
        10% { transform: translate(-1px, -2px) rotate(-1deg); }
        30% { transform: translate(3px, 2px) rotate(0deg); }
        50% { transform: translate(-1px, 2px) rotate(1deg); }
        100% { transform: translate(1px, -2px) rotate(-1deg); }
    }

    /* Ukrycie nudnych elementów */
    div[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- FUNKCJE I DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="1s")
        # WYMUSZENIE KOLUMN - To naprawia Twój błąd
        expected_cols = ["Timestamp", "Date", "Note", "ID", "Category"]
        for col in expected_cols:
            if col not in data.columns:
                data[col] = "None"
        return data
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category"])

df = load_data()

# Funkcja pomocnicza do bezpiecznego pobierania tekstu
def get_safe_val(val, length=None):
    s = str(val) if val is not None else "???"
    return s[:length] if length else s

FRIENDS_QUOTES = [
    "How you doin'?",
    "WE WERE ON A BREAK!",
    "Pivot! Pivot! PIVOT!",
    "I'm not great at the advice. Can I interest you in a sarcastic comment?",
    "Could this BE any more organized?",
    "Joey doesn't share food!",
    "Smelly cat, smelly cat, what are they feeding you?",
    "Welcome to the real world. It sucks. You’re gonna love it!"
]

CATEGORIES = {
    "MONICA: Clean & Fast": "🔴",
    "CHANDLER: Sarcastic Admin": "🔵",
    "ROSS: The Logistics Docent": "🟡",
    "JOEY: Truck Driver Vibes": "🟠",
    "PHOEBE: Smelly Logistics": "🟢"
}

# --- UI ---
st.markdown('<div class="friends-logo">F·R·I·E·N·D·S<br><small style="font-size: 2rem;">SQM LOGISTICS EDITION</small></div>', unsafe_allow_html=True)

if 'quote' not in st.session_state:
    st.session_state.quote = random.choice(FRIENDS_QUOTES)

st.info(f"💡 {st.session_state.quote}")

col_form, col_content = st.columns([1, 1.5], gap="large")

with col_form:
    st.markdown("### 🎬 Start New Episode")
    with st.form("ultimate_form"):
        char_cat = st.radio("Who's handling this slot?", list(CATEGORIES.keys()), horizontal=True)
        
        note_content = st.text_area("What's the 'The One With...' title?", 
                                    value=st.session_state.get('edit_content', ""),
                                    height=150, 
                                    placeholder="The One Where the 24t Truck Arrives Early...")
        
        st.markdown('<div class="pivot-button">', unsafe_allow_html=True)
        pivot = st.form_submit_button("PIVOT!")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if pivot and note_content:
            new_data = pd.DataFrame([{
                "Timestamp": datetime.now().strftime("%H:%M:%S"),
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Note": note_content,
                "ID": str(uuid.uuid4()),
                "Category": char_cat
            }])
            df = pd.concat([df, new_data], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            st.session_state.edit_content = ""
            st.session_state.quote = random.choice(FRIENDS_QUOTES)
            st.rerun()

    st.markdown("---")
    st.markdown("### ☕ Central Perk Slot Tracker")
    cal_events = []
    for _, row in df.iterrows():
        # Bezpieczne pobieranie wartości do kalendarza
        cat_name = get_safe_val(row.get('Category', '???'), 3)
        note_preview = get_safe_val(row.get('Note', ''), 15)
        
        cal_events.append({
            "title": f"{cat_name}: {note_preview}",
            "start": str(row['Date']),
            "color": "#f1c40f" if "ROSS" in str(row['Category']).upper() else "#e74c3c"
        })
    
    calendar(events=cal_events, options={"initialView": "dayGridMonth"}, key="ultra_cal_v2")

with col_content:
    st.markdown("### 📺 Season Highlights (Your Logs)")
    
    if df.empty or (len(df) == 1 and df.iloc[0]['Note'] == ""):
        st.warning("No episodes recorded yet. Is the show cancelled?")
    else:
        # Sortowanie od najnowszych
        sorted_df = df.sort_values(by=['Date', 'Timestamp'], ascending=False)
        for _, row in sorted_df.iterrows():
            if not row['Note'] or row['Note'] == "None": continue
            
            with st.container():
                st.markdown(f"""
                <div class="door-note">
                    <div class="peephole"></div>
                    <div style="display: flex; justify-content: space-between; border-bottom: 2px solid rgba(255,255,255,0.3); padding-bottom: 5px;">
                        <span style="font-family: 'Varela Round'; font-weight: bold; color: #f1c40f;">
                            {CATEGORIES.get(row['Category'], '⚪')} {row['Category']}
                        </span>
                        <span style="font-size: 0.8rem; opacity: 0.8;">{row['Date']} @ {row['Timestamp']}</span>
                    </div>
                    <div class="note-text">
                        "{row['Note']}"
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                c1, c2, c3 = st.columns([1, 1, 1])
                with c1:
                    if st.button("Rewind (Edytuj)", key=f"ed_{row['ID']}"):
                        st.session_state.edit_content = row['Note']
                        st.rerun()
                with c2:
                    if st.button("Cancel Show (Usuń)", key=f"del_{row['ID']}"):
                        df = df[df['ID'] != row['ID']]
                        conn.update(data=df)
                        st.cache_data.clear()
                        st.rerun()
                with c3:
                    if st.button("Unagi! (Ważne)", key=f"un_{row['ID']}"):
                        st.toast("Unagi! Total awareness of this slot.")

st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.5;'>The One with SQM Multimedia Solutions & Logistics - 2026</p>", unsafe_allow_html=True)
