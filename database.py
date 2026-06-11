from pathlib import Path
from sqlalchemy import create_engine
import pandas as pd
import streamlit as st

@st.cache_data
def get_data_from_db():
    db_path = Path("data/quiz.db")
    #db_path = Path("C:/Users/Max/Documents/giganti_mysli/data/quiz.db")
    
    if not db_path.is_file():
        return "NO_FILE", None
        
    engine = create_engine(f"sqlite:///{db_path}")
    #engine = create_engine("sqlite:///C:/Users/Max/Documents/giganti_mysli/data//quiz.db")
    df = pd.read_sql_query("SELECT * FROM games ORDER BY date(date)", con=engine)
    
    if df.empty:
        return "EMPTY_DB", None
        
    df['date'] = pd.to_datetime(df['date'])
    df['day_num'] = df['date'].dt.dayofweek
    ru_days = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}
    df['day_name'] = df['day_num'].map(ru_days)
    return "OK", df
