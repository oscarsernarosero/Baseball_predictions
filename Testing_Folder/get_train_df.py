from path import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
from pybaseball import batting_stats
from pybaseball import batting_stats_range
from pybaseball import pitching_stats_range
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report
from pybaseball import schedule_and_record
import re
from pybaseball import pitching_stats
import datetime as dt
import col_handeler as col


###########  MOVE THIS TO ANOTHER .PY FILE  ##################
team_dict = {'Angels':'LAA',
            'Athletics': 'OAK',
            'Astros': 'HOU',
            'Braves': 'ATL',
            'Brewers': 'MIL',
            'Cards': 'STL',
            'Cubs': 'CHC',
            'Diamondbacks': 'ARI',
            'Dodgers': 'LAD',
            'Giants': 'SFG',
            'Indians': 'CLE',
            'Blue Jays': 'TOR',
            'Mariners': 'SEA',
            'Marlins': 'MIA',
            'Mets': 'NYM',
            'Nats': 'WSN',
            'Orioles': 'BAL',
            'Padres': 'SDP',
            'Phillies': 'PHI',
            'Pirates': 'PIT',
            'Rangers': 'TEX',
            'Rays': 'TBR',
            'Red Sox': 'BOS',
            'Reds': 'CIN',
            'Rockies': 'COL',
            'Royals': 'KCR',
            'Tigers': 'DET',
            'Twins': 'MIN',
            'White_Sox': 'CHW',
            'Yankees': 'NYY'
             
           }
def get_key_from_dict(dictionary, val): 
    for key, value in dictionary.items(): 
         if val == value: 
            return key 
            
def switch_key_val_dict(dictionary): 
    new_dict = {}
    
    for key, value in dictionary.items():
        new_dict.update({value:key})
    
    return new_dict 

acr_team_dict = {}
acr_team_dict.update({'CHC':'CUB'})
#acr_team_dict.update({'LAD':'LAD'})
acr_team_dict.update({'SFG':'SFO'})
acr_team_dict.update({'SDP':'SDG'})
acr_team_dict.update({'TBR':'TAM'} )
acr_team_dict.update({'KCR':'KAN'})
acr_team_dict.update({'CHW':'CWS'})

################################################################

def format_dates_to_dt(un_date="Monday, Dec 31", year=1999):
    date = re.findall(r"\W\w\w\w\s\d+", un_date)
    date = date[0]
    date = str(year) + date
    date_formatted = dt.datetime.strptime(date,"%Y %b %d")
    return date_formatted
    
def modify_dates_from_lineups(date="1. Thu,3/29 at TEX W (4-1)#", year = 2018):
    date = re.findall(r"\d+/\d+", date)
    try: date = date[0]
    except: return
    date = str(year) +" " + date
    return date
    
    
def modify_date_col_from_lineups(df, year):
    df["0"] = df.apply(lambda x: modify_dates_from_lineups(x["0"],year), axis=1)
    df["0"] = pd.to_datetime(df["0"])
    return df
    
    
def clean_lineups(df):
    
#Version 2: Find unique names and replace them by the desired
#format all at once instead of replacing one single name at a time in the table.

#convert manually portion of df in a list to later get unique names through set()
    rows = []
    for row in range(0,len(df)):
        temp = [*df.iloc[row,2:11]]
        for x in temp:
            rows.append(x)
            
    #finding the different unique names in the df        
    original_names = set(rows)
    
    #Replacing all the cells that share the same name with the desired format all at once
    #to avoid unnecesary repetition of the work going cell by cell spliting and replacing. 
    for name in original_names:
        real_name = name.split("-")
        real_name = real_name[0]
        df.replace(name,real_name, inplace=True)
        
    return df  
    
    
def format_lineups_df(df, year):
    df  =  modify_date_col_from_lineups(df, year)
    #print("Time version 2:\n")
    #%timeit d_f1 = clean_lineups(df)
    d_f1 = clean_lineups(df)
    #print("Time version 0:\n")
    #%timeit d_f2 = clean_lineups_v0(df)
    d_f1.columns = ["index","Date","1","2","3","4","5","6","7","8","9"]
    d_f1.set_index("index", inplace=True, drop=True)
    return df
    
def get_dates_played(df=None,year=None):
    
    dates_played = [format_dates_to_dt(date, year) for date in df.Date]
    return dates_played
    
    
