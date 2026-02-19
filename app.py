import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM Terminal", page_icon="📝", layout="wide")

# --- DESIGN: WHATSAPP STYLE & NO BLINK ---
st.markdown("""
<style>
    .stApp { background-color: #f0f2f5; }
    
    /* Ukrycie menu Streamlit dla większego skupienia */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Karty notatek */
    .note-card {
        background-color: #ffffff;
        padding: 12px;
        border-radius: 10px;
        border-left: 5px solid #25d366;
        margin-bottom: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        font-family: 'Segoe UI', sans-serif;
    }
    
    .timestamp { color: #888; font-size: 0.8rem; }

    /* Duże pole tekstowe */
    .stTextArea textarea {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE I DANE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl="0s" wymusza pobranie świeżych danych bez mrugania przy każdym ruchu myszką
        df = conn.read(ttl="0s")
        return df
    except:
        return pd.DataFrame(columns=["Timestamp", "Date", "Note", "ID"])

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

# Załaduj dane raz na cykl
df = load_data()

# --- UKŁAD ---
col_left, col_right = st.columns([1, 1.2], gap="large")

with col_left:
    st.markdown("### ⚡ Szybki Zapis")
    
    # Używamy formularza, aby uniknąć mrugania przy każdym wpisanym znaku
    with st.form("quick_note_form", clear_on_submit=True):
        note_content = st.text_area("Treść notatki z rozmowy/maila:", height=150, placeholder="Np. Kierowca dzwonił, będzie za 20 min pod slotem 4...")
        submit = st.form_submit_button("ZAPISZ (ENTER)")
        
        if submit and note_content:
            now = datetime.now()
            new_note = pd.DataFrame([{
                "Timestamp": now.strftime("%H:%M:%S"),
                "Date": now.strftime("%Y-%m-%d"),
                "Note": note_content,
                "ID": str(uuid.uuid4())
            }])
            df = pd.concat([df, new_note], ignore_index=True)
            save_data(df)
            st.success("Zapisano!")
            st.rerun()

    st.markdown("---")
    st.markdown("### 🕒 Ostatnie 5 minut")
    
    if not df.empty:
        # Wyświetlamy ostatnie wpisy
        recent = df.tail(5).iloc[::-1]
        for idx, row in recent.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="note-card">
                    <div class="timestamp">{row['Date']} | {row['Timestamp']}</div>
                    {row['Note']}
                </div>
                """, unsafe_allow_html=True)
                # Przycisk do szybkiego kopiowania do schowka (pomocne przy Outlooku)
                st.button(f"Kopiuj treść", key=f"copy_{row['ID']}", on_click=lambda t=row['Note']: st.write(f"Skopiowano: {t}") if False else None)

with col_right:
    st.markdown("### 📅 Widok Dni")
    
    events = []
    if not df.empty:
        for _, row in df.iterrows():
            if pd.notna(row['Date']):
                events.append({
                    "title": f"{row['Timestamp']} - {row['Note'][:40]}...",
                    "start": str(row['Date']),
                    "color": "#25d366"
                })

    # Kluczowa zmiana: kalendarz jest teraz statyczny, nie reaguje na kliknięcia, co eliminuje mruganie
    calendar(
        events=events,
        options={
            "initialView": "dayGridMonth",
            "firstDay": 1,
            "locale": "pl",
            "selectable": False, # Wyłączone dla stabilności
            "height": 550
        },
        key="static_calendar"
    )

    with st.expander("🗑️ Edytuj / Usuń wpisy"):
        if not df.empty:
            edit_df = df.sort_values(by=['Date', 'Timestamp'], ascending=False)
            st.dataframe(edit_df[['Date', 'Timestamp', 'Note']], use_container_width=True)
            
            to_del_id = st.selectbox("Wybierz wpis do usunięcia", options=df.index, format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:20]}")
            if st.button("USUŃ DEFINITYWNIE"):
                df = df.drop(to_del_id)
                save_data(df)
                st.rerun()
