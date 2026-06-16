import streamlit as st
import plotly.express as px

# ==========================================
# Любимые бары / локации
# ==========================================
st.title("🍻 Где мы чаще всего играем?")

df_games = st.session_state["df_games"]
df_bars = df_games["bar"].value_counts().reset_index()
df_bars.columns = ["Локация", "Количество игр"]

fig_bars = px.pie(
    df_bars, values="Количество игр", names="Локация", hole=0.4
)

fig_bars.update_layout(
    # --- НАСТРОЙКА АДАПТИВНОЙ ЛЕГЕНДЫ ---
    legend=dict(
        orientation="h",     # Делаем легенду горизонтальной
        yanchor="top",       # Привязываем верхнюю границу легенды
        y=-0.1,              # Уводим её вниз ПОД график (значение меньше 0)
        xanchor="center",    # Центрируем по горизонтали
        x=0.5                # Смещаем ровно на середину экрана
    ),
    
    # Отключаем зум
    dragmode=False,
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True),
    margin=dict(l=10, r=10, t=50, b=10)
)

st.plotly_chart(fig_bars, width='stretch', config={'scrollZoom': False, 'displayModeBar': False})