def get_team_schedule(year=None, team = "HOU"):
    
    try: teams_df  = schedule_and_record(year, team)
    except: 
        message: "Not able to get_team_schedule()"
        print(message)
        return message
    teams_df  = teams_df.iloc[ : , [0,1,2,3,4,10,17] ]
    teams_df["Date"] = teams_df.apply(lambda x: format_dates_to_dt(x["Date"],year), axis=1)
    teams_df.replace("@",1, inplace=True)
    teams_df.replace("Home",0, inplace=True)
    return teams_df
    
    
def get_players_per_game(year = None, team = None, line_ups_dict = None):
    
    
    
    schedule_df = get_team_schedule(year, team)
    if(type(schedule_df)=="str"): return schedule_df
    else: print(f"Dates played by {team} downloaded successfully...")
    
   
  
    opponents = set(schedule_df["Opp"])
    
    bat_stat_path = Path(f"../Data/Batting/Clean_Data/clean_batting_data_{year}.csv")
    all_bat_stats = pd.read_csv(bat_stat_path)
    
    pitchers_path = Path(f"Starting_Pitchers/Starting_Pitchers_{year}.csv")
    starting_pitchers = pd.read_csv(pitchers_path)
    #print(f"head of PITCHER STATS: \n{starting_pitchers.head()}")
    
    if line_ups_dict == None:
        
        lineups_path = Path(f"Lineups/{team}_lineups_{year}.csv")
        all_lineups_season = pd.read_csv(lineups_path)
        all_lineups_season = format_lineups_df(all_lineups_season, year)

        opponents_lineups = {}
        for opponent in opponents:
            opp_lineups_path = Path(f"Lineups/{opponent}_lineups_{year}.csv")
            opp_all_lineups_season = pd.read_csv(opp_lineups_path)
            #print(f"Reading CSV for: {opponent} successfully....")
            opp_all_lineups_season = format_lineups_df(opp_all_lineups_season, year)
            opponents_lineups.update({opponent:opp_all_lineups_season})
    else:
        all_lineups_season = line_ups_dict[team]
        
        opponents_lineups = {}
        for opponent in opponents:
            opponents_lineups.update({opponent:line_ups_dict[opponent]})
            
            
    
    players_df = pd.DataFrame()
    
    i = 0
    for date in schedule_df["Date"]:
        
        
        adversary = schedule_df[schedule_df["Date"]==date.strftime("%Y-%m-%d")]["Opp"].values[0]
        
        
        
        temp_dict = {"Date":date}

        ##Line ups for the team
        try: all_players_on_date = all_lineups_season[all_lineups_season["Date"]==date.strftime("%Y-%m-%d")]
            
        except:
            print(f"No game on this date {date} for team")
            continue
            
        count = 1  
        #print(f"ALL PLAYERS ON DATE:\n{all_players_on_date}")
        if len(all_players_on_date)==0: continue
        else: 
            all_players_team = all_players_on_date.iloc[0]
            for player in all_players_team[1:]:            
                temp_dict.update({f"player_{count:02}" : player})           
                count+=1
        
        ##Line ups for the adversary
        try:
            opp_lineups_df = opponents_lineups[adversary]
            all_opponents_on_date = opp_lineups_df[opp_lineups_df["Date"]==date.strftime("%Y-%m-%d")]
            all_opponents_on_date.columns = ["Date","10","11","12","12","14","15","16","17","18"]
        except:
            print(f"No game on this date {date} for opponent")
            continue

        count = 10  
        if len(all_opponents_on_date)==0: continue
        else: 
            all_players_opp = all_opponents_on_date.iloc[0]       
            for enemy in all_players_opp[1:]:            
                temp_dict.update({f"player_{count:02}" : enemy})           
                count+=1
         
        pitcher_on_date = starting_pitchers[starting_pitchers["Date"]==date.strftime("%Y-%m-%d")]
        #print(f"PITCHERS ON DATE: \n{pitcher_on_date}")    
        if team in acr_team_dict.keys():
                team = acr_team_dict[team]
        
        try:
            team_pitcher = pitcher_on_date[pitcher_on_date["Team"]==team]["PITCHER"].values[0]
            #print(f"TEAM PITCHER: \n{team_pitcher}")   
            temp_dict.update({"pitcher_team": team_pitcher })
        except:
            opponent_pitcher = "Unknown"
            print(f"No pitcher found for {team} on {date}")
            
        
        if adversary in acr_team_dict.keys(): 
            
            adversary = acr_team_dict[adversary]
        
        try:
            opponent_pitcher = pitcher_on_date[pitcher_on_date["Team"]==adversary]["PITCHER"].values[0] 
            #print(f"OPPONENT PITCHER: \n{opponent_pitcher}") 
            temp_dict.update({"pitcher_opp": opponent_pitcher})
        except:
            print(f"No pitcher found for {adversary} on {date}")
            opponent_pitcher = "Unknown"
        
        temp_df = pd.DataFrame(temp_dict, index =[i])
        players_df = pd.concat([players_df,temp_df], axis=0, sort = True )
        i+=1
        
    schedule_df.drop_duplicates(inplace = True)
    schedule_df.set_index("Date", inplace=True)
    players_df.drop_duplicates(inplace = True)
    players_df.set_index("Date", inplace=True)
    
    teams_df = pd.concat([schedule_df,players_df], axis=1)
    teams_df.reset_index(inplace=True, drop=False)
    
    return teams_df
    
    
