import streamlit as st
import pandas as pd
from datetime import datetime

with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/heart-report-2020-08-31-2020-09-30.csv','rb') as f:
    df2 = pd.read_csv(f, parse_dates=True)




df2.index = pd.to_datetime(df2.date.map(lambda x: x.strip("'")))


st.sidebar.slider('Select range',value = (datetime(2020, 10, 1, 9, 30),datetime(2020, 11, 1, 9, 30)),format="MM/DD/YY - hh:mm")
options = st.sidebar.multiselect('select heart rate options',['resting','minimum','maximum'],default = ['resting'])


st.line_chart(df2.loc[:,options])