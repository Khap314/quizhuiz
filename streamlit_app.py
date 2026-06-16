import pandas as pd
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as graph_objects
from database import get_data_from_db
from filters import render_filters

# ==========================================
# Настройка страницы сайта
# ==========================================
st.set_page_config(
    page_title = "Квиз, хуиз! Статистика",
    layout = "wide",
    page_icon = "data/sticker.webp"
    #page_icon = "C:/Users/khapaev.m/Documents/giganti_mysli/data/sticker.webp"
  )
st.title("🧠 Гиганты мысли")
st.markdown("---")

# ==========================================
# Авторизация
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
login_container = st.empty()

if not st.session_state["logged_in"]:
    login_container = st.empty()
    
    with login_container.container():
        st.subheader("Авторизация")
        # Обертываем ввод в форму, чтобы кнопка и текстовое поле работали вместе
        with st.form("login_form"):
            password = st.text_input("Введите пароль:", type="password")
            col1, col2 = st.columns([4, 1])
            with col2:
                submit_button = st.form_submit_button("Войти", width='stretch')
            
            # Логика проверяется ТОЛЬКО после нажатия кнопки или Enter
            if submit_button:
                if password == "quizhuiz":
                    st.session_state["logged_in"] = True
                    login_container.empty()  # Полностью убираем форму с экрана
                    st.rerun()               # Перезапускаем скрипт уже как для авторизованного
                else:
                    st.error("❌ Неверный пароль!")
                    
        # Останавливаем выполнение остальной части скрипта, пока не войдем
        st.stop()
            
# ==========================================
# Подключение к БД
# ==========================================
status, data_result = get_data_from_db()

if status == "NO_FILE":
    st.error("Не найден файл БД!")
    st.stop()
elif status == "EMPTY_DB":
    st.info("Не найдены данные в базе!")
    st.stop()
else:
    df_games = data_result
    
# ==========================================
# Sidebar
# ==========================================
# Шрифты
st.markdown("""
    <style>
    /* Базовые настройки для мобильных экранов (ширина до 768px) */
    @media (max-width: 768px) {
        /* Уменьшаем главные заголовки (st.title) */
        .stMarkdown h1 {
            font-size: 1.8rem !important;
        }
        /* Уменьшаем подзаголовки (st.header / st.subheader) */
        .stMarkdown h2, .stMarkdown h3 {
            font-size: 1.3rem !important;
        }
        /* Уменьшаем обычный текст и подписи к виджетам */
        .stMarkdown p, label {
            font-size: 0.9rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.header("📍 Навигация")
st.sidebar.markdown("""
- [ℹ️ Главные метрики](#glavnye-metriki-po-vsem-igram)
- [📈 Динамика результатов](#dinamika-rezultatov)
- [📈 Занятое место по отношению к числу команд](#zanyatoe-mesto-po-otnosheniyu-k-chislu-komand)
- [🎯 Эффективность по раундам](#effektivnost-po-raundam-v-ot-maksimuma)
- [🎭 Результаты по типам игр](#rezultaty-po-tipam-igr)
- [🍻 Где мы чаще всего играем?](#gde-my-chasche-vsego-igraem)
- [🗓️ Статистика по дням недели](#statistika-po-dnyam-nedeli)
- [📋 Все игры (сводная таблица)](#vse-igry-svodnaya-tablitsa)
""", unsafe_allow_html=True)

# ==========================================
# Конфиг для графиков
# ==========================================
plotConfig = {
    'scrollZoom': False,      # Отключает зум колесиком мыши / щипком
    #'displayModeBar': False   # Прячет верхнюю панель инструментов, которая наползает на мобильных
}

# ==========================================
# БЛОК 1: Главные метрики (Key Metrics)
# ==========================================
st.subheader("ℹ️ Главные метрики по всем играм")
total_games = len(df_games)
top_10_count = (df_games['placing'] <= 10).sum()
top_5_count = (df_games['placing'] <= 5).sum()
last_game = df_games["date"].max().strftime("%d.%m.%Y")
avg_place = int(round(df_games["placing"].mean(), 1))
total_spent = df_games["price"].sum()

col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Всего сыграно игр", total_games)
col2.metric("Попаданий в топ 10", top_10_count)
col3.metric("Попаданий в топ 5", top_5_count)
col4.metric("Последняя игра", last_game)
col5.metric("Среднее место во всех играх", avg_place)
col6.metric("Потрачено на игры (руб) (пока на одного человека)", f"{total_spent} ₽")
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
fig_timeline.update_layout(
    height=400, 
    margin=dict(l=20, r=20, t=40, b=20) # Уменьшаем отступы по бокам для экономии места
)
st.plotly_chart(fig_timeline, width='stretch', config=plotConfig)
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
st.plotly_chart(fig_place_to_teamNum, width='stretch', config=plotConfig)
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
    
    st.plotly_chart(fig_rounds, width='stretch', config=plotConfig)

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
    st.plotly_chart(fig_types, width='stretch', config=plotConfig)

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
st.plotly_chart(fig_bars, width='stretch', config=plotConfig)

# ==========================================
# БЛОК 6: Статистика по дням недели
# ==========================================
st.subheader("🗓️ Статистика по дням недели")

df_filtered = render_filters(df_games)
df_days = (
    df_filtered.groupby(["day_num", "day_name"])["placing"]
    .agg(avg_place="mean", total_games="count")
    .reset_index()
)
df_days = df_days.sort_values('day_num')

if not df_days.empty and df_days["total_games"].sum() > 0:
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Добавляем СТОЛБЦЫ для общего количества игр (левая ось Y)
    fig.add_trace(
        graph_objects.Bar(
            x=df_days["day_name"],
            y=df_days["total_games"],
            text=df_days["total_games"],  # Указываем, какой текст выводить на столбцах
            textposition="auto",  # Автоматически размещает текст (внутри или снаружи)
            textfont=dict(
                size=12, color="white"
            ),  # Делаем шрифт белым и четким для темной темы
            name="Количество игр",
            marker_color="rgba(46, 117, 182, 0.6)",  # Полупрозрачный синий
        ),
        secondary_y=False,
    )
    
    # Добавляем ЛИНИЮ для среднего балла (правая ось Y)
    fig.add_trace(
        graph_objects.Scatter(
            x=df_days["day_name"],
            y=df_days["avg_place"],
            text=df_days["avg_place"].round(0),  # Указываем, какой текст выводить на столбцах
            textposition="top center",
            name="Среднее место (выше = лучше)",
            mode="lines+markers+text",
            line=dict(color="#FF4B4B", width=3),  # Красная линия
        ),
        secondary_y=True,
    )
    
    # Настраиваем подписи осей и внешний вид
    fig.update_layout(
        title_text="Количество игр и среднее занятое место по дням недели",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    
    fig.update_yaxes(title_text="<b>Всего игр</b> (столбцы)", secondary_y=False)
    fig.update_yaxes(title_text="<b>Среднее место</b> (линия, 1-е место вверху)", secondary_y=True, autorange="reversed",)
    
    # Отображаем график в Streamlit
    st.plotly_chart(fig, width='stretch', config=plotConfig)
else:
    st.info("Нет данных по дням недели для выбранного фильтра 🤷‍♂️")

st.markdown("---")

# ==========================================
# БЛОК 7: Таблица с поиском
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