def stats_single_game_x_team(players=None, names_df = None, team=None, stats_df=None, 
                             counter=1, pitching_stats = False, opponent = False, warnings=False):
    
    all_players_team_stats = pd.DataFrame()
    
    if team in acr_team_dict.keys(): team = acr_team_dict[team]
        
    if str(players[0]) != "nan":
        for player in players:

                if("00:00:00" in str(player)): continue #If it's a date, Skip it.
                if "jr." in player: player = player[:-3]

                try: 
                    
                    current_team_players = names_df[names_df.Team==team]
                    player_full_name = [x for x in current_team_players.Name if player.lower() == x.split(" ")[1].lower() ]
                    if len(player_full_name)>1 and warnings: 
                        print(f"More than one player with this laste name \n{player_full_name}")
                    if len(player_full_name)==0: 
                    # If we couldn't find a player in current season, let's try finding him in stats from last year
                        player_full_name = [x for x in stats_df.Name if (player.lower() in x.lower()) &
                                           (stats_df[stats_df.Team==get_key_from_dict( team_dict ,team )])]
                        if warnings:
                            if len(player_full_name)==0: print(f"We couldn't find player {player}")
                            else: print(f"We found {player} in last year's stats")
                    #print(player_full_name)
                    player_stats = stats_df[stats_df.Name==player_full_name[0]]
                    if len(player_stats)==0: 
                        if warnings: print(f"couldn't find statistics for {player_full_name[0]}")
                    # If we couldn't find statistics x player let's iterate the array pf possible players
                        i=1
                        while (len(player_stats)==0):
                            player_stats = stats_df[stats_df.Name==player_full_name[i]] 
                            if len(player_stats)==1: 
                                if warnings: print(f"We found stats for {player_full_name[i]} instead.")
                            i+=1
                                
                        else: print(f"We found {player} in last year's stats")
                    if len(player_stats["Name"])>1 : 
                        if warnings: 
                            print("More than one player with same name")
                            print(player_stats)
                        player_stats = player_stats[player_stats.Team == get_key_from_dict( team_dict ,team )]
                   
                                        

                except Exception as e: 
                    if warnings: print(f"{player} from {get_key_from_dict( team_dict ,team )}, {team} not in list Pitcher? :{pitching_stats}. \nError: {e}")

                    try:
                        #nanlist = np.empty((1,len(player_stats.columns)))
                        nanlist = np.empty((1,len(stats_df.columns)))
                    except Exception as e:
                        if warnings: print(f"Not able to get columns from last player\n{e}")
                        continue
                    nanlist.fill(np.nan)
                    fake_columns = stats_df.columns
                    player_stats = pd.DataFrame(data = nanlist, columns = fake_columns)
                    #player_stats.drop(columns=["index"], inplace=True)

                new_col = []
                for col in player_stats.columns:
                    if pitching_stats: 
                        if opponent: new_col.append(f"opponet_pitcher_{col}")
                        else: new_col.append(f"team_pitcher_{col}")
                    else: new_col.append(f"{counter:02}_{col}")
                player_stats.columns = new_col
                player_stats.reset_index(inplace=True, drop=True)
                all_players_team_stats = pd.concat([ all_players_team_stats, player_stats ] ,   axis=1)

                counter+=1
                
    else:
        print(f"Received not a string as a player ({type(players)})\n{players}")
        try:
            nanlist = np.empty((1,len(stats_df.columns)))
        except Exception as e:
            print(f"Not able to get columns from last player\n{e}")
            return 
            
        nanlist.fill(np.nan)
        fake_columns = stats_df.columns
        player_stats = pd.DataFrame(data = nanlist, columns = fake_columns)
        
        new_col = []
        for col in player_stats.columns:
            if pitching_stats: 
                if opponent: new_col.append(f"opponet_pitcher_{col}")
                else: new_col.append(f"team_pitcher_{col}")
            else: new_col.append(f"{counter:02}_{col}")
        player_stats.columns = new_col
        player_stats.reset_index(inplace=True)
        all_players_team_stats = pd.concat([ all_players_team_stats, player_stats ] ,   axis=1)

        counter+=1

            
    return all_players_team_stats
    
    
