import pandas as pd
import numpy as np




#move to different module!!!!     
def get_col_explanation(col1,col2):
    print(f"column 1: {col1[:10]}\ncolumn2: {col2[:10]}")
    try: col1 = [x.split("_")[1] for x in col1 if x is not "index"]
    except: pass
    try: col2 = [x.split("_")[1] for x in col2 if x is not "index"]
    except: pass   
    print(f"column 1: {col1[:10]}\ncolumn2: {col2[:10]}")
    if(len(col1)>len(col2)):missing_col = list(set(col1).difference(set(col2)))
    else:missing_col = list(set(col2).difference(set(col1)))
    return missing_col
    
    
#move to different module!!!!   
def get_col_contains(name=None, columns=None, split_criteria = "_"):
   # columns_processed = []
    try: 
        #columns_processed = [x.split(split_criteria)[1] for x in columns if x is not "index"]
        cols = [x for x in columns if name in x]
    except: pass
    return list(cols)
    
    
#move to different module!!!!           
def check_values_in_cols(val=np.nan,col_contains=None, df=None):
    
    cols = get_col_contains(name=col_contains, columns=df.columns)
    names_dataf = df[cols]
    if val==np.nan:
        narows=[index for index in range(0,len(names_dataf)) if
                names_dataf.iloc[index].isna().values.any()]
    else:
        narows=[index for index in range(0,len(names_dataf)) if
                (names_dataf.iloc[index]==val).any()]
    #print(f"NA Rows (total: {len(narows)}): \n{narows}\ntotal: {len(narows)}")
    return names_dataf.iloc[narows]
    
    
#move to different module!!!!              
def get_raw_col(columns):
    
    raw_col = []
    for x in columns:
        
        x = x.split("_")
        if len(x)>1:
            if len(x)>2: raw_col.append("_".join(x[1:]))
            else: raw_col.append(x[1])
                        
        else: raw_col.append(*x)
        
    return raw_col