import pandas as pd
import json
from matplotlib import pyplot as plt
import numpy as np
import pytz
import re
from os import walk


from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

# %%
plt.plot(np.random.randn(10,2))
plt.show()

#%% DayOne Journal

with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/2020-9-30-I-O.json') as f:
    journal = json.load(f)

df = pd.DataFrame(journal['entries'],columns = ['location','creationDate','timeZone','text'])
df.info()

#%% Time normalization
time_zone = pytz.timezone(df.timeZone[0])
df.index = pd.to_datetime(df.creationDate)
df.index = df.index.tz_convert(time_zone).to_period('d')
df.drop('creationDate',axis = 1,inplace = True)
df.head()

#%% Heart metrics
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/heart-report-2020-08-31-2020-09-30.csv','rb') as f:
    df2 = pd.read_csv(f, parse_dates=True)

df2.index = pd.to_datetime(df2.date.map(lambda x: x.strip("'")))
df2.index = df2.index.tz_localize(pytz.utc).tz_convert(time_zone).to_period('d')

df = pd.concat([df,df2],axis=1)

#%%
x = np.arange(0,len(df),1)
fig, ax = plt.subplots(1,1)
ax.plot(x,df['resting'])
ax.set_xticks(x)
ax.set_xticklabels(df.index,rotation = 90)
plt.show()


#%% Calory and Nutrition

with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/CaloryNutritionLog.csv','rb') as f:
    Nutritiondf = pd.read_csv(f, parse_dates=True)
foods = Nutritiondf.groupby('Date')[' Name'].apply(list)


#%% Counters
with open('/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/counter.csv','rb') as f:
    counterdf = pd.read_csv(f, parse_dates=True)
    print(f.path)

#%%
counterdf.info()
counterdf.drop(columns = ['Comment'])


#%% Iteration and maintaining the state for all files

directory = '/Users/aravind/Library/Mobile Documents/com~apple~CloudDocs/Documents/IO/'
f = []
for (dirpath, dirnames, filenames) in walk(directory):
    f.extend(filenames)
    break
f

#%%
#todo load archives
archives = []
new_files = [file for file in f if file not in archives]
for file_name in new_files:
    if re.fullmatch('[A-Za-z0-9- ]*-I-O\.json$',file_name):
        # code for DayOne json objects
        archives.append(file_name)
        print(f'DayOne files {file_name}')


    if re.fullmatch('^counter[ 0-9]*\.csv$',file_name):
        # code for Counter objects
        archives.append(file_name)
        print(f'counter files {file_name}')

    if re.fullmatch('^CaloryNutritionLog[ 0-9]*\.csv$',file_name):
        # code for Calory objects
        archives.append(file_name)
        print(f'Calory Nutrition files {file_name}')


    if re.search('^heart-report[ 0-9-]*\.csv$',file_name):
        # code for Heart rate objects
        archives.append(file_name)
        print(f'Heart report files {file_name}')