def get_stats_startingplayer_by_game(players_df=None, team=None, batting_season_data=None,pitching_season_data=None, year=None, warnings=False):
    
    if batting_season_data.empty: batting_season_data = batting_stats(year-1)   
    if pitching_season_data.empty: pitching_season_data = pitching_stats(year-1)
    print("stats loaded")
    
    bat_names_path = Path(f"../Data/Batting/Clean_Data/clean_batting_data_{year}.csv")
    all_bat_names = pd.read_csv(bat_names_path)
    
    pitch_names_path = Path(f"../Data/Pitching/Clean_Data/clean_pitching_data_{year}.csv")
    all_pitch_names = pd.read_csv(pitch_names_path)
    #names_teams_current_season = batting_stats(year)
    #pitchers_teams_current_season = pitching_stats(year)    
    print("names loaded")
    
    names_teams_current_season = all_bat_names[["Date","Name","Tm"]]  
    names_teams_current_season.columns = ["Date","Name","Team"]
    #print(names_teams_current_season.head())
    pitchers_teams_current_season = all_pitch_names[["Date","Name","Tm"]]
    pitchers_teams_current_season.columns = ["Date","Name","Team"]
    #print(pitchers_teams_current_season.head())
    
    #print(pitching_season_data.head()) 
    
    stats_players_start_lineup = pd.DataFrame()
    print("starting concatenating df..")
    for row in range(0,len(players_df)):
        
        all_players_stats = pd.DataFrame()
       
        date_x=players_df.iloc[row][0]
        all_players_team_stats = stats_single_game_x_team(players = players_df.iloc[row][9:18],
                                                          names_df = names_teams_current_season[names_teams_current_season["Date"]==
                                                                                               date_x.strftime("%Y-%m-%d")],
                                                                  team = team, 
                                                                  stats_df = batting_season_data)
        
        #print("names_df for team pitchers:\n")
        #print(pitchers_teams_current_season[pitchers_teams_current_season["Date"]==date_x.strftime("%Y-%m-%d")])
        pitcher_team = stats_single_game_x_team(players = [players_df.iloc[row][8]],
                                                          names_df = pitchers_teams_current_season[pitchers_teams_current_season["Date"]==
                                                                                               date_x.strftime("%Y-%m-%d")],
                                                                  team = team, 
                                                                  stats_df = pitching_season_data,
                                                           pitching_stats = True)
        
        
        #print("names_df for opponent batters:\n")
        #print(names_teams_current_season[names_teams_current_season["Date"]==date_x.strftime("%Y-%m-%d")])  
        all_players_opp_stats = stats_single_game_x_team(players = players_df.iloc[row][18:], 
                                                       names_df = names_teams_current_season[names_teams_current_season["Date"]==
                                                                                               date_x.strftime("%Y-%m-%d")],
                                                                  team = players_df.iloc[row][3], 
                                                                  stats_df = batting_season_data,
                                                                  counter = 10)     
        
        #print("names_df for opponent pitchers:\n")
        #print(pitchers_teams_current_season[pitchers_teams_current_season["Date"]==date_x.strftime("%Y-%m-%d")])
        pitcher_opp = stats_single_game_x_team(players = [players_df.iloc[row][7]],
                                                          names_df = pitchers_teams_current_season[pitchers_teams_current_season["Date"]==
                                                                                               date_x.strftime("%Y-%m-%d")],
                                                                  team = players_df.iloc[row][3], 
                                                                  stats_df = pitching_season_data,
                                                           pitching_stats = True,
                                                           opponent = True)
        
        
        try:
            all_players_stats = pd.concat([ all_players_team_stats, 
                                           pitcher_team,
                                           all_players_opp_stats,
                                           pitcher_opp] ,  
                                          axis=1)   

        except Exception as e: 
            print(f"could not concatenate stats\n{e}")
            continue
            
        try: 
            stats_players_start_lineup = stats_players_start_lineup.append(all_players_stats, ignore_index=True)
        except Exception as e: 
            print(f"could not append {e}")
            print(f"explanation: \n{col.get_col_explanation(stats_players_start_lineup.columns,all_players_stats.columns)}")
            
            continue
        
    
    return stats_players_start_lineup
    

    
