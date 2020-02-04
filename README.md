# BASEBALL PREDICTION   

This project is an on going project developed as part of the Rice Fintec Bootcamp.

This project automatically extracts information trhough web scraping and APIs to build a dataframe with the statistics of each player that is later filtered and used to predict who is going to be the winner in a particualr baseball game.

The way this data analysis is carried out is by gathering statistical historical data of each player in the starting lineups of the each team that will be used later to train a machin learning model. 

To make use of the project, simply navigate to the jupyter notebook in Testing_Folder/Models.ipynb and make use of the function run_model().

The parameters and their default values are:

run_model(year=2019, model_type = "randomforest", save_model = False, pca = False)

Parameters

year: the year of the model to be trained. It will only use half of the season.

model_type: string. "randomforest" or "svm" are the only options for right now.

save_model: boolean. If you want to store your model and the results set this value to True.

pca: boolean. If you wish to run a Principal Component Analysis on the data set this value to True.

So far, the best models are random forests with an accuracy of 58% ~ 59%.

The models are store in a folder inside Testing_Folder called "Models".