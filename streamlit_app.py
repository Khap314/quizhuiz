import streamlit as st
from utility.database import get_data_from_db

# ==========================================
# Настройка главной страницы
# ==========================================
st.set_page_config(
    page_title = "Квиз, хуиз! Статистика",
    layout = "wide",
    page_icon = "data/sticker.webp"
  )
  
# ==========================================
# Шрифты
# ==========================================
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

st.title("🧠 Гиганты мысли")
st.markdown("---")

# ==========================================
# Страницы сайта
# ==========================================
page_metrics = st.Page("pages/metrics.py", title="Главные метрики", icon="ℹ️")
page_dynamics = st.Page("pages/dynamics.py", title="Динамика результатов", icon="📈")
page_percentile = st.Page("pages/percentile.py", title="Занятое место по отношению к числу команд", icon="📊")
page_bars = st.Page("pages/bars.py", title="Где мы чаще всего играем?", icon="🍻")
page_weekdays = st.Page("pages/weekdays.py", title="Статистика по дням недели", icon="🗓")
page_gametypes = st.Page("pages/gameTypes.py", title="Результаты по типам игр", icon="🎭")
page_rounds = st.Page("pages/rounds.py", title="Эффективность по раундам (в % от максимума)", icon="🎯")
page_table = st.Page("pages/table.py", title="Все игры (сводная таблица)", icon="📋")
page_photos = st.Page("pages/photo.py", title="Фото с игр", icon="📸")

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
        with st.form("login_form"):
            password = st.text_input("Введите пароль:", type="password")
            col1, col2 = st.columns([4, 1])
            with col2:
                submit_button = st.form_submit_button("Войти", width='stretch')
            
            if submit_button:
                if password == "quizhuiz":
                    st.session_state["logged_in"] = True
                    login_container.empty()
                    st.rerun()
                else:
                    st.error("❌ Неверный пароль!")
                    
else:
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
        st.session_state["df_games"] = data_result
# ==========================================
# Навигация и запуск 
# ==========================================
    mainPage = st.navigation([page_metrics, page_dynamics, page_percentile, page_bars, page_weekdays, page_gametypes, page_rounds, page_table, page_photos])
    mainPage.run()
