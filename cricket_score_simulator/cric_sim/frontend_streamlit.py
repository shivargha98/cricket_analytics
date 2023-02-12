import streamlit as st
import random
from get_categorical_encodings import *
from model_inference import *
st.title("T20 Internationals Simulator App")

#countries_selected = ["None","None"]
###### Ask User to Select Country #####

@st.cache
def get_toss_res(team1,team2):
     ################ Random Coin TOSS ################
    toss_won_by = random.choice([team1,team2])
    if toss_won_by == team1:
        toss_loser = team2
    else:
        toss_loser = team1
    decision_toss_winner = random.choice(["bat","field"])
    toss_res = "Toss won by {} and {} choose to {}".format(toss_won_by,toss_won_by,decision_toss_winner)
    return toss_res,decision_toss_winner,toss_won_by,toss_loser
    #############################################

country_list = give_countries_as_options()
countries_selected = st.multiselect(
    'Select Two Countries to create a Simulated Match',
    country_list,
    max_selections = 3
    )


if len(countries_selected) > 1:
    toss_str,decision_toss_winner,toss_won_by,toss_loser= get_toss_res(countries_selected[0],countries_selected[1])
    st.subheader("Toss Result")
    st.write(toss_str)

############# Select Venue/City ###############
venues_list = get_venue_options()
venues_list = ["None"] + venues_list
venue_selected = st.selectbox('Select a Venue for the Match',venues_list)
##############################################



playing_11s = []
if len(countries_selected) > 1:

    toss_winner = toss_won_by
    if decision_toss_winner == "bat":
        bat_first_team = toss_winner
        bat_second_team = toss_loser
    
    elif decision_toss_winner == "field":
        bat_first_team = toss_loser
        bat_second_team = toss_winner

    col1, col2 = st.columns(2)
    select_players_bat_first_team = select_players(bat_first_team)
    with col1:
        options1 = st.multiselect(
            'Select Your Playing 11 for {}'.format(bat_first_team),
            select_players_bat_first_team,
            key=1,
            max_selections = 12
            )
       
        st.subheader("Selected Playing 11 for {}".format(bat_first_team))
        st.markdown(options1)
        playing_11s.append(options1)
        

    select_players_bat_second_team = select_players(bat_second_team)
    with col2:
        options2 = st.multiselect(
            'Select Your Playing 11 for {}'.format(bat_second_team),
            select_players_bat_second_team,
            key=2,
            max_selections = 12
            )
     
        st.subheader("Selected Playing 11 for {}".format(bat_second_team))
        st.markdown(options2)
        playing_11s.append(options2)

    #print(playing_11s)
    ##team1 -->> bat 1st, team2 --bat 2nd
    team1,team2 = playing_11s[0],playing_11s[1]
    team1_copy,team2_copy = team1.copy(),team2.copy()
    
    col3,col4 = st.columns(2)
    with col3:
        select_striker = st.multiselect(
            'Select Your Striker  for {} team'.format(bat_first_team),
            team1,
            key=3,
            max_selections = 2
            )
        if len(select_striker) > 0:
            team1_copy.remove(select_striker[0])
        select_non_striker = st.multiselect(
            'Select Your Non Striker  for {} team'.format(bat_first_team),
            team1,
            key=4,
            max_selections = 2
            )
        if len(select_non_striker) > 0:
            team1_copy.remove(select_non_striker[0])
        #print(select_striker,select_non_striker)
        
    with col4:
        select_bowler = st.multiselect(
            'Select Your Bowler  for {} team'.format(bat_second_team),
            team2,
            key=5,
            max_selections = 2
            )

    batsman_dict = {}
    bowler_dict = {}
    innings_dict={}
    over = []
    counter = 0
    ################ innings 1 ##############################
    innings_number = 1
    for over_num in range(0,20):
        for ball in range(1,7):
            if (len(select_striker) > 0) and (len(select_non_striker)>0):
                if (len(select_bowler) > 0):
                    venue_encodings = get_venue_encodings(venue_selected)
                    over = float(str(over_num)+"."+str(ball))
                    if innings_number == 1:
                        curr_inn_type_encoding = get_innings_type_encoding(innings_number)
                    elif innings_number == 2:
                        curr_inn_type_encoding = get_innings_type_encoding(innings_number)
                    
                    curr_inn_team_encoding = get_current_innings_encodings(bat_first_team)
                    bowling_team_encoding = get_bowling_innings_encodings(bat_second_team)
                    striker_encoding = get_batsman_encodings(select_striker[0])
                    non_striker_encoding = get_non_striker_encodings(select_non_striker[0])
                    bowler_encoding = get_bowler_encodings(select_bowler[0])
                    super_encodings = get_super_over_encodings("No")

                    batting_exp_encoding = get_batting_experience(select_striker[0])
                    bowling_exp_encoding = get_bowler_experience(select_bowler[0])
                    
                    explosivity_rating,running_rating,powerplay_rating,end_over_explosivity = get_batsman_stats(select_striker[0])
                    wicket_taking_rating,bowling_consistency_rating = get_bowler_stats(select_bowler[0])
                    
                    if counter == 0:
                        curr_score,curr_wickets = 0,0
                        

                        ### add batsman personal_score###
                        striker_score,balls_faced_batsman,batsman_strike_rate = 0,0,0

                        #####bowler by ball records##
                        runs_conceded_by_bowler,balls_bowled_bowler,wickets_by_bowler=0,0,0 
                        wickets_by_bowler,bowler_economy = 0,0

                        ###### batsman proportions#######
                        batsman_prop0,batsman_prop1,batsman_prop2,batsman_prop3 = 0,0,0,0
                        batsman_prop4,batsman_prop5,batsman_prop6,batsman_prop7 = 0,0,0,0

                        ####### bowler proportions ########
                        bowler_prop0,bowler_prop1,bowler_prop2,bowler_prop3 =0,0,0,0
                        bowler_prop4, bowler_prop5,bowler_prop6,bowler_prop7 = 0,0,0,0
                        bowler_prop8 = 0

                        ####create array for first prediction###
                        data_encoded = np.concatenate((venue_encodings,curr_inn_team_encoding,\
                            bowling_team_encoding,curr_inn_type_encoding,striker_encoding,
                            bowler_encoding,non_striker_encoding,super_encodings,
                            batting_exp_encoding,bowling_exp_encoding),axis=0)
                        
                        data_encoded = np.append(data_encoded,[over,curr_score,curr_wickets,striker_score,\
                         balls_faced_batsman,batsman_strike_rate,\
                         runs_conceded_by_bowler,balls_bowled_bowler,wickets_by_bowler,\
                        bowler_economy,batsman_prop0,batsman_prop1,batsman_prop2,\
                        batsman_prop3,batsman_prop4,batsman_prop5,batsman_prop6,\
                        batsman_prop7,bowler_prop0,bowler_prop1,bowler_prop2,bowler_prop3,\
                        bowler_prop4,bowler_prop5,bowler_prop6,\
                        bowler_prop7,bowler_prop8,explosivity_rating,\
                        running_rating,powerplay_rating,end_over_explosivity,\
                        wicket_taking_rating,bowling_consistency_rating])
                        ##################################
                        #print(data_encoded.shape)
                        prediction = inference_random_forest(data_encoded.reshape(1,-1))
                        st.write("{} bowls to {} results in {}".format(select_striker[0],
                        select_bowler[0],
                        prediction[0]))

                        counter = counter + 1



        

        
    