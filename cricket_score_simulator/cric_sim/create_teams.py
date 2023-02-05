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
