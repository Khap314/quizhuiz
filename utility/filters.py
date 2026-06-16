import streamlit as st
import pandas as pd

def render_filters(df, key_prefix="global"):
    col1, col2, col3, col4 = st.columns(4)
    
    # Типы игры
    with col1:
        total_all = len(df)
        game_types_with_count = [f"Все типы ({total_all})"]
        counts_type = df['gameType'].value_counts()
        for g_type, count in counts_type.items():
            game_types_with_count.append(f"{g_type} ({count})")
            
        selected_display_type = st.selectbox("Тип игры:", game_types_with_count, key=f"{key_prefix}_game_type")
        selected_type = selected_display_type.split(" (")[0]

    # Бары
    with col2:
        bars = ["Все бары"] + list(df['bar'].dropna().unique())
        selected_bar = st.selectbox("Бар:", bars, key=f"{key_prefix}_bar")
        
    # Даты
    with col3:
        min_date = df['date'].min().date()
        max_date = df['date'].max().date()
        
        sub_date_col1, sub_date_col2 = st.columns(2)
        with sub_date_col1:
            start_date = st.date_input(
                "Дата с:",
                value=min_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key_prefix}_start_date"
            )
        with sub_date_col2:
            end_date = st.date_input(
                "по:",
                value=max_date,
                min_value=min_date,
                max_value=max_date,
                key=f"{key_prefix}_end_date"
            )
    # Занятое место
    with col4:
        min_place = 1
        max_place = int(df['placing'].max())
        
        sub_place_col1, sub_place_col2 = st.columns(2)
        with sub_place_col1:
            best_place = st.number_input(
                "Место с:", 
                min_value=min_place, 
                max_value=max_place, 
                value=min_place,
                step=1,
                key=f"{key_prefix}_best_place"
            )
        with sub_place_col2:
            worst_place = st.number_input(
                "по:", 
                min_value=min_place, 
                max_value=max_place, 
                value=max_place,
                step=1,
                key=f"{key_prefix}_worst_place"
            )
    # Фильтруем последовательно
    df_filtered = df.copy()
    
    if selected_type != "Все типы":
        df_filtered = df_filtered[df_filtered['gameType'] == selected_type]
        
    if selected_bar != "Все бары":
        df_filtered = df_filtered[df_filtered['bar'] == selected_bar]

    df_filtered = df_filtered[
        (df_filtered["date"].dt.date >= start_date)
        & (df_filtered["date"].dt.date <= end_date)
    ]
    
    df_filtered = df_filtered[
        (df_filtered['placing'] >= best_place) & 
        (df_filtered['placing'] <= worst_place)
    ]

    # Возвращаем один готовый отфильтрованный датафрейм
    return df_filtered
