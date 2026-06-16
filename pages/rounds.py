import plotly.express as px
import streamlit as st
import pandas as pd

# ==========================================
# Аналитика по раундам и типам игр
# ==========================================
st.title("🎯 Эффективность по раундам (в % от максимума)")

df_games = st.session_state["df_games"]

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

st.plotly_chart(fig_rounds, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})