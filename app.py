import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM: The One Where We Ship It", page_icon="🟡", layout="wide")

# --- DESIGN: THE ULTIMATE FRIENDS EXPERIENCE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Varela+Round&family=Kalam:wght@300;700&display=swap');

    :root {
        --friends-red: #e74c3c;
        --friends-yellow: #f1c40f;
        --friends-blue: #3498db;
        --monica-purple: #6a5acd;
    }

    .stApp {
        background-color: var(--monica-purple);
        background-image: url("https://www.transparenttextures.com/patterns/cubes.png");
    }

    /* Nagłówek z kropkami */
    .friends-logo {
        font-family: 'Permanent Marker', cursive;
        font-size: 5rem;
        text-align: center;
        color: white;
        margin-bottom: 10px;
    }
    .dot-red { color: var(--friends-red); }
    .dot-yellow { color: var(--friends-yellow); }
    .dot-blue { color: var(--friends-blue); }

    /* Kultowa żółta ramka Moniki jako kontener notatki */
    .monica-frame {
        border: 12px solid var(--friends-yellow);
        border-radius: 50% 5% 50% 5% / 5% 50% 5% 50%; /* Nieregularny kształt ramki */
        padding: 30px;
        background-color: rgba(255, 255, 255, 0.95);
        color: #2c3e50;
        font-family: 'Kalam', cursive;
        box-shadow: 15px 15px 30px rgba(0,0,0,0.4);
        position: relative;
        min-height: 200px;
    }

    .category-badge {
        position: absolute;
        top: -15px;
        right: 10px;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
        font-family: 'Varela Round', sans-serif;
    }

    /* Przyciski sterujące */
    .stButton>button {
        font-family: 'Permanent Marker', cursive !important;
        border-radius: 50px !important;
        border: 3px solid white !important;
        font-size: 1.2rem !important;
        transition: all 0.2s;
        height: 3em !important;
    }

    /* Kolory przycisków */
    div.stButton > button:first-child { background-color: var(--friends-red) !important; color: white !important; } /* Pivot */
    
    /* Inputy */
    .stTextArea textarea {
        background-color: #fdfdfd !important;
        border: 2px solid var(--friends-blue) !important;
        font-family: 'Varela Round', sans-serif !important;
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: var(--monica-purple); }
    ::-webkit-scrollbar-thumb { background: var(--friends-yellow); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- LOGIKA KATEGORII ---
CATEGORIES = {
    "Monica (Hard Deadline)": {"color": "#e74c3c", "icon": "🧹"},
    "Joey (Logistics/Trucks)": {"color": "#e67e22", "icon": "🍕"},
    "Ross (Technical/Specs)": {"color": "#3498db", "icon": "🦖"},
    "Chandler (Office/Admin)": {"color": "#9b59b6", "icon": "💻"},
    "Phoebe (Random/Other)": {"color": "#2ecc71", "icon": "🎸"}
}

# --- POŁĄCZENIE Z DANYMI ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        data = conn.read(ttl="1s")
        if "Category" not in data.columns:
            data["Category"] = "Phoebe (Random/Other)"
        return data
    except Exception:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID", "Category"])

df = load_data()

# --- HEADER ---
st.markdown("""
    <div class="friends-logo">
        S<span class="dot-red">.</span>Q<span class="dot-yellow">.</span>M<span class="dot-blue">.</span> 
        L<span class="dot-red">.</span>O<span class="dot-yellow">.</span>G<span class="dot-blue">.</span>S
    </div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown("### 📝 The One Where You Add a Task")
    
    with st.form("main_form"):
        # Wybór "postaci" (kategorii)
        cat_choice = st.selectbox("Who's responsible?", list(CATEGORIES.keys()))
        
        note_txt = st.text_area(
            "What's the situation?",
            value=st.session_state.get('edit_content', ""),
            height=150,
            placeholder="Type here or 'Regina Phalange' will find you..."
        )
        
        # PIVOT Button
        submit = st.form_submit_button("PIVOT! PIVOT! PIVOT!")
        
        if submit and note_txt:
            now = datetime.now()
            new_row = pd.DataFrame([{
                "Timestamp": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Note": note_txt,
                "ID": str(uuid.uuid4()),
                "Category": cat_choice
            }])
            
            df = pd.concat([df, new_row], ignore_index=True)
            conn.update(data=df)
            st.cache_data.clear()
            st.session_state['edit_content'] = ""
            st.balloons()
            st.rerun()

    st.markdown("---")
    st.markdown("### 🎞️ Previous Episodes (Notes)")

    if not df.empty:
        sorted_df = df.sort_values(by=['Date', 'Timestamp'], ascending=False)
        for _, row in sorted_df.iterrows():
            cat_info = CATEGORIES.get(row['Category'], CATEGORIES["Phoebe (Random/Other)"])
            
            # Kartka w żółtej ramce Moniki
            st.markdown(f"""
                <div class="monica-frame">
                    <div class="category-badge" style="background-color: {cat_info['color']};">
                        {cat_info['icon']} {row['Category']}
                    </div>
                    <div style="font-size: 0.8rem; color: #7f8c8d; margin-bottom: 10px;">
                        Season {row['Date'][:4]} | Ep. {row['Timestamp']}
                    </div>
                    <div style="font-size: 1.3rem; line-height: 1.2; color: #2c3e50; font-weight: bold;">
                        {row['Note']}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Przyciski pod ramką
            c1, c2, _ = st.columns([1, 1, 2])
            with c1:
                if st.button("Edit", key=f"ed_{row['ID']}"):
                    st.session_state['edit_content'] = row['Note']
                    st.rerun()
            with c2:
                if st.button("Delete", key=f"de_{row['ID']}"):
                    df = df[df['ID'] != row['ID']]
                    conn.update(data=df)
                    st.cache_data.clear()
                    st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)

with col_right:
    st.markdown("### 🗓️ Central Perk Master Schedule")
    
    # Przygotowanie eventów z kolorami kategorii
    calendar_events = []
    for _, row in df.iterrows():
        cat_color = CATEGORIES.get(row['Category'], {"color": "#333"})["color"]
        calendar_events.append({
            "title": f"{row['Category'].split(' ')[0]}: {row['Note'][:20]}",
            "start": str(row['Date']),
            "backgroundColor": cat_color,
            "borderColor": "white"
        })

    calendar(
        events=calendar_events,
        options={
            "initialView": "dayGridMonth",
            "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
            "height": 600,
        },
        key="friends_ultra_calendar"
    )
    
    # Cytat na poprawę humoru przy ciężkiej logistyce
    st.markdown("""
        <div style="background: rgba(255,255,255,0.2); padding: 20px; border-radius: 15px; margin-top: 20px; text-align: center; font-style: italic;">
            "Welcome to the real world! It sucks. You're gonna love it!" <br><b>- Monica Geller</b>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("Secret Geller Cup (Raw Data)"):
        st.dataframe(df, use_container_width=True)
