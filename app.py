import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# Ustawienia strony logistycznej SQM
st.set_page_config(
    page_title="SQM Notatnik Country", 
    page_icon="🚛", 
    layout="wide"
)

# STYLIZACJA CSS - STYL COUNTRY
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Lora:wght@400;700&display=swap');

    .stApp {
        background-color: #fdf5e6;
        color: #3e2723;
    }

    h1, h2, h3 {
        font-family: 'Special+Elite', serif;
        color: #5d4037 !important;
    }

    .stButton>button {
        background-color: #8d6e63 !important;
        color: #ffffff !important;
        border: 2px solid #5d4037 !important;
        font-family: 'Lora', serif;
        border-radius: 0px !important;
    }

    .fc { /* Kalendarz */
        background-color: #ffffff;
        padding: 15px;
        border-radius: 5px;
        border: 2px solid #d7ccc8;
    }

    [data-testid="stSidebar"] {
        background-color: #efebe9 !important;
    }
</style>
""", unsafe_allow_html=True)

# POŁĄCZENIE Z GOOGLE SHEETS
# Upewnij się, że w Secrets masz [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Pobieramy dane z arkusza Sheet1
    return conn.read(worksheet="Sheet1", ttl="0s")

def save_data(dataframe):
    # Nadpisujemy arkusz nowymi danymi
    conn.update(worksheet="Sheet1", data=dataframe)
    st.cache_data.clear()

# Inicjalizacja danych
try:
    df = load_data()
except Exception as e:
    # Jeśli arkusz jest pusty, tworzymy szkielet
    df = pd.DataFrame(columns=["Date", "Note", "ID"])

# Tytuł aplikacji
st.title("🤠 SQM: Logistyczny Notatnik Country")
st.write(f"Zalogowano do arkusza: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Przygotowanie wpisów do kalendarza
calendar_events = []
if not df.empty:
    for i, row in df.iterrows():
        if pd.notna(row['Date']) and row['Date'] != "":
            calendar_events.append({
                "title": str(row['Note']),
                "start": str(row['Date']),
                "id": str(row['ID']),
                "color": "#8d6e63"
            })

# Układ kolumn
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Kalendarz")
    
    calendar_options = {
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth"
        },
        "initialView": "dayGridMonth",
        "firstDay": 1,
        "locale": "pl"
    }
    
    state = calendar(
        events=calendar_events,
        options=calendar_options,
        key="country_cal"
    )

    if state.get("dateClick"):
        st.session_state["clicked_date"] = state["dateClick"]["date"].split("T")[0]

with col_right:
    st.subheader("Zarządzaj notatkami")
    
    tab1, tab2 = st.tabs(["Dodaj", "Edytuj / Usuń"])
    
    # DODAWANIE
    with tab1:
        with st.form("new_note_form", clear_on_submit=True):
            sel_date = st.session_state.get("clicked_date", datetime.now().strftime("%Y-%m-%d"))
            date_val = st.date_input("Data wpisu", value=datetime.strptime(sel_date, "%Y-%m-%d"))
            note_val = st.text_area("Treść (np. transport, nr naczepy, slot)")
            
            if st.form_submit_button("ZAPISZ"):
                if note_val:
                    new_row = pd.DataFrame([{
                        "Date": date_val.strftime("%Y-%m-%d"),
                        "Note": note_val,
                        "ID": str(uuid.uuid4())
                    }])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success("Zapisano w Google Sheets!")
                    st.rerun()
                else:
                    st.warning("Wpisz treść notatki.")

    # EDYCJA / USUWANIE
    with tab2:
        if not df.empty:
            note_to_edit = st.selectbox(
                "Wybierz notatkę do zmiany",
                options=df.index,
                format_func=lambda x: f"{df.at[x, 'Date']} - {str(df.at[x, 'Note'])[:20]}..."
            )
            
            new_text = st.text_area("Popraw treść", value=df.at[note_to_edit, 'Note'])
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("AKTUALIZUJ"):
                    df.at[note_to_edit, 'Note'] = new_text
                    save_data(df)
                    st.success("Zmieniono!")
                    st.rerun()
            with c2:
                if st.button("USUŃ"):
                    df = df.drop(note_to_edit)
                    save_data(df)
                    st.warning("Usunięto!")
                    st.rerun()
        else:
            st.info("Brak notatek do wyświetlenia.")

# Podgląd tabeli dla pewności
with st.expander("Zobacz podgląd arkusza (Raw Data)"):
    st.dataframe(df, use_container_width=True)
