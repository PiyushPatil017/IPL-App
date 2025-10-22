import pandas as pd
import numpy as np
import streamlit as st
import requests
from PIL import Image
import json
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config('IPL App', layout='wide')

# request player, season, team name form api
players = requests.get("http://127.0.0.1:7000/player_name").json()
season = requests.get('http://127.0.0.1:7000/seasons').json()
teams = requests.get('http://127.0.0.1:7000/ipl_teams').json()

# set session_state so that we do not get blank screen on shifting screen
if "screen" not in st.session_state:
    st.session_state.screen = "start"

# Create sidebar and menu option
st.sidebar.title('IPL Data')
option1 = st.sidebar.selectbox('Select option',options = ['IPL Records','Team Records','Player Records'],
                               index = None,placeholder='Select Option...')

# take first option from sidebar
if option1 == 'IPL Records':
    season_option = st.sidebar.selectbox('Select Season', options = season)
elif option1 == 'Team Records':
    team_option = st.sidebar.selectbox('Select Team',options = teams)
elif option1 == 'Player Records':
    player_option = st.sidebar.selectbox('Select Player', options= players)

btn1 = st.sidebar.button('Select')

# if btn1 pressed action to be performed. in this we create separate screen for all the options and assign them to session_state
if btn1:
    if option1 == 'IPL Records' and season_option:
        st.session_state.screen = 'season_screen'
        st.session_state.season = season_option
    elif option1 == 'Team Records' and team_option:
        st.session_state.screen = 'team_screen'
        st.session_state.team1 = team_option
    elif option1 == 'Player Records' and player_option:
        st.session_state.screen = 'player_screen'
        st.session_state.player = player_option
    else:
        st.sidebar.warning('Please make a selection')
    st.rerun()

# when this season option is choosed this will be displayed on screen
if st.session_state.screen == 'season_screen':
    st.title('Season')

# if team option is choosed this will be displayed on screen
elif st.session_state.screen in ['team_screen','team_vs_team_screen']:
    # provide team1 and show its logo and name
    team1 = st.session_state.team1
    col1, col2 = st.columns([0.15, 0.85], vertical_alignment='center')
    with col1:
        img = Image.open('ipl logo/{}.png'.format(team1))
        img = img.resize((400, 300))
        st.image(img)
    with col2:
        st.title('{}'.format(team1))

    # when only 1 team is selected overall and season wise stat is displayed
    if st.session_state.screen == 'team_screen':
        # request data from api
        data = requests.get('http://127.0.0.1:7000/team',params={'team': team1}).json()


        # Overall Stats
        overall_df = pd.DataFrame(data['Overall'],index = [0])
        trophy = overall_df['Trophys'].values
        years = overall_df['trophy_years'].values[0]
        # display trophy logo and years in which trophy won
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

    # Option for team vs team
    st.sidebar.divider()
    team2_option = st.sidebar.selectbox('Select Team to Compare Against',options = teams, key = 'team2_selector')
    team_btn = st.sidebar.button('Compare')
    if team_btn:
        st.session_state.screen = 'team_vs_team_screen'
        st.session_state.team2 = team2_option
        st.rerun()

    # This screen displays stat of team1 against team2
    if st.session_state.screen == 'team_vs_team_screen':
        team2 = st.session_state.team2
        if team1 != team2:
            st.title(team1 + " vs " + team2)
            response = requests.get('http://127.0.0.1:7000/team_vs_team', params = {'team1':team1, 'team2': team2}).json()
            df = pd.DataFrame(response).T
            df.reset_index(names = 'Teams',inplace = True)
            st.dataframe(df,hide_index = True)
            # st.bar_chart(x=df['won'], y= df['won'])
        else:
            st.warning('Please select different team')

