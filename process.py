import pandas as pd
import numpy as np
import json
from matplotlib import pyplot as plt
import numpy as np
import pytz
import re
from os import walk

import getGoogleData

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

import streamlit as st


#Reusable Functions and variables

def cus_strip(x):
    x = re.sub('[A-Za-z% ]*','',x)
    try:
        x = int(x)
    except:
        x = float(x)
    return x

def time_to_hours(x):
    x = re.sub('[A-Za-z% ]*', '', x)
    x= int(x.split(':')[0]) + int(x.split(':')[1]) / 60
    return x

def to_hour_categorical(x):
    bins = pd.IntervalIndex.from_tuples([(0, 4),(4,6),(6,10), (10, 18), (18, 20),(20,24)])
    x = x.map(time_to_hours)
    return pd.cut(x,bins)


def date_index(df):
    for column in df.columns:
        name = re.fullmatch('[ A-Z-z]*(Date|date)[ A-Z-z]*',column)
    try:
        df.index = pd.to_datetime(df[name])
    except:
        print('error')
    df.index = df.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')
    return df




#%% Iteration and maintaining the state for all files

directory = '/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/'
f = []
for (dirpath, dirnames, filenames) in walk(directory):
    f.extend(filenames)
    break
f

#todo load archives
archives = []
new_files = [file for file in f if file not in archives]
for file_name in new_files:
    if re.fullmatch('[A-Za-z0-9- ]*-I-O\.json$',file_name):
        # code for DayOne json objects
        archives.append(file_name)
        print(f'DayOne files {file_name}')


    elif re.fullmatch('^counter[ 0-9]*\.csv$',file_name):
        # code for Counter objects
        archives.append(file_name)
        print(f'counter files {file_name}')

    elif re.fullmatch('^CaloryNutritionLog[ 0-9]*\.csv$',file_name):
        # code for Calory objects
        archives.append(file_name)
        print(f'Calory Nutrition files {file_name}')


    elif re.search('^heart-report[ 0-9-]*\.csv$',file_name):
        # code for Heart rate objects
        archives.append(file_name)
        print(f'Heart report files {file_name}')

    elif re.search('^SmartBP[ 0-9-]*\.csv$',file_name):
        # code for Blood Pressure
        archives.append(file_name)
        print(f'BP report files {file_name}')



#%% DayOne Journal - loading and processing todo process dayOne

with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/2020-9-30-I-O.json') as f:
    journal = json.load(f)

df = pd.DataFrame(journal['entries'],columns = ['location','creationDate','timeZone','text'])
df.info()

#Time normalization


time_zone = pytz.timezone(df.timeZone[0])
df.index = pd.to_datetime(df.creationDate)
df.index = df.index.tz_convert(time_zone).to_period('d')
df.drop('creationDate',axis = 1,inplace = True)
df.head()

#%% Heart metrics - loading and processing
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/heart-report-2020-10-19-2020-11-19.csv','rb') as f:
    heartDf = pd.read_csv(f, parse_dates=True,usecols=['date','minimum','maximum','average','activity','weight','calories'])


heartDf.index = pd.to_datetime(heartDf.date.map(lambda x: x.strip("'")))
heartDf.index = heartDf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

heartDf.drop(columns = ['date'],inplace=True)
heartDf.rename(columns={'minimum':'min_HR','maximum':'max_HR','average':'avg_HR'},inplace=True)
heartDf.info()

#%% Blood Pressure metrics - loading and processing
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/SmartBP 2.csv','rb') as f:
    bpDf = pd.read_csv(f, parse_dates=True)

bpDf.drop(columns = ['hkid','Pulse','Weight','Tags'],inplace=True)
bpDf.rename(columns = {'Pulse Pressure':'Pulse_Pressure'},inplace=True)

bpDf.index = pd.to_datetime(bpDf.Date)
bpDf.index = bpDf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

bpDf = bpDf.assign(Systolic = lambda x: x.Systolic.map(cus_strip),
                   Diastolic = lambda x: x.Diastolic.map(cus_strip),
                   Pulse_Pressure = lambda x: x.Pulse_Pressure.map(cus_strip),
                   MAP = lambda x: x.MAP.map(cus_strip)
                   )
