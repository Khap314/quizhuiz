import streamlit as st
import plotly.express as px

# ==========================================
# Занятое место по отношению к числу команд
# ==========================================
st.title("📊 Занятое место по отношению к числу команд")

df_games = st.session_state["df_games"]
df_games['percentile'] = (df_games['teamNumber'] - df_games['placing']) / (df_games['teamNumber'] - 1) * 100

fig_place_to_teamNum = px.line(
    df_games.sort_values("date"),
    x="date",
    y="percentile",
    hover_data=["teamNumber", "placing", "date"],
    markers=True,
    title="Занятое место по отношению к числу команд",
    labels={"date": "Дата", "percentile": "Процентиль"},
)

st.plotly_chart(fig_place_to_teamNum, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})