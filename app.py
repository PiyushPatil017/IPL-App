import pandas as pd
import numpy as np
import streamlit as st
import requests
from PIL import Image

st.set_page_config('IPL App', layout='wide')

players = requests.get("http://127.0.0.1:7000/player_name").json()
season = requests.get('http://127.0.0.1:7000/seasons').json()
teams = requests.get('http://127.0.0.1:7000/ipl_teams').json()

# to change state of main screen as required
if 'step' not in st.session_state:
    st.session_state.step = 0

st.sidebar.title('IPL Data')
option1 = st.sidebar.selectbox('Select option',options = ['IPL Records','Team Records','Player Records'],
                               index = None,placeholder='Select Option...')

if option1 == 'IPL Records':
    season_option = st.sidebar.selectbox('Select Season', options = season)
elif option1 == 'Team Records':
    team_option = st.sidebar.selectbox('Select Team',options = teams)
elif option1 == 'Player Records':
    player_option = st.sidebar.selectbox('Select Player', options= players)

btn1 = st.sidebar.button('Select')
if btn1:
    st.session_state.step = 1
    if option1 == 'IPL Records':
        st.title('IPL Records')

    elif option1 == 'Team Records':
        # Display team logo and name
        col1, col2 = st.columns([0.15,0.85], vertical_alignment='center')
        with col1:
            img = Image.open('ipl logo/{}.png'.format(team_option))
            img = img.resize((400,300))
            st.image(img)
        with col2:
            st.title('{}'.format(team_option))

        # display team record
        team_record = requests.get('http://127.0.0.1:7000/team',params={'team': team_option})
        data = team_record.json()

        # Overall Stats
        overall_df = pd.DataFrame(data['Overall'],index = [0])
        trophy = overall_df['Trophys'].values
        years = overall_df['trophy_years'].values[0]
        if trophy > 0:
            col1,col2 = st.columns([0.1,0.9],vertical_alignment='center')
            with col1:
                img = Image.open('ipl logo/IPL trophy.png')
                img = img.resize((70,70))
                st.image(img,caption = trophy)
            with col2:
                st.text(years)

        st.subheader('Overall Statistic')
        st.dataframe(data = overall_df,hide_index=True,column_order=['Total Match','Total Win','Total Loss','Total Draw'])

        # Season Stats
        st.subheader('Season-Wise Statistic')
        season_df = pd.DataFrame(data['Season']).T
        season_df.sort_index(ascending = False,inplace=True)
        season_df.reset_index(names='Season', inplace =True)
        st.dataframe(data = season_df, hide_index=True, column_order=['Season','Matches','Won','Loss','Draw'])

    elif option1 == 'Player Records':
        st.title('{}'.format(player_option))

# Option to choose another team and stats against them
if st.session_state.step == 1:
    team2_option = st.sidebar.selectbox('Select team to show stats against them', options=teams)
    team_btn2 = st.sidebar.button('Analyze')
    if team_btn2:
        st.session_state.step = 2
        st.title(team2_option)