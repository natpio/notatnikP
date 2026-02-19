import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_calendar import calendar
import pandas as pd
import uuid
import plotly.express as px
from datetime import datetime, timedelta

# --- SETTINGS ---
st.set_page_config(page_title="SQM Logistics Hub", page_icon="🚀", layout="wide")

# --- CUSTOM CSS: DARK COUNTRY MODERN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syncopate:wght@400;700&family=Inter:wght@300;600&display=swap');

    .stApp { background-color: #1a1a1a; color: #e0e0e0; }
    
    /* Panele operacyjne */
    div[data-testid="stVerticalBlock"] > div.stVerticalBlock {
        background-color: #262626;
        padding: 25px;
        border-radius: 20px;
        border: 1px solid #3d3d3d;
    }

    /* Nagłówek futurystyczny */
    .logo-text {
        font-family: 'Syncopate', sans-serif;
        font-size: 2.5rem;
        background: linear-gradient(90deg, #d4af37, #8d6e63);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }

    /* Customowe metryki */
    .metric-box {
        background: #333333;
        border-bottom: 4px solid #d4af37;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }

    /* Kalendarz w trybie Dark */
    .fc { background: #262626 !important; color: white !important; border: none !important; }
    .fc-daygrid-day:hover { background: #333333 !important; }
    .fc-toolbar-title { color: #d4af37 !important; font-family: 'Syncopate'; }
</style>
""", unsafe_allow_html=True)

# --- DATA ENGINE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    df = conn.read(ttl="0s")
    # Zabezpieczenie kolumn
    cols = ["Date", "Note", "Type", "LDM", "Priority", "ID"]
    for col in cols:
        if col not in df.columns: df[col] = 0 if col == "LDM" else ""
    return df

def save_data(df):
    conn.update(data=df)
    st.cache_data.clear()

df = get_data()

# --- TOP BAR: HUB OVERVIEW ---
st.markdown('<p class="logo-text">SQM LOGISTICS HUB</p>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="metric-box"><small>STATUS FLOTY</small><h2>AKTYWNA</h2></div>', unsafe_allow_html=True)
with m2:
    today_ldm = df[df['Date'] == datetime.now().strftime("%Y-%m-%d")]['LDM'].astype(float).sum()
    st.markdown(f'<div class="metric-box"><small>WYKORZYSTANIE LDM (DZIŚ)</small><h2>{today_ldm} / 13.6</h2></div>', unsafe_allow_html=True)
with m3:
    pending = len(df[df['Date'] >= datetime.now().strftime("%Y-%m-%d")])
    st.markdown(f'<div class="metric-box"><small>OPERACJE W TOKU</small><h2>{pending}</h2></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-box"><small>POZIOM ALARMÓW</small><h2 style="color:#d4af37">NISKI</h2></div>', unsafe_allow_html=True)

st.write("---")

# --- MAIN SECTION: TRÓJPODZIAŁ ---
col_sidebar, col_mid, col_chart = st.columns([1, 2, 1])

# 1. KONTROLA (LEWA)
with col_sidebar:
    st.subheader("🛠️ KONSOLA WPISÓW")
    with st.form("hub_form"):
        date = st.date_input("Data operacji")
        op_type = st.selectbox("Typ", ["🚛 Pełny Transport", "📦 Doładunek", "⏱️ Slot Rozładunkowy", "🛠️ Przegląd"])
        ldm = st.number_input("Zajętość naczepy (LDM)", min_value=0.0, max_value=13.6, step=0.4)
        note = st.text_area("Szczegóły / Nr Naczepy")
        prio = st.select_slider("Priorytet", options=["Standard", "KRYTYCZNY"])
        
        if st.form_submit_button("AUTORYZUJ I ZAPISZ"):
            new_data = pd.DataFrame([{"Date": str(date), "Note": note, "Type": op_type, "LDM": ldm, "Priority": prio, "ID": str(uuid.uuid4())}])
            df = pd.concat([df, new_data], ignore_index=True)
            save_data(df)
            st.rerun()

    if not df.empty:
        st.subheader("🗑️ USUWANIE")
        to_del = st.selectbox("Wybierz wpis", df.index, format_func=lambda x: f"{df.at[x,'Date']} - {df.at[x,'Note'][:15]}")
        if st.button("USUŃ Z BAZY"):
            df = df.drop(to_del)
            save_data(df)
            st.rerun()

# 2. WIZUALIZACJA (ŚRODEK)
with col_mid:
    st.subheader("📅 HARMONOGRAM OPERACYJNY")
    events = []
    for _, row in df.iterrows():
        if len(str(row['Date'])) >= 10:
            events.append({
                "title": f"{row['Type']} ({row['LDM']} LDM)",
                "start": str(row['Date']),
                "color": "#d4af37" if row['Priority'] == "KRYTYCZNY" else "#5d4037",
                "allDay": True
            })
    
    calendar(events=events, options={
        "initialView": "dayGridMonth",
        "headerToolbar": {"left": "prev,next", "center": "title", "right": "dayGridMonth,listWeek"},
        "locale": "pl", "height": "600px"
    }, key="hub_cal")

# 3. ANALITYKA (PRAWA)
with col_chart:
    st.subheader("📈 OBCIĄŻENIE LOGISTYKI")
    if not df.empty:
        # Wykres ilości typów transportów
        fig = px.pie(df, names='Type', hole=.4, color_discrete_sequence=['#d4af37', '#8d6e63', '#3d3d3d', '#5d4037'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Wykres LDM w czasie
        st.write("**Planowane zajęcie naczep (LDM):**")
        df_chart = df.groupby('Date')['LDM'].sum().reset_index()
        fig2 = px.bar(df_chart.tail(7), x='Date', y='LDM', color_discrete_sequence=['#d4af37'])
        fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig2, use_container_width=True)

# --- DATA TABLE ---
with st.expander("📄 ARCHIWUM DANYCH"):
    st.dataframe(df.sort_values('Date', ascending=False), use_container_width=True)
