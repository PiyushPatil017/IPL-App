import pandas as pd
import numpy as np
import streamlit as st
import requests


players = requests.get("http://127.0.0.1:7000/player_name").json()
season = requests.get('http://127.0.0.1:7000/seasons').json()
teams = requests.get('http://127.0.0.1:7000/ipl_teams').json()

st.sidebar.title('IPL Data')
option1 = st.sidebar.selectbox('Select option',options = ['IPL Records','Team Records','Player Records'])
# btn1 = st.sidebar.button('Select')

# if btn1:
if option1 == 'IPL Records':
    st.sidebar.selectbox('Select Season', options = season)
elif option1 == 'Team Records':
    st.sidebar.selectbox('Select Team',options = teams)
elif option1 == 'Player Records':
    st.sidebar.selectbox('Select Player', options= players)