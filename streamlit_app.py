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
from sqlalchemy import create_engine

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
if not Path("data/quiz.db").is_file():
    st.error("Не найден файл БД!")
    st.stop()
else:
    engine = create_engine("sqlite:///data/quiz.db")
    df_games = pd.read_sql_query("SELECT * FROM games ORDER BY date(date)", con=engine)
    if df_games.empty:
        st.info("Не найдены данные в базе!")
        st.stop()
    df_games["date"] = pd.to_datetime(df_games["date"])
    
# Sidebar
st.sidebar.header("📍 Навигация")
st.sidebar.markdown("---")
st.sidebar.markdown("""
- [ℹ️ Главные метрики](#glavnye-metriki)
- [📈 Динамика результатов](#dinamika-rezultatov)
- [📈 Занятое место по отношению к числу команд](#zanyatoe-mesto-po-otnosheniyu-k-chislu-komand)
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
last_game = df_games["date"].max().strftime("%Y.%m.%d")
total_spent = df_games["price"].sum()

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
# БЛОК 3: Занятое место по отношению к числу команд
# ==========================================
st.subheader("📈 Занятое место по отношению к числу команд")
chart_df = df_games.copy()
# Вычисляем отношение (индекс места)
chart_df['place_ratio'] = chart_df['placing'] / chart_df['teamNumber'] * 100

fig_place_to_teamNum = px.line(
    chart_df.sort_values("date"),
    x="date",
    y="place_ratio",
    hover_data=["teamNumber", "placing", "date"],
    markers=True,
    title="Занятое место по отношению к числу команд",
    labels={"date": "Дата", "place_ratio": "Отношение места к кол-ву команд"},
)
fig_place_to_teamNum.update_yaxes(autorange="reversed")
st.plotly_chart(fig_place_to_teamNum, use_container_width=True)
st.markdown("---")

# ==========================================
# БЛОК 4: Аналитика по раундам и типам игр
# ==========================================
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("🎯 Эффективность по раундам (в % от максимума)")
    # Максимальные баллы для всех типов игр
    max_scores = {
        "Классические игры": {
            "old": {"round1": 6, "round2": 6, "round3": 6, "round4": 12, "round5": 6, "round6": 6, "round7": 21},
            "new": {"round1": 8, "round2": 8, "round3": 6, "round4": 9, "round5": 6, "round6": 8, "round7": 24}
        },
        "Квиз-плиз!": {
            "old": {"round1": 8, "round2": 8, "round3": 7, "round4": 12, "round5": 6, "round6": 8, "round7": 24},
            "new": {"round1": 8, "round2": 8, "round3": 6, "round4": 12, "round5": 6, "round6": 8, "round7": 24}
        },
        "Хардкор": {
            "old": {"round1": 8, "round2": 8, "round3": 7, "round4": 12, "round5": 6, "round6": 8, "round7": 24},
            "new": {"round1": 8, "round2": 8, "round3": 6, "round4": 12, "round5": 6, "round6": 8, "round7": 24}
        }
    }
    
    # Дата изменения правил (Х). Приводим к типу date для сравнения
    change_date = pd.to_datetime("2025-03-25").date() 
    
    # 2. Выбор типа игры
    game_types = list(df_games["gameType"].unique())
    selected_type = st.selectbox("Выберите тип игры:", game_types)
    
    # 3. Фильтрация данных по типу и приведение даты к нужному типу
    df_filtered = df_games[df_games["gameType"] == selected_type].copy()
    # Убедимся, что колонка даты в вашем df_games имеет тип datetime/date
    df_filtered["date"] = pd.to_datetime(df_filtered["date"]).dt.date
    
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
    
    # Извлекаем два набора правил для выбранной игры
    old_rules = max_scores[selected_type]["old"]
    new_rules = max_scores[selected_type]["new"]
    
    # Функция для нормировки одной строки (одной игры)
    def normalize_row(row):
        # Выбираем нужный набор максимумов в зависимости от даты игры
        rules = old_rules if row["date"] < change_date else new_rules
        
        # Делим каждый раунд на его исторический максимум
        for r_col in round_cols:
            max_val = rules[r_col]
            # Записываем процент эффективности прямо в строку
            row[f"{r_col}_pct"] = (row[r_col] / max_val) * 100
        return row
        
    # 5. АГРЕГАЦИЯ: Теперь считаем среднее по уже отнормированным процентам!
    pct_cols = [f"{col}_pct" for col in round_cols]
    
    # Применяем функцию нормировки к каждой игре
    df_normalized = df_filtered.apply(normalize_row, axis=1)
    
    # Считаем средний процент для каждого раунда
    avg_pct = df_normalized[pct_cols].mean().reset_index()
    avg_pct.columns = ["Раунд", "Эффективность (%)"]
    avg_pct["Раунд"] = avg_pct["Раунд"].str.replace("_pct", "").str.replace("round", "Раунд ")

    # Также посчитаем чистый средний балл (исключительно для красивой подсказки)
    avg_scores = df_normalized[round_cols].mean().reset_index()
    avg_pct["Средний балл"] = avg_scores[0]

    # 6. Отрисовка графика
    fig_rounds = px.bar(
        avg_pct,
        x="Раунд",
        y="Эффективность (%)",
        color="Эффективность (%)",
        color_continuous_scale="Viridis",
        range_y=[0, 100]
    )
    
    fig_rounds.update_traces(
        hovertemplate="<b>%{x}</b><br>Эффективность: %{y:.1f}%<br>Ср. балл за все время: %{customdata:.2f}<extra></extra>",
        customdata=avg_pct["Intermediate_score"] if "Intermediate_score" in avg_pct else avg_pct["Средний балл"]
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
# БЛОК 5: Любимые бары / локации
# ==========================================
st.subheader("🍻 Где мы чаще всего играем?")
df_bars = df_games["bar"].value_counts().reset_index()
df_bars.columns = ["Локация", "Количество игр"]

fig_bars = px.pie(
    df_bars, values="Количество игр", names="Локация", hole=0.4
)
st.plotly_chart(fig_bars, use_container_width=True)

# ==========================================
# БЛОК 6: Таблица с поиском
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
            "round1",
            "round2",
            "round3",
            "round4",
            "round5",
            "round6",
            "round7",
            "extid"
        ]
    ].sort_values("date", ascending=False),
    use_container_width=True, 
    column_config=
        {
            "date": st.column_config.DatetimeColumn("Дата", format="DD.MM.YYYY HH:mm"),
            "gameName": "Название",
            "gameType": "Тип игры",
            "bar": "Бар",
            "placing": "Занятое место",
            "teamNumber": "Количество команд",
            "summary": "Результат (баллов)"
        }
)
