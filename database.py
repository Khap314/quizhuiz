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
    #df['day_name'] = df['date'].dt.day_name(locale='rus_rus')
    df['day_name'] = df['date'].dt.day_name(locale='ru_RU.UTF-8')
    return "OK", df