def create_trining_df(year = (dt.datetime.today().year-1), team = "HOU" , batting_season_data=None,
                      pitching_season_data=None, line_ups_dict = None):
                       
    
    if line_ups_dict == None:   players_df = get_players_per_game(year, team)
    else:                       players_df = get_players_per_game(year, team, line_ups_dict)
        
    if type(players_df)=="str": return players_df
    else: print(f"List of names for players from {team} for every game in {year} successfully created...")
    #print(players_df.tail(10))    
    
    stats_players_start_lineup = get_stats_startingplayer_by_game(players_df = players_df, 
                                                                  batting_season_data = batting_season_data,
                                                                  pitching_season_data = pitching_season_data,
                                                                  team =team, year = year)
    
    return pd.concat([players_df.iloc[:,[4,0,1,2,3,5,6]],stats_players_start_lineup], axis=1, join='inner')
        

    
    
    
def clean_baseball_stats_df(data_frame=None):
  
    df = data_frame.copy()
    #set date as index
    try: df.set_index("Date", inplace=True, drop=True)
    except: 
        print("Could not set Date as index. Maybe it already is?")
        pass
    df.replace(np.nan, 0, inplace =True)
    
    df.replace("W-wo","W", inplace = True)
    df.replace("L-wo","L", inplace = True)
    #df[["W/L","GB"]].replace("W",1, inplace=True)
    #df[["W/L","GB"]].replace("L",0, inplace=True)
    
    #drop col with (pfx) as discovered in earlier.
    pfx_col = [x for x in df.columns if "(pfx)" in x ]
    
    #drop col with Age since they are not relevant.
    age_col = [x for x in df.columns if "Age" in x ]
    
    #drop col when they have scalars but others have the same expressed in percentage.
    col_not_to_drop = [x for x in df.columns if "%" in x and x[:-1] in df.columns]
    not_perc_col = [x[:-1] for x in col_not_to_drop]
    
    #Drop columns that have Name, index, Season 
    #name_cols = col.get_col_contains(name="Name", columns=df.columns)
    index_cols = col.get_col_contains(name="index", columns=df.columns)
    team_cols = col.get_col_contains(name="Team", columns=df.columns)
    Season_cols = col.get_col_contains(name="Season", columns=df.columns)
    
    #Drop columns Team, Opp
    specific_col = ["GB"]
    

    
    cols_to_drop =[ *pfx_col, *not_perc_col,*index_cols, *team_cols,
                   *Season_cols,*age_col,*specific_col]
    
    
    

    
    df.drop(columns=cols_to_drop, inplace=True)
    
    
    return df
    
def create_global_train_df(year=2019):
    
    #downlaoding the batting and pitching statistics from preveous year
    batting_season_data = batting_stats(year-1)   
    pitching_season_data = pitching_stats(year-1)
    print("Statistics downloaded successfully...")
    
    #reading line ups for every team in the year and storing it in a dictionary.
    line_ups_dict = {}
    
    for key, val in team_dict.items():
        
        lineups_path = Path(f"Lineups/{val}_lineups_{year}.csv")
        lineups_season = pd.read_csv(lineups_path)
        print(f"Reading CSV for: {val} successfully....")
        lineups_season = format_lineups_df(lineups_season, year)
        line_ups_dict.update({val:lineups_season})
    
    #creating the global training dataframe
    global_training_df = pd.DataFrame()
    for key, val in team_dict.items():
        print(val)
        training_df_team = create_trining_df(year=year, team = val,
                                             batting_season_data =  batting_season_data,
                                             pitching_season_data = pitching_season_data,
                                             line_ups_dict = line_ups_dict)
        
        if type( training_df_team )  ==  "str" : 
            print("Training Datframe failed. -----------\n\n")
            print( training_df_team ) 
            continue
        global_training_df = pd.concat([global_training_df,training_df_team], axis=0, sort =False)
        
    global_training_df.sort_index(axis=0,inplace=True)
    clean_global_df = global_training_df.copy()
    clean_global_df = clean_baseball_stats_df(clean_global_df)
    clean_global_df.sort_index(axis=0,inplace=True)
    
    return clean_global_df, global_training_df
    
    
    
def create_all_training_df(start_year,final_year):
    
    for year in range( start_year, final_year+1):
        
        global_training_df, raw_training_df = create_global_train_df(year)
        
        raw_training_df.set_index("Date", inplace = True)
        
        raw_path = Path(f"training_dataframes/raw_{year}.csv")
        raw_training_df.to_csv(raw_path)
        
        clean_path = Path(f"training_dataframes/clean_{year}.csv")
        global_training_df.to_csv(clean_path)
        
##########EXAMPLE##########
#create_all_training_df(2017,2019)