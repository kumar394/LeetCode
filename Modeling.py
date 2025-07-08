# This file has modelling codes that will be used in model building

# The following code is load/deploy model binary file on DBT platform
{{
    config(
        materialized = 'model',
        tags = ['dbt_tag'],
        ml_config = {
            "model_type": "xgboost",
            "model_path": "cloud_location"
        },
    )
}}

# The following code is to generate scores from the model file
SELECT predicted_label AS model_score
FROM {{dbt_ml.predict(ref('dbt_model_name'), ref('data_table')) }}

def data_prelim_stats(df, num, cat):

    total = df.shape[0]

    df_num = df[num]
    df_cat = df[cat]

    # stats for numeric features
    df_out_num = pd.DataFrame()
    Feat = []
    Missing = []
    Not_Missing = []
    Missing_Percentage= []
    Max = []
    Min = []
    Mean = []
    P_1 = []
    P_99 = []
    Standard_Dev = []

    for i in num:
        Feat.append(i)
        Missing.append(df_num[i].isna().sum())
        Not_Missing.append(total - df_num[i].isna().sum())
        Missing_Percentage.append((df_num[i].isna().sum())/total*100)
        Max.append(df_num[i].max())
        Min.append(df_num[i].min())
        Mean.append(df_num[i].mean())
        P_1.append(df_num[i].quantile(0.01))
        P_99.append(df_num[i].quantile(0.99))
        Standard_Dev.append(df_num[i].std())


    # save the output in a dataframe
    df_out_num["NumericFeatures"] = Feat
    df_out_num["MissingCount"] = Missing
    df_out_num["DataAvailable"] = Not_Missing
    df_out_num["MissingPercentage"] = Missing_Percentage
    df_out_num["Max"] = Max
    df_out_num["Min"] = Min
    df_out_num["Mean"] = Mean
    df_out_num["P_1"] = P_1
    df_out_num["P_99"] = P_99
    df_out_num["Std"] = Standard_Dev


    # stats for categorical features
    df_out_cat = pd.DataFrame()
    Cat_Feat=[]
    Cat_Unique = []
    Cat_DataAvailable = []
    Cat_Percentage = []
    Cat_Missing_Val = []
    Cat_Missing_Val_Per = []
    cat_n = 5 
    top_freq = []
    
    for i in cat:
        Cat_Feat.append(i)
        Cat_Unique.append(df_cat[i].nunique())
        Cat_DataAvailable.append(total - df_cat[i].isna().sum())
        Cat_Percentage.append(df_cat[i].isna().sum()/total*100)
        Cat_Missing_Val.append(df_cat[i].isna().sum())
        Cat_Missing_Val_Per.append(df_cat[i].isna().sum()/total*100)
        top_freq.append(df_cat[i].value_counts()[:cat_n].index.tolist())

    # save the output
    df_out_cat

        _




