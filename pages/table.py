import streamlit as st

# ==========================================
# Таблица с поиском
# ==========================================
st.title("📋 Все игры (сводная таблица)")

df_games = st.session_state["df_games"]

st.dataframe(
    df_games[
        [
            "date",
            "gameName",
            "gameType",
            "bar",
            "placing",
            "teamNumber",
            "summary",
            "round1",
            "round2",
            "round3",
            "round4",
            "round5",
            "round6",
            "round7",
        ]
    ].sort_values("date", ascending=False),
    width='stretch', 
    column_config=
        {
            "date": st.column_config.DatetimeColumn("Дата", format="DD.MM.YYYY HH:mm"),
            "gameName": "Название",
            "gameType": "Тип игры",
            "bar": "Бар",
            "placing": "Занятое место",
            "teamNumber": "Количество команд",
            "summary": "Результат (баллов)",
            "round1": "Раунд 1",
            "round2": "Раунд 2",
            "round3": "Раунд 3",
            "round4": "Раунд 4",
            "round5": "Раунд 5",
            "round6": "Раунд 6",
            "round7": "Раунд 7"
        }
)