import plotly.express as px
import streamlit as st

st.title("🎭 Результаты по типам игр")

df_games = st.session_state["df_games"]
df_types = (
    df_games.groupby("gameType")["placing"]
    .mean()
    .reset_index()
    .sort_values("placing")
)
df_types.columns = ["Тип игры", "Среднее место"]

fig_types = px.bar(
    df_types,
    x="Тип игры",
    y="Среднее место",
    title="В каких играх мы сильнее? (Меньше столбец = лучше место)",
)
st.plotly_chart(fig_types, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})