import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
from datetime import datetime, timedelta

# --- KONFIGURACJA ---
st.set_page_config(page_title="SQM LOGISTICS", page_icon="🚛", layout="wide")

# --- MINIMALISTYCZNY DESIGN OPERACYJNY ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; color: #1a1a1a; }
    
    /* Panele boczne i karty */
    [data-testid="stVerticalBlock"] > div.stVerticalBlock {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Przyciski */
    .stButton>button {
        width: 100%;
        background-color: #212529 !important;
        color: white !important;
        font-weight: bold;
        border-radius: 5px !important;
        height: 45px;
    }

    /* Nagłówki */
    h1, h2, h3 { color: #212529 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }

    /* Kalendarz */
    .fc { background: white !important; padding: 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- POŁĄCZENIE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    df = conn.read(ttl="0s")
    if "LDM" not in df.columns: df["LDM"] = 0.0
    return df

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

df = load_data()

# --- INTERFEJS ---
st.title("🚛 SQM: Zarządzanie Transportem i Przestrzenią")

col_left, col_right = st.columns([1, 2], gap="large")

# LEWA KOLUMNA: OPERACJE
with col_left:
    st.subheader("🛠️ Dodaj Zdarzenie")
    with st.form("main_form", clear_on_submit=True):
        d = st.date_input("Data", value=datetime.now())
        t = st.selectbox("Typ", ["🚛 Pełny Transport", "📦 Doładunek", "⏱️ Slot Rozładunkowy", "🛠️ Serwis/Inne"])
        l = st.number_input("Zajęte metry ładowne (LDM)", min_value=0.0, max_value=13.6, step=0.1, help="Standardowa naczepa to 13.6 LDM")
        n = st.text_area("Szczegóły (Nr naczepy, kierowca, miejsce)")
        
        if st.form_submit_button("ZAPISZ"):
            new_row = pd.DataFrame([{"Date": str(d), "Note": n, "Type": t, "LDM": l, "ID": str(uuid.uuid4())}])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Wpis dodany pomyślnie.")
            st.rerun()

    st.markdown("---")
    st.subheader("📋 Plan na najbliższe 2 dni")
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    plan_df = df[df['Date'].isin([today, tomorrow])].sort_values('Date')
    if not plan_df.empty:
        for _, row in plan_df.iterrows():
            with st.container():
                st.markdown(f"**{row['Date']}** | {row['Type']}")
                st.caption(f"{row['Note']} (Zajęte: {row['LDM']} LDM)")
    else:
        st.info("Brak zaplanowanych zadań na dziś i jutro.")

# PRAWA KOLUMNA: HARMONOGRAM I KONTROLA
with col_right:
    st.subheader("📅 Harmonogram Miesięczny")
    
    events = []
    for _, row in df.iterrows():
        if len(str(row['Date'])) >= 10:
            events.append({
                "title": f"[{row['LDM']} LDM] {row['Note'][:20]}...",
                "start": str(row['Date']),
                "backgroundColor": "#343a40" if row['Type'] == "🚛 Pełny Transport" else "#adb5bd",
                "borderColor": "#212529"
            })

    calendar(events=events, options={
        "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,listWeek"},
        "initialView": "dayGridMonth",
        "firstDay": 1,
        "locale": "pl",
        "height": "650px"
    }, key="sqm_calendar")

    with st.expander("🗑️ Usuwanie wpisów"):
        if not df.empty:
            to_del = st.selectbox("Wybierz wpis do usunięcia", df.index, 
                                 format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:30]}")
            if st.button("POTWIERDŹ USUNIĘCIE"):
                df = df.drop(to_del)
                save_data(df)
                st.rerun()

# --- DOLNY PANEL: PODGLĄD DANYCH ---
st.markdown("---")
with st.expander("🔍 Pełny podgląd bazy danych (Google Sheets)"):
    # Obliczamy sumę LDM na dzień dla podglądu
    daily_sum = df.groupby('Date')['LDM'].sum().reset_index()
    st.write("**Podsumowanie zajętości LDM wg dni:**")
    st.dataframe(daily_sum, hide_index=True)
    st.write("**Wszystkie wpisy:**")
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
