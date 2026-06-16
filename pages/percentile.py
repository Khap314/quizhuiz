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

fig_place_to_teamNum.update_layout(
    height=400, 
    margin=dict(l=20, r=20, t=40, b=20),
    dragmode=False, 
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True)
)

st.plotly_chart(fig_place_to_teamNum, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})
