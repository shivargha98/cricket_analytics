import pandas as pd
import numpy as np
import random

df = pd.read_csv("/home/shivargha/cricket_analytics/cricket_score_simulator/modeling/categories_with_encoding.csv")

def give_countries_as_options():

    teams = set(list(df["current_innings"].unique()) + list(df["bowling_team_name"].unique()))
    countries_list = list(teams)
    return countries_list

def get_venue_options():

    venues = set(list(df["venue"].unique()))
    venues_list = list(venues)
    return venues_list
    


def select_players(country_name):

    batsman = list(df[df["current_innings"] == country_name]["batsman"])
    bowler = list(df[df["bowling_team_name"] == country_name]["bowler"])
    all_players = batsman + bowler
    players_to_select = list(set(all_players))

    return players_to_select

def get_venue_encodings(venue_city):

    ## encoding is numpy array ##
    encodings = df[df["venue"]==venue_city][["venue_0","venue_1","venue_2","venue_3",\
        "venue_4","venue_5","venue_6","venue_7"]].iloc[0].values
    return encodings

def get_innings_type_encoding(innings_number):
    if innings_number == 1:
        inn_type = 'score_setter'
    elif innings_number == 2:
        inn_type = 'chasing'

    encodings = df[df["innings_type"]==inn_type][["innings_type_0",\
        "innings_type_1"]].iloc[0].values
    return encodings

def get_current_innings_encodings(team_name):

    encodings = df[df["current_innings"]==team_name][['current_innings_0', 'current_innings_1', \
            'current_innings_2', 'current_innings_3',\
         'current_innings_4', 'current_innings_5', 'current_innings_6']].iloc[0].values
    return encodings

def get_bowling_innings_encodings(team_name):

    encodings = df[df["bowling_team_name"]==team_name][['bowling_team_name_0', \
    'bowling_team_name_1', 'bowling_team_name_2', \
        'bowling_team_name_3', 'bowling_team_name_4', \
            'bowling_team_name_5', 'bowling_team_name_6']].iloc[0].values
    return encodings

def get_batsman_encodings(batsman_name):

    encodings = df[df["batsman"]==batsman_name][['batsman_0', 'batsman_1', \
    'batsman_2', 'batsman_3', 'batsman_4', 'batsman_5', 'batsman_6', \
    'batsman_7', 'batsman_8', 'batsman_9', 'batsman_10', 'batsman_11']].iloc[0].values
    return encodings

def get_bowler_encodings(bowler_name):

    encodings = df[df["bowler"]==bowler_name][['bowler_0', 'bowler_1', 'bowler_2', \
    'bowler_3', 'bowler_4', 'bowler_5', 'bowler_6', 'bowler_7', 'bowler_8', \
    'bowler_9', 'bowler_10']].iloc[0].values
    return encodings

def get_non_striker_encodings(non_striker):

    encodings = df[df["non_striker"]==non_striker][['non_striker_0', 'non_striker_1', \
    'non_striker_2', 'non_striker_3', 'non_striker_4', 'non_striker_5', 'non_striker_6', \
    'non_striker_7', 'non_striker_8', 'non_striker_9', 'non_striker_10', 'non_striker_11']].iloc[0].values
    return encodings

def get_super_over_encodings(isSuperOver):
    encodings = df[df["super_over"]==isSuperOver][['super_over_0', 'super_over_1']].iloc[0].values
    return encodings

def get_batting_experience(batsman):
    encodings = df[df["batsman"]==batsman][['batting_experience_0',\
         'batting_experience_1']].iloc[0].values
    return encodings

def get_out_batsman_encoding(batsman):

    df[df["out_batsman"]==batsman][['out_batsman_0', 'out_batsman_1', 
    'out_batsman_2', 'out_batsman_3', 
    'out_batsman_4', 'out_batsman_5', 'out_batsman_6', 'out_batsman_7', 
    'out_batsman_8', 'out_batsman_9', 'out_batsman_10', 'out_batsman_11']].iloc[0].values

def get_bowler_experience(bowler):
    encodings = df[df["bowler"]==bowler][['bowler_experience_0', \
        'bowler_experience_1']].iloc[0].values
    return encodings

def get_batsman_stats(batsman):
    explosivity_rating =  df[df["batsman"]==batsman]["explosivity"].iloc[0]
    running_rating = df[df["batsman"]==batsman]["running_rating"].iloc[0]
    powerplay_rating = df[df["batsman"]==batsman]["power_play_rating"].iloc[0]
    end_over_explosivity = df[df["batsman"]==batsman]["end_over_explosivity"].iloc[0]

    return explosivity_rating,running_rating,powerplay_rating,end_over_explosivity

def get_bowler_stats(bowler):

    wicket_taking_rating =  df[df["batsman"]==bowler]["wicket_taking_rating"].iloc[0]
    bowling_consistency_rating = df[df["batsman"]==bowler]["bowling_consistency_rating"].iloc[0]
    return wicket_taking_rating,bowling_consistency_rating