# from email.policy import default
# from turtle import onclick
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


st.sidebar.write("Use this page to develop new fields")
st.sidebar.write("""Choose a Base Field and any fields you'd like to compare to. For example, if you wanted to know the percentage of a state in a 
                    correctional facility, choose 'Total:_RACE' as your Base Field and 'Correctional facilities for adults' as your comparison field""")


def calculate_fields(comp_val, base_val):
    try:
        val_to_return = comp_val / base_val
    except ZeroDivisionError:
        val_to_return = 0
    return(val_to_return)

def new_df(results, base_field, comparison_fields):

    new_results = pd.DataFrame.copy(results)
    new_fields = []
    for comp_field in comparison_fields:
        new_field = "{} per {}".format(comp_field, base_field)
        new_results[new_field] = new_results.apply(lambda x: calculate_fields(x[comp_field], x[base_field]), axis = 1)
        new_fields.append(new_field)
    return(new_results, new_fields)

def dist_plots(data, fields, new_fields):
    #create a correlation plot using seaborn
    total_fields = fields + new_fields
    st.write(total_fields)
    with st.expander('Scatter Dist'):
        fig = px.scatter_matrix(data, dimensions=total_fields)
        st.plotly_chart(fig, use_container_width = True)
    left_col, right_col = st.columns(2)
    with left_col:
        with st.expander('Box Plots'):
            for field in total_fields:
                fig = px.box(data, y=field, points = 'all')
                st.plotly_chart(fig, use_container_width = True)
    



def analysis():

    results = st.session_state['df']
    fields_to_read = st.session_state['fields_to_read']
    county = st.session_state['county']
    tract = st.session_state['tract']
    needed_tabs = ['State']
    if county:
        needed_tabs.append('County')
    if tract:
        needed_tabs.append('Tract')

    

    base_field = st.selectbox(label="Base Field", options = fields_to_read)
    comparison_fields = st.multiselect(label="Comparison fields", options = fields_to_read, default = fields_to_read[0])

    new_results, new_fields = new_df(results, base_field ,comparison_fields)
    
    with st.expander("Update field names"):
        new_names = {}
        for field in new_fields:
            new_name = st.text_input(label = field, value = field)
            new_names[field] = new_name

        for field in new_fields:
            new_results.rename(columns={field: new_names[field]}, inplace = True)
        new_fields = list(new_names.values())
    
    st.write(new_results)
    chart_fields = st.multiselect(label='Choose fields', options = new_fields, default = new_fields[0])

    tabs = st.tabs(needed_tabs)
    for i in range(len(needed_tabs)):
        
        with tabs[i]:
            if needed_tabs[i] == 'State':
                # st.bar_chart(new_results, x = 'State', y = chart_fields)
                dist_plots(new_results, fields_to_read, chart_fields)
            if needed_tabs[i] == 'County':
                st.bar_chart(new_results, x = 'County Name', y = chart_fields)
            if needed_tabs[i] == 'Tract':
                st.bar_chart(new_results, x = 'tract', y = chart_fields)

    st.session_state['new_df'] = new_results



analysis()              
# for i in range(len(fields_to_read)):
#     with tabs[i]:
#         tab_fields = st.multiselect(label='add fields', options = fields_to_read, default = fields_to_read[i])
#         st.header(fields_to_read[i])
#         st.bar_chart(results[1], x = 'STUSAB', y = tab_fields) 
