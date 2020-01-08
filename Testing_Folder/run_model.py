from path import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import os
import pickle
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import col_handeler as col


def get_training_df(year):
    
    training_path = Path(f"training_dataframes/clean_{year}.csv")
    train_df = pd.read_csv(training_path, index_col = "Date", infer_datetime_format = True)
    
    return train_df
    
    
def get_xy(df):
    
    #getting team for future verification purposes
    team_df = df[["Tm","Opp"]]
    
    #getting X
    X = df.copy()
    X.drop(columns = ["W/L",], inplace = True)
    
    #Getting y
    y = df["W/L"]
    
    #Cleanning X
    string_col = [x for x in X.columns if X[x].dtype == "O" or X[x].dtype == "str"]
    X.drop(columns = string_col, inplace = True)
    
    return {"X":X, "y":y,"Team":team_df}  
    
    
def traintestsplit(X,y,team_df, split_at = 0.5):
   
    mid = int(X.shape[0]*split_at)
    
    #Train
    X_train = X[ : mid]
    y_train = y[ : mid]
    team_df_train = team_df[ : mid]
    
    #test
    X_test = X[mid : ]
    y_test = y[mid : ] 
    team_df_test = team_df[mid : ]
    
    return {"X_train":X_train, "y_train":y_train, "Team_train":team_df_train,
           "X_test":X_test, "y_test":y_test, "Team_test":team_df_test}    
           
           
def random_forest(X_train,y_train,X_test):
    
    rand_for_clf = RandomForestClassifier(n_estimators = 1000, min_samples_split = 4, 
                                      max_leaf_nodes = 10, max_depth = 25)
    
    rand_for_clf.fit(X_train,y_train)
    
    return {"model":rand_for_clf,
            "y_pred":rand_for_clf.predict(X_test),
            "feature_importance":
            pd.Series(rand_for_clf.feature_importances_,index=X_train.columns).sort_values(ascending=False)
           }    
           
           
def svm(X_train,y_train,X_test):
    svm = Pipeline((
    ("scaler", StandardScaler()),
    ("svm_clf", SVC(kernel = "poly", degree = 4, coef0=1.5, C=30, gamma = "auto"))
    ))
    svm.fit(X_train,y_train)
    
    return {"model":svm,
            "y_pred":svm.predict(X_test)}
            
    
    
def process_feat_imp(feature_imp):

    imp_features = set(col.get_raw_col(feature_imp.index.values))

    relevance_raw_feat = []
    for feat in imp_features:

        if feat == "Streak": stats = ["Streak"]
        else: 

            stats = [x for x in feature_imp.index if (feat == x[3:] or 
                                                      x == "team_"+feat or 
                                                      x == "opponet_"+feat or
                                                      x == "Home_"+feat   )]


        batter_stats = [x for x in stats 
                        if (x.startswith("01_") or x.startswith("02_") or x.startswith("03_") or x.startswith("04_") or 
                            x.startswith("05_") or x.startswith("06_") or x.startswith("07_") or x.startswith("08_") or
                            x.startswith("09_") or x.startswith("10_") or x.startswith("11_") or x.startswith("12_") or
                            x.startswith("13_") or x.startswith("14_") or x.startswith("15_") or x.startswith("16_") or
                            x.startswith("17_") or x.startswith("18_"))]

        pitcher_stats = [x for x in stats if x.startswith("team_pitcher_") or x.startswith("opponet_pitcher_") ]

        total_relevance = 0
        if len(batter_stats)>0:
            kind = "Batter"
            for stat in batter_stats: total_relevance += feature_imp[stat]
            relevance_raw_feat.append([feat,total_relevance, kind])   

        total_relevance = 0
        if len(pitcher_stats)>0: 
            kind = "Pitcher"
            for stat in pitcher_stats: total_relevance += feature_imp[stat]
            relevance_raw_feat.append([feat,total_relevance, kind]) 

        if len(batter_stats)==0 and len(pitcher_stats)==0:
            kind = "Team"

            relevance_raw_feat.append([stats[0],feature_imp[stats[0]], kind])

    relevance_raw_feat = sorted(relevance_raw_feat, key=lambda x: x[1], reverse=True)
    relevance_raw_feat_df = pd.DataFrame(relevance_raw_feat)
    relevance_raw_feat_df.columns = ["Statistic","Importance","Kind of stat"]
    
    return relevance_raw_feat_df
    
    
def store_model(year=2017, model=None, accuracy=0.0, relevance_raw_feat_df=None, 
               predictions_df=None,model_type="randomforest"):
    
    os.makedirs(f"Models/{year}/{model_type}/acc_{accuracy:.5f}")
    
    model_file = f"Models/{year}/{model_type}/acc_{accuracy:.5f}/{model_type}_{accuracy:.5f}.sav"
    pred_file = Path(f"Models/{year}/{model_type}/acc_{accuracy:.5f}/prediction_{accuracy:.5f}.csv")

    pickle.dump(model, open(model_file, 'wb'))
    predictions_df.to_csv(pred_file)
    
    if model_type == "randomforest":
        feat_file = Path(f"Models/{year}/{model_type}/acc_{accuracy:.5f}/randomforest_{accuracy:.5f}_features.csv")
        relevance_raw_feat_df.to_csv(feat_file)


def run_model(year=2019, model_type = "randomforest", save_model = False):
    
    data = get_training_df(year)
    xy_dict = get_xy(data)
    xy_split = traintestsplit( xy_dict["X"] , xy_dict["y"] , xy_dict["Team"], split_at = 0.5 )
          
    if model_type == "randomforest":
        model_dict = random_forest( xy_split["X_train"] , xy_split["y_train"] , xy_split["X_test"] )
        model, y_pred, feat_imp = model_dict["model"],model_dict["y_pred"],model_dict["feature_importance"]
        relevance_raw_feat_df = process_feat_imp(feat_imp)
        print(relevance_raw_feat_df.head(25))
        
    elif model_type == "svm":
        model_dict = svm( xy_split["X_train"] , xy_split["y_train"] , xy_split["X_test"] )
        model, y_pred = model_dict["model"],model_dict["y_pred"]
        
    accuracy = metrics.accuracy_score(xy_split["y_test"], y_pred)
    print(f"accuracy: {accuracy}")
    
    y_test_df = xy_split["y_test"].to_frame()
    predictions_df = pd.concat([xy_split["Team_test"],y_test_df, pd.DataFrame({"predicted":y_pred},index = y_test_df.index)], axis=1,ignore_index=False)
   
    
    if save_model: 
       
        if model_type == "randomforest":
            store_model(year, model , accuracy ,relevance_raw_feat_df, predictions_df ,model_type)
        else:
            store_model(year ,model ,  accuracy ,predictions_df = predictions_df,model_type = model_type )
            
            
##########examples###############
#for x in range(0,10): run_model(2019,"randomforest",True)  
#run_model(2017,"svm",True)  