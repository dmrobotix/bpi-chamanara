#!/usr/bin/env python
# coding: utf-8

# In[431]:


import numpy as np
import pandas as pd
import datetime
import xarray as xr


# # Opening Files

# In[432]:


# PEI project flare types
datdir = 'C:/Users/Punch/Documents/Vespene_Repo/UN_data_validation_for_margot/'

geog_dist_fname = 'Geographic_Distribution_2020-2021.csv'
mon_consump_fname = 'monthly_consumption_new_model.csv'


# In[433]:


# open file: schools that were awarded the clean school bus award
geog_dist = pd.read_csv(datdir + geog_dist_fname)
print("Opened File:", datdir + geog_dist_fname)


# In[434]:


# open file: schools that were awarded the clean school bus award
mon_consump = pd.read_csv(datdir + mon_consump_fname, header = 1)
print("Opened File:", datdir + mon_consump_fname)


# ### Prep Geographic Distribution Data

# In[435]:


geog_dist


# In[436]:


# remove % from monthly hashrate data
geog_dist['monthly_hashrate_%'] = geog_dist['monthly_hashrate_%'].str.strip('%').astype(float)


# In[437]:


# turn into true percentage
geog_dist['monthly_hashrate_%'] = geog_dist['monthly_hashrate_%'] / 100


# In[438]:


# change date to datetime
geog_dist['date'] = pd.to_datetime(geog_dist['date'], format="%Y-%m-%d")


# In[439]:


# set date column as index
geog_dist = geog_dist.set_index('date')


# In[440]:


# get list of unique countries in the dataset
countries = geog_dist['country'].unique()


# In[441]:


# make a list of all the data split up by country
country_data_list = []

for i in range(len(countries)):
    
    country_data_list.append(geog_dist.loc[geog_dist['country'] == countries[i]].drop(columns=['country']))


# In[442]:


country_xr = xr.concat([df.to_xarray() for df in country_data_list], dim = 'country_name')


# In[443]:


# remove * from some of country names
countries[8] = countries[8].strip(' *')
countries[9] = countries[9].strip(' *')


# In[444]:


country_xr = country_xr.assign_coords(country_name = countries)


# In[445]:


country_xr


# In[446]:


country_xr.sel(country_name = countries[0])


# ### Prep Monthly Consumption Data

# In[447]:


mon_consump


# In[448]:


# change date format of monthly consumption data
mon_consump['date'] = None
for i in range(len(mon_consump)):
    month = mon_consump.loc[i, 'Month'].split(' ')[0]
    year = mon_consump.loc[i, 'Month'].split(' ')[1]

    month_number = datetime.datetime.strptime(month, '%B').month    
    date = datetime.datetime(int(year), int(month_number), 1)
    converted_date = datetime.datetime.strptime(date.strftime('%Y-%m-%d'), '%Y-%m-%d')

    mon_consump.loc[i, 'date'] = converted_date
    
mon_consump.drop(['Month'], axis=1, inplace=True)


# In[449]:


# set date column as index
mon_consump = mon_consump.set_index('date')


# In[450]:


# clip monthly consumption data to be the same dates as the geographical data
mon_consump = mon_consump[country_data_list[0].index.min():country_data_list[0].index.max()]


# In[451]:


# add monthly consumption data to country xarray
all_data = country_xr.assign(mon_consump = mon_consump['Monthly consumption, TWh'])


# ### Analysis

# In[452]:


all_data.sel(country_name = countries[0])


# In[453]:


all_data.sel(country_name = countries[0])["monthly_hashrate_%"]


# In[454]:


all_data["mon_consump"]


# In[464]:


country_2yr_consump = []

for i in range(len(countries)):
    
    print((all_data.sel(country_name = countries[i])["monthly_hashrate_%"] * all_data["mon_consump"]).groupby('date.year').sum('date').sum(), "\n")


# In[466]:


all_data.sel(country_name = 'Mainland China')

