from email.policy import default
from turtle import onclick
import streamlit as st
import pandas as pd
import numpy as np
import requests

import matplotlib.pyplot as plt
from matplotlib import colors
import seaborn as sns

from bs4 import BeautifulSoup

import plotly.express as px


st.set_page_config(
    page_title = "Census API Helper App",
    layout = 'wide',
    initial_sidebar_state = 'auto'
)


st.title('Census API Helper App')


st.sidebar.write("Instructions will go here. i.e. how to use app and what it can do for you")

#Load state table and abbreviations
@st.cache()
def load_states():
    state_codes = pd.read_csv('https://www2.census.gov/geo/docs/reference/state.txt', sep='|', dtype={'STATE': str})
    return(state_codes)

@st.cache()
def load_counties(state_codes):
    US_counties = []
    for i in range(len(state_codes)):
        state_num = state_codes.iloc[i]['STATE']
        state_ab = state_codes.iloc[i]['STUSAB'].lower()
        # print("state num: {} state_ab: {}".format(state_num, state_ab))
        county_url = 'https://www2.census.gov/geo/docs/reference/codes/files/st{}_{}_cou.txt'.format(state_num, state_ab)
        county_codes = pd.read_csv(county_url, names=['State', 'State Code', 'County Code', 'County Name', 'Fips Class Code'], dtype={'County Code': str, 'State Code': str})
        US_counties.append(county_codes)
    return(pd.concat(US_counties))


def concept_dict_creation(final_df):
    concepts_fields = {}
    concepts = list(final_df['Concept'].unique())
    concepts.remove('Census API Geography Specification')
    concepts = concepts[1:]
    for c in concepts:
        curr_df = final_df.loc[final_df['Concept'] == c]
        labels = list(curr_df['Label'])
        field = list(curr_df['Name'])
        concepts_fields[c] = {}
        for l in range(len(labels)):
            #split by !!
            label_split = labels[l].split("!!")
            new_label = label_split[-1]
            new_label = new_label + "_" + c
            concepts_fields[c][new_label] = field[l]
    return(concepts_fields)


@st.cache()
def load_fields():
    url = 'https://api.census.gov/data/2020/dec/pl/variables.html'
    html_text = requests.get(url).text
    soup = BeautifulSoup(html_text, 'html.parser')
    tables = []
    for table in soup.find_all('table'):
        tables.append(table)
    data_table = tables[0]
    columns = []
    header = data_table.find_all('thead')[0].find_all('th')
    for i in header:
        curr_column = i.get_text()
        curr_column = curr_column.replace(' ', '_')
        columns.append(curr_column)
    
    final_list = []
    for i in data_table.find_all('tr'):
        curr_row = i.find_all('td')
        if len(curr_row) == len(columns):
            curr_list = []
            #parse date
            for val in range(0,len(columns)):
                to_add = curr_row[val].get_text().strip().replace(',','')
                curr_list.append(to_add)
            final_list.append(curr_list)
    final_df = pd.DataFrame(final_list, columns=columns)
    final_df = final_df.loc[final_df['Concept'] != ""]
    dict_to_return = concept_dict_creation(final_df)
    return(dict_to_return)

state_codes = load_states()
state_list = list(state_codes['STUSAB'])
state_list.append('ALL STATES')

US_county_codes = load_counties(state_codes)
US_county_list = list(US_county_codes['County Name'])
US_county_list.append('ALL COUNTIES')

field_dict = load_fields()

