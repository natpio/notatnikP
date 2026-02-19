import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime

# Konfiguracja SQM
st.set_page_config(page_title="SQM Notatnik", page_icon="🚛", layout="wide")

# Styl Country
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Special+Elite&family=Lora:wght@400;700&display=swap');
    .stApp { background-color: #fdf5e6; color: #3e2723; }
    h1, h2, h3 { font-family: 'Special+Elite', serif; color: #5d4037 !important; }
    .stButton>button { background-color: #8d6e63 !important; color: #ffffff !important; border: 2px solid #5d4037 !important; font-family: 'Lora', serif; border-radius: 0px !important; }
    .fc { background-color: #ffffff; padding: 15px; border-radius: 5px; border: 2px solid #d7ccc8; }
</style>
""", unsafe_allow_html=True)

# Połączenie
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    # Pobiera dane z pierwszej karty arkusza
    return conn.read(ttl="0s")

def save_data(dataframe):
    # Zapisuje dane z powrotem do arkusza
    conn.update(data=dataframe)
    st.cache_data.clear()

# Załaduj dane lub stwórz puste, jeśli arkusz nie ma nagłówków
try:
    df = load_data()
    # Upewnij się, że kolumna ID istnieje
    if "ID" not in df.columns:
        df["ID"] = [str(uuid.uuid4()) for _ in range(len(df))]
except:
    df = pd.DataFrame(columns=["Date", "Note", "ID"])

st.title("🤠 SQM: Logistyczny Notatnik")

calendar_events = []
if not df.empty:
    for _, row in df.iterrows():
        if pd.notna(row['Date']) and str(row['Date']).strip() != "":
            calendar_events.append({
                "title": str(row['Note']),
                "start": str(row['Date']),
                "id": str(row['ID']),
                "color": "#8d6e63"
            })

col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("Kalendarz miesięczny")
    state = calendar(
        events=calendar_events,
        options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "firstDay": 1, "locale": "pl"},
        key="sqm_cal"
    )
    if state.get("dateClick"):
        st.session_state["clicked_date"] = state["dateClick"]["date"].split("T")[0]

with col_right:
    st.subheader("Opcje")
    t1, t2 = st.tabs(["Dodaj", "Edytuj/Usuń"])
    
    with t1:
        with st.form("add_form", clear_on_submit=True):
            def_date = st.session_state.get("clicked_date", datetime.now().strftime("%Y-%m-%d"))
            d_val = st.date_input("Data", value=datetime.strptime(def_date, "%Y-%m-%d"))
            n_val = st.text_area("Treść notatki")
            if st.form_submit_button("ZAPISZ"):
                new_entry = pd.DataFrame([{"Date": d_val.strftime("%Y-%m-%d"), "Note": n_val, "ID": str(uuid.uuid4())}])
                df = pd.concat([df, new_entry], ignore_index=True)
                save_data(df)
                st.success("Dodano!")
                st.rerun()

    with t2:
        if not df.empty:
            idx = st.selectbox("Wybierz wpis", options=df.index, format_func=lambda x: f"{df.at[x, 'Date']} - {str(df.at[x, 'Note'])[:20]}")
            edit_txt = st.text_area("Zmień treść", value=df.at[idx, 'Note'])
            if st.button("AKTUALIZUJ"):
                df.at[idx, 'Note'] = edit_txt
                save_data(df)
                st.success("Zmieniono!")
                st.rerun()
            if st.button("USUŃ"):
                df = df.drop(idx)
                save_data(df)
                st.warning("Usunięto!")
                st.rerun()

with st.expander("Podgląd bazy danych"):
    st.dataframe(df)