bpDf.drop(columns = ['Date'],inplace=True)
daily_bpDf = bpDf.drop(columns = ['Notes']).groupby(level=0).mean()

#%% Plotting and testing sci view in Pycharm

"""
x = np.arange(0,len(df),1)
fig, ax = plt.subplots(1,1)
ax.plot(x,df['resting'])
ax.set_xticks(x)
ax.set_xticklabels(df.index,rotation = 90)
plt.show()

"""


#%% Calory and Nutrition - loading and processing

with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/CaloryNutritionLog.csv','rb') as f:
    Nutritiondf = pd.read_csv(f, parse_dates=True)

Nutritiondf.columns = Nutritiondf.columns.str.strip()
Nutritiondf.columns = Nutritiondf.columns.str.replace(' ', '_')

Nutritiondf.index = pd.to_datetime(Nutritiondf.Date)
Nutritiondf.index = Nutritiondf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

#Daily information of foods and timings
foods = Nutritiondf.groupby(level = 0)['Name'].apply(list)
meals = Nutritiondf.groupby(level=0)['Meal_Type'].apply(set)
meal_timings = to_hour_categorical(Nutritiondf.Time)


Nutritiondf = Nutritiondf.drop(columns=['Date','Meal_Type','Name','Time'])
Nutritiondf = Nutritiondf.groupby(level = 0).sum()
Nutritiondf.info()

#%% Counters - loading and processing
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/counter.csv','rb') as f:
    counterdf = pd.read_csv(f, parse_dates=True)
counterdf.info()
counterdf.drop(columns = ['Comment'])




#%%loading and processing activity data from Google sheets #todo process activity data

spreadsheet = '1zBobHYySwSJuzEkJ5wHB0XaFoMpV0QKYzeoQVu724WA'
range = 'Workouts'

activityDf = getGoogleData.get(spreadsheet, range)

activityDf = date_index(activityDf)

activityDf.index = pd.to_datetime(activityDf.Date)
activityDf.index = activityDf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')



activities = activityDf.groupby(level=0)['Meal_Type'].apply(set)


activityDf.info()


#%%loading and Processing health metrics from Google sheets

spreadsheet = '1pfwy5fPst1lscUK3HPe9ORfY-R7bWoAajUqmystGcdg'
range = 'Daily Metrics'
dailyDf = getGoogleData.get(spreadsheet, range)

dailyDf.index = pd.to_datetime(dailyDf.Date)
dailyDf.index = dailyDf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

dailyDf.drop(columns=['Date','VO₂ max'],axis = 1,inplace = True)

#todo unable to convert to numeric - problem
dailyDf = dailyDf.astype('float')

dailyDf.rename(columns = {'Active Energy': 'Active_Energy','Resting Energy': 'Resting_Energy','Resting':'Resting_HR'},inplace=True)
dailyDf.info()

#%%loading and processing Sleep from Google sheets

spreadsheet = '1pfwy5fPst1lscUK3HPe9ORfY-R7bWoAajUqmystGcdg'
range = 'Sleep'
SleepDf = getGoogleData.get(spreadsheet, range)

SleepDf.index = pd.to_datetime(SleepDf.Date)
SleepDf.index = SleepDf.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')
SleepDf.drop(columns=['Date','Data Source','InBed','Awake','Fall Asleep'],axis = 1,inplace = True)

#todo bin and convert start and end times to categorical, edit efficiency

SleepDf.Start = to_hour_categorical(SleepDf.Start)
SleepDf.End = to_hour_categorical(SleepDf.End)

SleepDf = SleepDf.assign(Efficiency = lambda x: x.Efficiency.map(cus_strip),
                         Asleep = lambda x: x.Asleep.map(time_to_hours),
                         Asleep_sum = lambda x: x.groupby(level = 0).sum().Asleep)

SleepDf = SleepDf.astype({'Wake Count': 'int32','Efficiency':'int32'})
SleepDf = SleepDf[SleepDf['Main'] == 'TRUE']
SleepDf.drop(columns=['Asleep','Main'],axis = 1,inplace = True)
SleepDf.rename(columns={'Efficiency':'Sleep_Efficiency','Wake Count': 'Wake_Count','Start':'Sleep_Start','End':'Sleep_End'},inplace=True)


SleepDf.info()