#Call Census Query
def census_2020(API_key, county_codes = US_county_codes, fields = {'OCCUPANCY STATUS': {'!!Total:' :'H1_001N'}},
                 state_abr = "ALL STATES", county_name = "ALL COUNTIES", county = True,
                  tract = True, field_dict = field_dict):
    ''' Takes in API Key, Census fields, and geography and granularity specifications. Returns a dataframe'''

    # fields = fields['OCCUPANCY STATUS'].values()
    field_list = []
    for k in field_dict.keys():
        for i in fields:
            field_list.append(field_dict[k].get(i))
    field_list = list(filter(None, field_list))

    state_abr = state_abr[0]
    
    state_codes = pd.read_csv('https://www2.census.gov/geo/docs/reference/state.txt', sep='|', dtype={'STATE': str})
    if state_abr == 'ALL STATES':
        state = '*'
    if state_abr != "ALL STATES":
        state = state_codes.loc[state_codes['STUSAB'] == state_abr]['STATE'].values[0]
        county_codes = county_codes.loc[county_codes['State'] == state_abr]
    
    # if (state_abr != "ALL STATES"):
    #     county_codes = county_codes.loc[county_codes['State Code'] == state_abr]
    #     # county_url = 'https://www2.census.gov/geo/docs/reference/codes/files/st{}_{}_cou.txt'.format(state, state_abr.lower())
    #     # print(county_url)
    #     # county_codes = pd.read_csv(county_url, names=['State', 'State Code', 'County Code', 'County Name', 'Fips Class Code'], dtype={'County Code': str})
    if county_name[0] == "ALL COUNTIES":
        county_name = "*"
    elif county_name != "ALL COUNTIES":
        # county_name = county_codes.loc[county_codes['County Name'] == county_name]['County Code'].values[0]
        county_name = county_codes.loc[county_codes['County Name'].isin(county_name)]['County Code'].values
        county_name = ','.join(county_name)


    if tract:
        final_call = 'https://api.census.gov/data/2020/dec/pl?get={}&for=tract:*&in=state:{}&in=county:{}&key={}'.format(','.join(field_list), state, county_name, API_key)
        # st.write(final_call)
        call_return = requests.get(final_call).json()
        call_df = pd.DataFrame(call_return)
        call_df.columns = call_df.iloc[0]
        call_df = call_df.drop(call_df.index[0])

        call_df = call_df.merge(county_codes, left_on = ['state', 'county'], right_on = ['State Code','County Code'], how = 'left')

    elif county:
        final_call = 'https://api.census.gov/data/2020/dec/pl?get={}&for=county:{}&in=state:{}&key={}'.format(','.join(field_list), county_name, state, API_key)
        # st.write(final_call)
        call_return = requests.get(final_call).json()
        call_df = pd.DataFrame(call_return)
        call_df.columns = call_df.iloc[0]
        call_df = call_df.drop(call_df.index[0])
        call_df = call_df.astype({'county': str})

        call_df = call_df.merge(county_codes, left_on = 'county', right_on = 'County Code', how = 'left')
    else:
        final_call = 'https://api.census.gov/data/2020/dec/pl?get={}&for=state:{}&key={}'.format(','.join(field_list), state, API_key)
        # st.write(final_call)
        call_return = requests.get(final_call).json()
        call_df = pd.DataFrame(call_return)
        call_df.columns = call_df.iloc[0]
        call_df = call_df.drop(call_df.index[0])

        #merge with state codes table
        call_df = call_df.merge(state_codes, left_on = 'state', right_on = 'STATE', how = 'left')
        call_df = call_df.rename(columns = {'STUSAB': 'State', 'STATE': 'State Code', 'state': 'state code'})


    #update call_df to the right data types
    call_df[field_list] = call_df[field_list].astype(int)
    for i in range(len(fields)):
        call_df.rename(columns = {field_list[i]: fields[i]}, inplace = True)

    return(final_call, call_df)

api = st.sidebar.text_input(label="Enter API Key", value="")

state = st.sidebar.multiselect(label="Enter State Abbreviation", options=state_list ,default='ALL STATES')

county = st.sidebar.radio(label = "County Granularity", options = (True, False))

# county_name = st.sidebar.text_input(label = "Enter County Name (If known)", value = "")
county_name = st.sidebar.multiselect(label = "Enter County Name (If known)", options = US_county_list, default='ALL COUNTIES')

tract = st.sidebar.radio(label = "Census Tract Granularity", options = (True, False))

#options for what fields to choose
occupancy_fields = st.sidebar.multiselect(label = "Occupancy Fields", options = list(field_dict['OCCUPANCY STATUS'].keys()))

race_fields = st.sidebar.multiselect(label = "Race Fields", options = list(field_dict['RACE'].keys()))

race_18plus_fields = st.sidebar.multiselect(label = "Race 18+ Fields", options = list(field_dict['RACE FOR THE POPULATION 18 YEARS AND OVER'].keys()))

hisp_lat_fields = st.sidebar.multiselect(label = "Hispanic/Latino Fields", options = list(field_dict['HISPANIC OR LATINO AND NOT HISPANIC OR LATINO BY RACE'].keys()))

hist_lat_18plus_fields = st.sidebar.multiselect(label = "Hispanic/Latino 18+ Fields", options = list(field_dict['HISPANIC OR LATINO AND NOT HISPANIC OR LATINO BY RACE FOR THE POPULATION 18 YEARS AND OVER'].keys()))

group_quarters_fields = st.sidebar.multiselect(label = "Group Quarters Fields", options = list(field_dict['GROUP QUARTERS POPULATION BY MAJOR GROUP QUARTERS TYPE'].keys()))

fields_to_read = occupancy_fields + race_fields + race_18plus_fields + hisp_lat_fields + hist_lat_18plus_fields + group_quarters_fields

button_clicked = st.sidebar.button(label="Run Query")

if button_clicked:
    results = census_2020(api, US_county_codes, fields_to_read, state, county_name, county, tract, field_dict)
    st.write(results[1])

    needed_tabs = ['State']
    if county:
        needed_tabs.append('County')
    if tract:
        needed_tabs.append('Tract')

    tabs = st.tabs(needed_tabs)
    for i in range(len(needed_tabs)):
        with tabs[i]:
            if needed_tabs[i] == 'State':
                st.bar_chart(results[1], x = 'State', y = fields_to_read)
            if needed_tabs[i] == 'County':
                st.bar_chart(results[1], x = 'County Name', y = fields_to_read)
            if needed_tabs[i] == 'Tract':
                st.bar_chart(results[1], x = 'tract', y = fields_to_read)                
    # for i in range(len(fields_to_read)):
    #     with tabs[i]:
    #         tab_fields = st.multiselect(label='add fields', options = fields_to_read, default = fields_to_read[i])
    #         st.header(fields_to_read[i])
    #         st.bar_chart(results[1], x = 'STUSAB', y = tab_fields) 

def run_query(api = 'empty', state = 'empty'):
    st.write("Api: {} State: {}".format(api, state))

