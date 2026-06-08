from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st
from app.database import fetch_events
from app.classifier import analyst_alert

st.set_page_config(page_title="LATAM OSINT Monitor", layout="wide")
st.title("LATAM OSINT Monitor — MVP")
st.caption("Monitoreo inicial desde periódicos, RSS y GDELT. Requiere revisión analítica humana.")

rows = [dict(r) for r in fetch_events(1000)]
if not rows:
    st.warning("No hay eventos todavía. Ejecuta: python scripts/ingest.py")
    st.stop()

df = pd.DataFrame(rows)

with st.sidebar:
    st.header("Filtros")
    countries = sorted([c for c in df["country"].dropna().unique()])
    types = sorted([t for t in df["event_type"].dropna().unique()])
    severities = ["critical", "high", "medium", "low"]
    selected_countries = st.multiselect("País", countries, default=countries)
    selected_types = st.multiselect("Tipo", types, default=types)
    selected_severities = st.multiselect("Severidad", severities, default=severities)

filtered = df[
    df["country"].isin(selected_countries)
    & df["event_type"].isin(selected_types)
    & df["severity"].isin(selected_severities)
].copy()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Eventos", len(filtered))
col2.metric("Alta/Crítica", len(filtered[filtered["severity"].isin(["high", "critical"])]))
col3.metric("Países", filtered["country"].nunique())
col4.metric("Fuentes", filtered["source_name"].nunique())

st.subheader("Eventos recientes")
show_cols = ["published_at", "severity", "country", "event_type", "title", "source_name", "url"]
st.dataframe(filtered[show_cols].sort_values("published_at", ascending=False), use_container_width=True, hide_index=True)

st.subheader("Alerta analítica")
selected_title = st.selectbox("Selecciona un evento", filtered["title"].tolist())
selected = filtered[filtered["title"] == selected_title].iloc[0].to_dict()
st.text_area("Borrador de alerta", analyst_alert(selected), height=320)

st.subheader("Distribución")
left, right = st.columns(2)
with left:
    st.bar_chart(filtered["event_type"].value_counts())
with right:
    st.bar_chart(filtered["severity"].value_counts())
