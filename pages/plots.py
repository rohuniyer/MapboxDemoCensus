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


st.sidebar.write("Instructions will go here. i.e. how to use app and what it can do for you")


def plots():

    results = st.session_state['df']
    fields_to_read = st.session_state['fields_to_read']
    county = st.session_state['county']
    tract = st.session_state['tract']
    needed_tabs = ['State']
    if county:
        needed_tabs.append('County')
    if tract:
        needed_tabs.append('Tract')


    tabs = st.tabs(needed_tabs)
    for i in range(len(needed_tabs)):
        with tabs[i]:
            if needed_tabs[i] == 'State':
                chart_fields = st.multiselect(label='Choose fields', options = fields_to_read, default = fields_to_read[0])
                st.bar_chart(results, x = 'State', y = chart_fields)
            if needed_tabs[i] == 'County':
                st.bar_chart(results, x = 'County Name', y = fields_to_read)
            if needed_tabs[i] == 'Tract':
                st.bar_chart(results, x = 'tract', y = fields_to_read)  

plots()              
# for i in range(len(fields_to_read)):
#     with tabs[i]:
#         tab_fields = st.multiselect(label='add fields', options = fields_to_read, default = fields_to_read[i])
#         st.header(fields_to_read[i])
#         st.bar_chart(results[1], x = 'STUSAB', y = tab_fields) 
