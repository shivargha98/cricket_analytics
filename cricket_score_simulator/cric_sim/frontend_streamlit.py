import streamlit as st
import random
from create_teams import *
st.title("T20 Internationals Simulator App")

#countries_selected = ["None","None"]
###### Ask User to Select Country #####

@st.cache
def get_toss_res(team1,team2):
     ################ Random Coin TOSS ################
    toss_won_by = random.choice([team1,team2])
    decision_toss_winner = random.choice(["bat","field"])
    toss_res = "Toss won by {} and {} choose to {}".format(toss_won_by,toss_won_by,decision_toss_winner)
    return toss_res
    #############################################

country_list = give_countries_as_options()
countries_selected = st.multiselect(
    'Select Two Countries to create a Simulated Match',
    country_list,
    max_selections = 3
    )


if len(countries_selected) > 1:
    toss_str = get_toss_res(countries_selected[0],countries_selected[1])
    st.subheader("Toss Result")
    st.write(toss_str)

############# Select Venue/City ###############
venues_list = get_venue_options()
venues_list = ["None"] + venues_list
venue_selected = st.selectbox('Select a Venue for the Match',venues_list)
##############################################



playing_11s = []
if len(countries_selected) > 1:


    col1, col2 = st.columns(2)
    select_players_team1 = select_players(countries_selected[0])
    with col1:
        options1 = st.multiselect(
            'Select Your Playing 11 for {}'.format(countries_selected[0]),
            select_players_team1,
            key=1,
            max_selections = 12
            )
       
        st.subheader("Selected Playing 11 for {}".format(countries_selected[0]))
        st.markdown(options1)
        playing_11s.append(options1)
        

    select_players_team2 = select_players(countries_selected[1])
    with col2:
        options2 = st.multiselect(
            'Select Your Playing 11 for {}'.format(countries_selected[1]),
            select_players_team2,
            key=2,
            max_selections = 12
            )
     
        st.subheader("Selected Playing 11 for {}".format(countries_selected[1]))
        st.markdown(options2)
        playing_11s.append(options2)

    #print(playing_11s)
    team1,team2 = playing_11s[0],playing_11s[1]
    team1_copy,team2_copy = team1.copy(),team2.copy()
    print(team1,team1_copy)
    col3,col4 = st.columns(2)
    with col3:
        select_striker = st.multiselect(
            'Select Your Striker  for {} team'.format(countries_selected[0]),
            team1,
            key=3,
            max_selections = 2
            )
        if len(select_striker) > 0:
            team1_copy.remove(select_striker[0])
        select_non_striker = st.multiselect(
            'Select Your Striker  for {} team'.format(countries_selected[0]),
            team1,
            key=4,
            max_selections = 2
            )
        if len(select_non_striker) > 0:
            team1_copy.remove(select_non_striker[0])
        #print(select_striker,select_non_striker)
    with col4:
        select_bowler = st.multiselect(
            'Select Your Striker  for {} team'.format(countries_selected[1]),
            team2,
            key=5,
            max_selections = 2
            )

    result = 0
    if (len(select_striker)>0) and (len(select_non_striker)>0):
        if (len(select_bowler)>0):
            st.write("Over 0.1 {} to {} results in {}".format(select_striker[0],select_bowler[0],\
                                                    result))

            result = "out"
            st.write("Over 0.2 {} to {} results in {} ".format(select_striker[0],select_bowler[0],\
                                                    result))
                                                
            select_striker = st.multiselect(
            'Select Your Striker  for {} team'.format(countries_selected[0]),
            team1_copy,
            key=6,
            max_selections = 2
            )
            if len(select_striker)>1:
                team1_copy.remove(select_striker[0])


            



        

        
    