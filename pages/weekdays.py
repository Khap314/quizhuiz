import streamlit as st
import plotly.graph_objects as graph_objects
from plotly.subplots import make_subplots
from utility.filters import render_filters


# ==========================================
# Статистика по дням недели
# ==========================================
st.title("🗓️ Статистика по дням недели")

df_games = st.session_state["df_games"]
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
    st.plotly_chart(fig, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})
else:
    st.info("Нет данных по дням недели для выбранного фильтра 🤷‍♂️")