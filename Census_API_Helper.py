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

st.write("This page will help you get situated with the Census API Helper App")
st.markdown(""" I plan to grow this so as you come back there will be more information available.
            If you have ideas, I'd love to hear them. You can reach out to me via my [website](https://www.rohuniyer.com) or
            or through [LinkedIn](https://www.linkedin.com/in/rohun-iyer-61518a112/). """)
st.markdown("## 1. API Query")
st.markdown("""This is the main page of the helper app. The App page is where you will start,
                after which you can go to the Plots and Analysis pages. Here you will enter your 
                Census API Key, choose your granularities and fields, and then run the query and
                actually call the API. """)
st.markdown("""You will need an API Key to run anything on the app. They are free
                and easy to get! You can go here to get one: [Census API Key Sign Up](https://api.census.gov/data/key_signup.html)
                
For more information: [Census API](https://www.census.gov/data/developers/guidance/api-user-guide.html)""")
st.markdown("""The 2020 Census does not contain any economic information but rather
                demographic data such as occupancy, race, ethnicity, and age.""")

st.markdown("## 2. Analysis")
st.markdown(
    """This page allows you to combine your chosen fields into new fields and produces a couple
        new charts along the way. """)
                
st.markdown(""" Choose a base field and one (or many) Comparison field(s) and the page will output a table
        with those new fields. You have the ability to update the field names and view the associated 
        scatter and box plots. """)

st.markdown("## 3. Plots")
st.markdown("""
            This is a barebones page at the moment. It only gives you the option to create one type
            of chart, a bar chart. You can view the data by the state, county and tract level based 
            on your initial selections. 
            """)

