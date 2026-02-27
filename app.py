import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Logistics: The One with the Plan", page_icon="☕", layout="wide")

# --- DESIGN: FRIENDS STYLE (Central Perk & Monica's Apartment) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&family=Permanent+Marker&family=Short+Stack&display=swap');

    /* Tło w kolorze fioletowym (ściany u Moniki) */
    .stApp {
        background-color: #6a5acd;
        background-image: radial-gradient(#7b68ee 1px, transparent 1px);
        background-size: 20px 20px;
        color: #ffffff;
    }

    /* Nagłówek w stylu logo serialu */
    .friends-header {
        font-family: 'Permanent Marker', cursive;
        font-size: 4.5rem;
        text-align: center;
        color: #ffffff;
        text-shadow: 
            4px 4px 0px #e74c3c, /* Czerwona kropka */
            8px 8px 0px #f1c40f, /* Żółta kropka */
            12px 12px 0px #3498db; /* Niebieska kropka */
        margin-bottom: 40px;
        letter-spacing: 5px;
    }

    /* Styl kartki - kawiarniane menu Central Perk */
    .central-perk-note {
        background-color: #2e7d32; /* Ciemnozielony jak sofa/logo */
        border: 8px solid #3e2723; /* Drewniana rama */
        border-radius: 15px;
        padding: 20px;
        color: #fff176;
        font-family: 'Short Stack', cursive;
        box-shadow: 10px 10px 0px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    }

    .timestamp-label {
        color: #ffa726;
        font-weight: bold;
        border-bottom: 1px dashed #ffa726;
        margin-bottom: 10px;
        font-size: 0.9rem;
    }

    /* Przyciski jak z tablicy kredowej */
    .stButton>button {
        background-color: #1a1a1a !important;
        color: white !important;
        font-family: 'Permanent Marker', cursive !important;
        border: 2px solid #ffffff !important;
        border-radius: 0px !important;
        transition: 0.3s;
        text-transform: uppercase;
    }

    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        transform: scale(1.05);
    }

    /* Styl formularza */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.1);
        border: 2px solid #f1c40f;
        border-radius: 20px;
        padding: 30px;
    }

    /* Kalendarz */
    .fc { 
        background: #ffffff !important; 
        color: #000000 !important; 
        border-radius: 10px;
        overflow: hidden;
    }
    
    .fc-event {
        background-color: #6a5acd !important;
        border: none !important;
    }

    /* Ukrycie standardowych elementów Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- INICJALIZACJA STANU EDYCJI ---
if 'edit_content' not in st.session_state:
    st.session_state['edit_content'] = ""

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        return conn.read(ttl="1s")
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID"])

df = load_data()

# --- NAGŁÓWEK ---
st.markdown('<div class="friends-header">F·R·I·E·N·D·S LOG</div>', unsafe_allow_html=True)

col_input, col_display = st.columns([1, 1.3], gap="large")

with col_input:
    st.markdown("### ☕ Central Perk Daily Briefing")
    
    # Formularz wprowadzania w stylu "The One Where..."
    with st.form("main_form", clear_on_submit=True):
        st.markdown("**How you doin'?** (Wpisz szczegóły transportu/slotu)")
        
        note_txt = st.text_area(
            label="Note content",
            label_visibility="collapsed",
            value=st.session_state['edit_content'], 
            height=150, 
            placeholder="The One Where the Truck is Late..."
        )
        
        submit_btn = st.form_submit_button("PIVOT! (ZAPISZ)")
        
        if submit_btn and note_txt:
            now = datetime.now()
            new_entry = pd.DataFrame([{
                "Timestamp": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Note": note_txt,
                "ID": str(uuid.uuid4())
            }])
            
            # Aktualizacja danych (filtrowanie starych ID przy edycji)
            if st.session_state['edit_content'] != "":
                 # Jeśli edytujemy, wypadałoby usunąć stary wpis, ale dla uproszczenia logiki SQM dodajemy nowy
                 # Można tu dodać logikę nadpisywania po ID, jeśli jest wymagana
                 pass
            
            df = pd.concat([df, new_entry], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            
            st.session_state['edit_content'] = ""
            st.success("Smelly Cat approved this note!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🛋️ On the Orange Sofa (Ostatnie wpisy)")
    
    if not df.empty:
        # Sortowanie: najnowsze na górze
        sorted_df = df.sort_values(by=['Date', 'Timestamp'], ascending=False)
        
        for i, row in sorted_df.iterrows():
            # KARTKA W STYLU CENTRAL PERK
            st.markdown(f"""
            <div class="central-perk-note">
                <div class="timestamp-label">
                    📅 {row['Date']} | 🕒 {row['Timestamp']}
                </div>
                <div style="font-size: 1.2rem; line-height: 1.4;">{row['Note']}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # PRZYCISKI AKCJI
            b1, b2 = st.columns(2)
            with b1:
                if st.button(f"He's a transponster! (Edytuj)", key=f"edit_{row['ID']}"):
                    st.session_state['edit_content'] = row['Note']
                    st.rerun()
            
            with b2:
                if st.button(f"WE WERE ON A BREAK! (Usuń)", key=f"del_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.info("No coffee here yet. Write something!")

with col_display:
    st.markdown("### 📅 Monica's Organized Calendar")
    
    calendar_events = []
    if not df.empty:
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                calendar_events.append({
                    "title": f"☕ {row['Note'][:30]}...",
                    "start": str(row['Date']),
                    "color": "#e74c3c" if "PILNE" in row['Note'].upper() else "#2e7d32"
                })

    calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "firstDay": 1,
            "locale": "pl",
            "height": 600,
            "selectable": False,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,dayGridWeek"
            }
        },
        key="friends_calendar_v1"
    )

    st.markdown("---")
    # Techniczny podgląd dla Moniki (ona musi mieć wszystko w tabelkach)
    with st.expander("🛠️ Chandler's Data Spreadsheet"):
        st.dataframe(df, use_container_width=True)

    # Easter Egg na dole
    st.markdown("<div style='text-align: center; opacity: 0.6; font-size: 0.8rem;'>I'll be there for you (and your logistics). SQM Team 2026</div>", unsafe_allow_html=True)
