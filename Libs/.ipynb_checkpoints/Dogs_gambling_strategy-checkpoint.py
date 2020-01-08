import pandas as pd

def dog_strategy(df=None, perc_strategy=None, bet_amount=None, total_budget=None):
    """This function will take the predictions vs actual dataframe that resulted from our RandomForestClassifier model.  It will return a dataframe detailing the profit/loss of our gambling
       strategy of only betting on underdogs that our model predicts to win.
       Arg:
       df: Dataframe with the predictions vs actual.
       bet_amount: amount to bet on each game.
       perc_strategy: percentage that the bet_amount represent of the total betting budget. MUST BE REPRESENTED IN %.
       So, for instance, for a 2.5 % put 2.5 for perc_strategy. for a 10 % simply put 10.
       """
    
    #variable validation:
    
    if df.empty or perc_strategy==None or (bet_amount==None and total_budget==None):
        return "Missing arguments. You must pass all the arguments. You can either skip bet_amount or total_budget, but not both"
    if (bet_amount == None) and (total_budget!=None):
        bet_amount = total_budget*(perc_strategy/100)
        
    elif (bet_amount != None) and (total_budget==None):
        total_budget = bet_amount/(perc_strategy/100)
    
    elif (bet_amount != None) and (total_budget!=None):
        if bet_amount != total_budget*(perc_strategy/100):
            return f"bet_amount {bet_amount}, perc_strategy {perc_strategy}, and total_budget {total_budget} don't match."
    

    winner = []
    loser = []
    prediction = []
    date = []
    previous_bankroll = [total_budget]
    current_bankroll = [total_budget]
    profit_loss = [0]
    current_bet = [0]
    total_profit_loss = [0]
    total_winnings = [0]
    
    for index, row in df.iterrows():
        if row['Home_Open_Odds'] > 0 and row['Predicted'] == 1:
            if row['Actual'] == row['Predicted']:
                current_bet.append(bet_amount)#to revise
                previous_bankroll.append(current_bankroll[-1])
                profit_loss.append(row['Home_Open_Odds']*(bet_amount/100))#to revise
                total_profit_loss.append(total_profit_loss[-1] + profit_loss[-1])
                current_bankroll.append(previous_bankroll[-1] + profit_loss[-1])
                date.append(index)
                winner.append(row['Home'])
                loser.append(row['Visitor'])
                prediction.append(row['Home'])
            else:
                current_bet.append(bet_amount)
                previous_bankroll.append(current_bankroll[-1])
                profit_loss.append(-bet_amount)#to revise
                total_profit_loss.append(total_profit_loss[-1] + profit_loss[-1])
                current_bankroll.append(previous_bankroll[-1] + profit_loss[-1])
                date.append(index)
                winner.append(row['Visitor'])
                loser.append(row['Home'])
                prediction.append(row['Visitor'])
        elif row['Visitor_Open_Odds'] > 0 and row['Predicted'] == 0:
            if row['Actual'] == row['Predicted']:
                current_bet.append(bet_amount)#to revise
                previous_bankroll.append(current_bankroll[-1])
                profit_loss.append(row['Visitor_Open_Odds']*(bet_amount/100))#to revise
                total_profit_loss.append(total_profit_loss[-1] + profit_loss[-1])
                current_bankroll.append(previous_bankroll[-1] + profit_loss[-1])
                date.append(index)
                winner.append(row['Visitor'])
                loser.append(row['Home'])
                prediction.append(row['Visitor'])
            else:
                current_bet.append(bet_amount)
                previous_bankroll.append(current_bankroll[-1])
                profit_loss.append(-bet_amount)#to revise
                total_profit_loss.append(total_profit_loss[-1] + profit_loss[-1])
                current_bankroll.append(previous_bankroll[-1] + profit_loss[-1])
                date.append(index)
                winner.append(row['Home'])
                loser.append(row['Visitor'])
                prediction.append(row['Visitor'])
    results_df = pd.DataFrame([date, winner, loser, prediction, current_bet[1:], previous_bankroll[1:], profit_loss[1:], total_profit_loss[1:], current_bankroll[1:]]).T
    results_df.columns = ['Date', 'Winner', 'Loser', 'Prediction', 'Current_Bet', 'Previous_Bankroll', 'Profit_Loss', 'Total_Profit_Loss', 'Current_Bankroll']
    results_df = results_df.set_index('Date')
    return results_df