# If player option is chose this will be displayed on screen
elif st.session_state.screen in ['player_screen','player_compare_screen']:
    if st.session_state.screen == 'player_screen':
        player = st.session_state.player
        st.title(player)
        first_name, *others, last_name = player.split(" ")
        st.page_link('https://en.wikipedia.org/wiki/{}_{}'.format(first_name,last_name),label=f'About {player}')

        # player obtained from selectbox contains full name while our dataset has short name. so we send short name in request
        with open('players_names.json') as rf:
            data = json.load(rf)
        player = data[player]

        # Send API Request
        response = requests.get('http://127.0.0.1:7000/player_record',params = {'player':player}).json()

        # create DataFrame for Batting
        st.subheader('Batting Statistics')
        overall_batting = pd.DataFrame(response['Batting']['Overall Record'], index = [0])
        overall_batting.rename(index = {0:'Overall'}, inplace = True)
        season_batting = pd.DataFrame(response['Batting']['Season']).T
        season_batting.sort_index(ascending=False,inplace = True)
        df_batting =pd.concat([overall_batting,season_batting])
        df_batting = df_batting.fillna('-')
        # height parameter to show all rows at once
        st.dataframe(df_batting, height = len(df_batting)*35 + 38)

        # visualize the Batting records
        btn_bat_viz = st.button('Visualize Batting Stats')
        if btn_bat_viz:
            temp_batting = df_batting.iloc[1:].sort_index(ascending=True)
            fig = px.line(temp_batting, x=temp_batting.index, y='Runs', text='Runs', labels={'index': 'Season'},
                         title='Runs Scored in Each Season',height=600,width = 700)
            fig.update_traces(textposition = 'top center')
            st.plotly_chart(fig)

        # create DataFrame for Bowling
        st.divider()
        st.subheader('Bowling Statistics')
        overall_bowling = pd.DataFrame(response['Bowling']['Overall Record'], index=[0])
        overall_bowling.rename(index={0: 'Overall'}, inplace=True)
        season_bowling = pd.DataFrame(response['Bowling']['Season']).T
        season_bowling.sort_index(ascending=False, inplace=True)
        df_bowling = pd.concat([overall_bowling, season_bowling])
        df_bowling = df_bowling.fillna('-')
        st.dataframe(df_bowling, height = len(df_bowling)*35 + 38)

        # visualize the Bowling records
        btn_bowl_viz = st.button('Visualize Bowling Stats')
        if btn_bowl_viz:
            # bar chart for runs in each season
            temp_bowling = df_bowling.iloc[1:].sort_index(ascending=True)
            fig = px.line(temp_bowling, x=temp_bowling.index, y='Wickets', labels={'index': 'Season'}, text = 'Wickets',
                         title='Wickets Taken in Each Season', height=600, width=700)
            fig.update_traces(textposition = 'top center')
            st.plotly_chart(fig)

    # add option to compare with other players
    st.sidebar.divider()
    player_compare_list = st.sidebar.multiselect('Select to player to compare stats', options=players,
                                                 key='compare_player', max_selections=3)
    player_compare_list.insert(0, st.session_state.player)
    player_compare_btn = st.sidebar.button('Compare')
    if player_compare_btn:
        st.session_state.screen = 'player_compare_screen'
        st.session_state.player_compare_list = player_compare_list
        st.rerun()

    # Screen to show comparison of players
    elif st.session_state.screen == 'player_compare_screen':
        player_compare_list = st.session_state.player_compare_list
        player_compare_bat_dict = {}
        player_compare_bowl_dict = {}
        title_str = ''

        # Loop to get data of players selected
        for player_name in player_compare_list:
            title_str = title_str + player_name + ' Vs '
            with open('players_names.json') as rf:
                data = json.load(rf)
            player_full_name = data[player_name]

            # Send API Request
            response = requests.get('http://127.0.0.1:7000/player_record', params={'player': player_full_name}).json()
            player_compare_bat_dict[player_name] = response['Batting']['Overall Record']
            player_compare_bowl_dict[player_name] = response['Bowling']['Overall Record']

        # show dataframe and bar chart for batting stats
        player_compare_bat_df = pd.DataFrame(player_compare_bat_dict)
        fig = px.bar(player_compare_bat_df, x = player_compare_bat_df.index, y = player_compare_bat_df.columns, text_auto=True, barmode='group', log_y=True,
                     height=600, width = 900, labels = {'index':'Stat'}, title = 'Batting Head to Head of Players')
        st.title(title_str[:-3])
        st.subheader('Batting Statistics')
        st.dataframe(player_compare_bat_df)
        st.plotly_chart(fig)
        st.divider()

        # show dataframe and bar chart for bowling stats
        player_compare_bowl_df = pd.DataFrame(player_compare_bowl_dict)
        fig = px.bar(player_compare_bowl_df, x=player_compare_bowl_df.index, y=player_compare_bowl_df.columns,
                     text_auto=True, barmode='group', log_y=True,
                     height=600, width=900, labels={'index': 'Stat'}, title='Bowling Head to Head of Players')
        st.subheader('Bowling Statistics')
        st.dataframe(player_compare_bowl_df)
        st.plotly_chart(fig)