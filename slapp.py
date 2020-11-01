import streamlit as st
import pandas as pd
import pytz

st.write('hello')
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/heart-report-2020-08-31-2020-09-30.csv','rb') as f:
    df2 = pd.read_csv(f, parse_dates=True)

time_zone = 'America/New_York'

st.write(df2.head())
df2.index = pd.to_datetime(df2.date.map(lambda x: x.strip("'")))
df2.index = df2.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

st.line_chart(df2.resting.values)