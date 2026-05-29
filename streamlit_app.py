# -*- coding: utf-8 -*-
"""
Created on Tue May 26 16:35:39 2026

@author: khapaev.m
"""

import sqlite3
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path

# Настройка страницы сайта
st.set_page_config(
    page_title = "Квиз, хуиз! Статистика",
    layout = "wide",
    page_icon = "data/sticker.webp"
  )
st.title("🧠 Гиганты мысли")
st.markdown("---")

# Авторизация
login_container = st.empty()
with login_container.container():
    password = st.text_input("Введите пароль:", type="password")
    if password != "quizhuiz":
        st.error("Неверный пароль!")
        st.stop()
    else:
        login_container.empty()
# Подключаемся к БД
if not (Path(__file__).resolve().parent/"quiz.db").is_file():
    st.error("Не найден файл БД!")
    st.stop()
else:
    conn = "data/quiz.db")
    df_games = pd.read_sql_query("SELECT * FROM games ORDER BY date(date)", conn)
    if df_games.empty:
        st.info("Не найдены данные в базе!")
        st.stop()
    df_games["date"] = pd.to_datetime(df_games["date"])
    conn.close()
    
# Sidebar
st.sidebar.header("📍 Навигация")
st.sidebar.markdown("---")
st.sidebar.markdown("""
- [ℹ️ Главные метрики](#glavnye-metriki)
- [📈 Динамика результатов](#dinamika-rezultatov)
- [🎯 Эффективность по раундам](#effektivnost-po-raundam)
- [🎭 Результаты по типам игр](#rezultaty-po-tipam-igr)
- [🍻 Где мы чаще всего играем?](#gde-my-chasche-vsego-igraem)
- [📋 Все игры (сводная таблица)](#vse-igry-svodnaya-tablitsa)
""", unsafe_allow_html=True)

# ==========================================
# БЛОК 1: Главные метрики (Key Metrics)
# ==========================================
st.subheader("ℹ️ Главные метрики")
total_games = len(df_games)
avg_place = int(round(df_games["placing"].mean(), 1))
last_game = df_games["date"].max().strftime("%Y-%m-%d")
total_spent = df_games["price"].str[:3].astype(int).sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Всего сыграно игр", total_games)
col2.metric("Среднее место", avg_place)
col3.metric("Последняя игра", last_game)
col4.metric("Потрачено на игры (руб)", f"{total_spent} ₽")
st.markdown("---")

# ==========================================
# БЛОК 2: Динамика результатов
# ==========================================
st.subheader("📈 Динамика результатов")
fig_timeline = px.line(
    df_games.sort_values("date"),
    x="date",
    y="placing",
    hover_data=["gameName", "bar", "summary"],
    markers=True,
    title="Динамика занятых мест от игры к игре",
    labels={"date": "Дата", "placing": "Занятое место"},
)
# Разворачиваем ось Y, чтобы 1-е место было на самом верху графика
fig_timeline.update_yaxes(autorange="reversed")
st.plotly_chart(fig_timeline, use_container_width=True)
st.markdown("---")

# ==========================================
# БЛОК 3: Аналитика по раундам и типам игр
# ==========================================
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🎯 Эффективность по раундам")
    # Считаем средний балл за каждый раунд
    round_cols = [
        "round1",
        "round2",
        "round3",
        "round4",
        "round5",
        "round6",
        "round7",
    ]
    avg_rounds = df_games[round_cols].mean().reset_index()
    avg_rounds.columns = ["Раунд", "Средний балл"]
    avg_rounds["Раунд"] = avg_rounds["Раунд"].str.replace(
        "round", "Раунд "
    )  # красивое имя

    fig_rounds = px.bar(
        avg_rounds,
        x="Раунд",
        y="Средний балл",
        color="Средний балл",
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig_rounds, use_container_width=True)

with right_col:
    st.subheader("🎭 Результаты по типам игр")
    # Считаем среднее место команды в зависимости от тематики
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
    st.plotly_chart(fig_types, use_container_width=True)

st.markdown("---")

# ==========================================
# БЛОК 4: Любимые бары / локации
# ==========================================
st.subheader("🍻 Где мы чаще всего играем?")
df_bars = df_games["bar"].value_counts().reset_index()
df_bars.columns = ["Локация", "Количество игр"]

fig_bars = px.pie(
    df_bars, values="Количество игр", names="Локация", hole=0.4
)
st.plotly_chart(fig_bars, use_container_width=True)

# ==========================================
# БЛОК 5: Таблица с поиском
# ==========================================
st.subheader("📋 Все игры (сводная таблица)")
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
        ]
    ].sort_values("date", ascending=False),
    use_container_width=True, 
    column_config=
        {
            "date": "Дата",
            "gameName": "Название",
            "gameType": "Тип игры",
            "bar": "Бар",
            "placing": "Занятое место",
            "teamNumber": "Количество команд",
            "summary": "Результат (баллов)"
        }
)
