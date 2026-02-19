import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
from datetime import datetime
import uuid

# Konfiguracja strony pod logistykę SQM
st.set_page_config(
    page_title="SQM Notatnik Country", 
    page_icon="🚛", 
    layout="wide"
)

# STYLIZACJA CSS - STYL COUNTRY / RUSTIC
st.markdown("""
<style>
    /* Import czcionek */
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Lora:wght@400;700&display=swap');

    /* Tło i główne kontenery */
    .stApp {
        background-color: #f4ece2;
        color: #3e2723;
    }

    /* Nagłówki */
    h1, h2, h3 {
        font-family: 'Special+Elite', serif;
        color: #5d4037 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Karty i sekcje */
    .stHeader {
        background-color: #d7ccc8;
    }

    /* Przyciski w stylu retro */
    .stButton>button {
        background-color: #8d6e63 !important;
        color: #ffffff !important;
        border: 2px solid #5d4037 !important;
        font-family: 'Lora', serif;
        font-weight: bold;
        border-radius: 0px !important;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #5d4037 !important;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }

    /* Kalendarz - dopasowanie kolorów */
    .fc-theme-standard td, .fc-theme-standard th {
        border: 1px solid #d7ccc8 !important;
    }
    
    .fc-daygrid-day:hover {
        background-color: #efebe9 !important;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #e0d7d0 !important;
        border-right: 2px solid #8d6e63;
    }
</style>
""", unsafe_allow_html=True)

# POŁĄCZENIE Z GOOGLE SHEETS
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Pobieranie danych z Twojego arkusza
    return conn.read(ttl="0s")

def save_data(dataframe):
    # Aktualizacja arkusza
    conn.update(data=dataframe)
    st.cache_data.clear()

# Załadowanie aktualnych danych
df = get_data()

# Nagłówek główny
st.title("🤠 Notatnik Logistyczny SQM")
st.markdown("---")

# Layout: Lewa strona (Kalendarz), Prawa strona (Edycja/Dodawanie)
col_cal, col_form = st.columns([2, 1])

# PRZYGOTOWANIE EVENTÓW DLA KALENDARZA
calendar_events = []
if not df.empty:
    for _, row in df.iterrows():
        if pd.notna(row['Date']):
            calendar_events.append({
                "title": str(row['Note']),
                "start": str(row['Date']),
                "id": str(row['ID']),
                "allDay": True,
                "backgroundColor": "#8d6e63",
                "borderColor": "#3e2723"
            })

with col_cal:
    st.subheader("Plan Miesięczny")
    
    # Konfiguracja kalendarza
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
        "editable": False,
        "selectable": True,
        "firstDay": 1, # Poniedziałek jako pierwszy dzień
        "locale": "pl"
    }
    
    state = calendar(
        events=calendar_events,
        options=calendar_options,
        key="sqm_calendar"
    )

    # Reakcja na kliknięcie w datę
    if state.get("dateClick"):
        clicked_date = state["dateClick"]["date"].split("T")[0]
        st.session_state["selected_date"] = clicked_date
        st.info(f"Wybrano datę: {clicked_date}. Wypełnij formularz obok, aby dodać wpis.")

with col_form:
    st.subheader("Zarządzanie wpisami")
    
    # Zakładki dla czystości interfejsu
    tab_add, tab_edit = st.tabs(["➕ Dodaj", "✏️ Edytuj / Usuń"])
    
    with tab_add:
        default_date = st.session_state.get("selected_date", datetime.now().strftime("%Y-%m-%d"))
        
        with st.form("add_form", clear_on_submit=True):
            date_input = st.date_input("Data", value=datetime.strptime(default_date, "%Y-%m-%d"))
            note_input = st.text_area("Treść notatki (np. slot, nr naczepy, kierowca)")
            submit_add = st.form_submit_button("ZAPISZ W ARKUSZU")
            
            if submit_add:
                if note_input:
                    new_entry = pd.DataFrame([{
                        "Date": date_input.strftime("%Y-%m-%d"),
                        "Note": note_input,
                        "ID": str(uuid.uuid4())
                    }])
                    df = pd.concat([df, new_entry], ignore_index=True)
                    save_data(df)
                    st.success("Wpis zapisany!")
                    st.rerun()
                else:
                    st.error("Wpisz treść notatki!")

    with tab_edit:
        if not df.empty:
            # Wybór wpisu do edycji na podstawie daty i treści
            note_options = df.index.tolist()
            selected_idx = st.selectbox(
                "Wybierz wpis do zmiany",
                options=note_options,
                format_func=lambda x: f"{df.at[x, 'Date']} | {str(df.at[x, 'Note'])[:30]}..."
            )
            
            edit_note = st.text_area("Edytuj treść", value=df.at[selected_idx, "Note"])
            edit_date = st.date_input("Zmień datę", value=datetime.strptime(str(df.at[selected_idx, "Date"]), "%Y-%m-%d"))
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("AKTUALIZUJ"):
                    df.at[selected_idx, "Note"] = edit_note
                    df.at[selected_idx, "Date"] = edit_date.strftime("%Y-%m-%d")
                    save_data(df)
                    st.success("Zaktualizowano!")
                    st.rerun()
            
            with col_btn2:
                if st.button("USUŃ WPIS"):
                    df = df.drop(selected_idx)
                    save_data(df)
                    st.warning("Usunięto!")
                    st.rerun()
        else:
            st.write("Brak wpisów do edycji.")

# STOPKA LOGISTYCZNA
st.markdown("---")
if st.checkbox("Pokaż podgląd tabeli (Raw Data)"):
    st.dataframe(df, use_container_width=True)

st.caption("System logistyczny SQM Multimedia Solutions | Styl Country v1.0")
