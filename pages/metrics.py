import streamlit as st
# ==========================================
# Главные метрики (Key Metrics)
# ==========================================
st.title("ℹ️ Главные метрики по всем играм")

df_games = st.session_state["df_games"]

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Всего сыграно игр", len(df_games))
col2.metric("Попаданий в топ 10", (df_games['placing'] <= 10).sum())
col3.metric("Попаданий в топ 5", (df_games['placing'] <= 5).sum())
col4.metric("Последняя игра", df_games["date"].max().strftime("%d.%m.%Y"))
col5.metric("Среднее место во всех играх", int(round(df_games["placing"].mean(), 1)))
col6.metric("Потрачено на игры (руб) (пока на одного человека)", f"{df_games["price"].sum()} ₽")
