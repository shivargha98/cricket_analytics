import pandas as pd
import numpy as np
import category_encoders as ce
from tqdm import tqdm

df2 = pd.read_csv("/home/shivargha/cricket_analytics/T20_cricket/t20is3.csv")


####################### Features Selected for ML Models ###############################
"""
'venue', 'current_innings', 'innings_type',bowling_team_name,
'over', 
'batsman', 'non_striker', 'bowler',
'curr_score', 'curr_wickers',
'current_run_rate', 'req_run_rate',
'super_over','batsman_score', runs_conceded_by_bowler
'balls_faced_batsman', 'batsman_strike_rate',
'balls_bowled_bowler', 'wickets_by_bower',
'bowler_economy', 'batsman_prop0', 'batsman_prop1', 'batsman_prop2',
'batsman_prop3', 'batsman_prop4', 'batsman_prop5', 'batsman_prop6',
'batsman_prop7', 'bowler_prop0', 'bowler_prop1', 'bowler_prop2',
'bowler_prop3', 'bowler_prop4', 'bowler_prop5', 'bowler_prop6',
'bowler_prop7', 'bowler_prop8', 'explosivity', 'running_rating',
'power_play_rating', 'end_over_explosivity', 'batting_experience',
'wicket_taking_rating', 'bowling_consistency_rating',
'bowler_experience'  --->>>>  predicts (batsman runs)
"""
#########################################################################################

#### creating a binary feature encoder #####
def binary_feature_encoder(column_name:str):
    
    df_col = pd.DataFrame(df2[column_name])
    encoder = ce.BinaryEncoder(cols=[column_name],return_df=True)
    data_encoded = encoder.fit_transform(df_col) 
    return data_encoded


################  Converting Categorical Columns ##############
## -->> venue,current_innings,innings_type,bowling_team_name
## -->> batsman,non_striker,bowler,super_over
## -->> batting_experience,bowler_experience

venue_df_encoded = binary_feature_encoder("venue")
curr_innings_df_encoded = binary_feature_encoder("current_innings")
bowling_team_df_encoded = binary_feature_encoder("bowling_team_name")
innings_type_df_encoded = binary_feature_encoder("innings_type")
batsman_df_encoded = binary_feature_encoder("batsman")
bowler_df_encoded = binary_feature_encoder("bowler")
non_striker_df_encoded = binary_feature_encoder("non_striker")
super_over_df_encoded = binary_feature_encoder("super_over")
batting_exp_df_encoded = binary_feature_encoder("batting_experience")
bowling_exp_df_encoded = binary_feature_encoder("bowler_experience")
out_batsman_df_encoded = binary_feature_encoder("out_batsman")
#################################################################


################ Getting all the numerical Features ####################
df_num_data = df2[["over","curr_score","curr_wickers",'current_run_rate', 'req_run_rate',\
    'batsman_score', 'balls_faced_batsman',\
    'batsman_strike_rate',"runs_conceded_by_bowler",
    'balls_bowled_bowler', 'wickets_by_bower',\
    'bowler_economy', 'batsman_prop0', 'batsman_prop1', 'batsman_prop2',\
    'batsman_prop3', 'batsman_prop4', 'batsman_prop5', 'batsman_prop6',\
    'batsman_prop7', 'bowler_prop0', 'bowler_prop1', 'bowler_prop2',\
    'bowler_prop3', 'bowler_prop4', 'bowler_prop5', 'bowler_prop6',\
    'bowler_prop7', 'bowler_prop8', 'explosivity', 'running_rating',\
    'power_play_rating', 'end_over_explosivity',\
    'wicket_taking_rating', 'bowling_consistency_rating']].copy()
########################################################################

##Run Out/Obstructing the field  Considered here as bowler's wicker for simplicity###
non_bowler_type = ["None","retired hurt","retired out","retired not out"]
bowler_out_type = []
for out in df2["dismissal_type"].unique():
    if out not in non_bowler_type:
        bowler_out_type.append(out)

#bowler out types -->> ['lbw','run out','caught','bowled','caught and bowled','stumped','hit wicket',\
# 'obstructing the field']

############# Creating the Labels #################
'''
As Maximum Run by a batsman is 7, hence considering Wicket as 8
'''
outcome_labels = []
for row in tqdm(range(len(df2))):
    
    out,out_type = df2.iloc[row]["out"],df2.iloc[row]["dismissal_type"]
    batsman_runs = df2.iloc[row]["batsman_runs"]
    #print(out)
    if out == "Yes":
        if out_type in bowler_out_type:
            outcome_labels.append(8)
        else:
            outcome_labels.append(0)
    else:
        outcome_labels.append(batsman_runs)


final_trainable_df = pd.concat([venue_df_encoded, curr_innings_df_encoded,\
                             bowling_team_df_encoded,innings_type_df_encoded,\
                              batsman_df_encoded,bowler_df_encoded,non_striker_df_encoded,\
                              super_over_df_encoded, batting_exp_df_encoded,\
                              bowling_exp_df_encoded,\
                            out_batsman_df_encoded,df_num_data], axis=1)

final_trainable_df["outcome"] = outcome_labels

final_trainable_df.to_csv("/home/shivargha/cricket_analytics/cricket_score_simulator/Final_T20_trainable.csv",\
                    index=False)





