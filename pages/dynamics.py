import streamlit as st
import plotly.express as px

plotConfig = {
    'scrollZoom': False,      # Отключает зум колесиком мыши / щипком
    'displayModeBar': False   # Прячет верхнюю панель инструментов, которая наползает на мобильных
}

# ==========================================
# Динамика результатов
# ==========================================
st.title("📈 Динамика результатов")

df_games = st.session_state["df_games"]
df_games['mean_placing'] = df_games['placing'].rolling(window=15, min_periods=1).mean()

fig_timeline = px.line(
    df_games.sort_values("date"),
    x="date",
    y="mean_placing",
    hover_data=["gameName", "bar", "summary"],
    markers=True,
    title="Динамика занятых мест от игры к игре",
    labels={"date": "Дата", "mean_placing": "Занятое место"},
)

fig_timeline.update_yaxes(autorange="reversed")

fig_timeline.update_layout(
    height=400, 
    margin=dict(l=20, r=20, t=40, b=20),
    dragmode=False, 
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True)
)

st.plotly_chart(fig_timeline, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})