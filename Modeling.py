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
    df_out_cat["CatFeatures"] = Cat_Feat
    df_out_cat["CatUnique"] = Cat_Unique
    df_out_cat["DataAvailable"] = Cat_DataAvailable
    df_out_cat["CatPercentage"] = Cat_Percentage
    df_out_cat["CatMissing"] = Cat_Missing_Val
    df_out_cat["CatMissingPercentage"] = Cat_Missing_Val_Per
    df_out_cat["CatTop5"] = top_freq

    return df_out_num, df_out_cat

        _
def fit_xgb_model (train, test, predictors, target, path, model_name, seed, monotonity):
    """
    This function fits a baseline xgboost algorithms with given parameters and returns a model object
    """

    x_train= train[predictors]
    x_test= test[predictors]
    y_train= train[target]
    y_test= test[target]

    params= {'booster': 'gbtree',
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
            'process_type': 'default',
            'eta': 0.4,
            'grow_policy': 'lossguide',
            'tree_method': 'hist',
            'max_depth': 6,
            'max_leaves': 0,
            'min_child_weight': 150,
            'max_delta_step': 0,
            'subsample': 0.8,
            'colsample_bytree': 0.8,
            'colsample_bylevel': 1,
            'colsample_bynode': 1,
            'gamma': 0,
            'lambda': 1,
            'alpha': 0,
            'scale_pos_weight': 1,
            'max_bin': 256,
            'num_parallel_tree': 1,
            'random_state': seed,
            'monotone_constraints': monotonity,
            'n_estimators': 400 
    }

    model = xgb.XGBClassifier((verbose = True,
                            **params))

    evaluation= [(x_train, y_train), (x_test, y_test)]

    model= model.fit(x_train, y_train, eval_set= evaluation,
                    early_stopping_rounds = 20
                    )

    pickle.dump(dump, open(path + "/{}.pkl".format(model_name), 'wb'))

    return model

def feature_impotance(model_file):

    """
    This function outputs feature importance of a given model from its binary file
    """

    score = model_file.get_booster().get_score(impotance_type = 'total_gain')
    df_score= pd.DataFrame(list(scores.items())).sort_values(by=1, ascending = False).reset_index(drop= True)
    df_score.columns = ['Feature', 'TotalGain']
    df_score["Gain"] = df_score['TotalGain']/df_score['TotalGain'].sum()

    return df_score 


def perf_model_files (df_test, df_train, path,  target, pkl_list):

    """
    This function calculates auc from various model files in pkl format and then returns the result
    """

    result = {}

    for file in pkl_list:

        if file[-3:] == 'pkl':
            a = {}

            iteration_count = file[-10:-4]

            storage_client = storage.Client()

            bucket = storage_client.bucket('bucket_location')

            blob_download = bucket.blob(path + "/{}".format(file))

            pickle_in = blob_download.download_as_string()
            model= pickle.loads(pickle_in)

            train_auc = roc_auc_curve(df_train[target], model.predict(xgb.DMatrix(df_train[model.feature_names])))
            test_auc = roc_auc_curve(df_test[target], model.predict(xgb.DMatrix(df_test[model.feature_names])))

            a["train_auc"] = train_auc
            a["test_auc"] = test_auc
            a["predictors_count"]= len(model.feature_names)

            result[iteration_count] = a

        else:
            continue

    return result


def bin_of_scores(df, score, bins):

    df["cut_base_{}".format(score)] = pd.qcut(df[score], q= bins, precision = 6)
    labels = [str[i] for i in range (1, df["cut_base_{}".format(score)].nunique() + 1, 1)]
    df["bins_{}".format(score)] = pd.qcut(df[score], bins, labels = labels)

    return df

def bad_rate_bins(df, score, target):

    return df.groupby(score)[target].mean().reset_index().rename(columns= {score:"ventile", target:"bad_rate"})

def bad_capture_rate(df, score, prediction, bins):

    df["cut_base"] = pd.qcut(df[prediction], q= bins, precision = 6)
    labels = [str[i] for i in range (1, df["cut_base_{}".format(score)].nunique() + 1, 1)]
    df["bins"] = pd.qcut(df[prediction], bins, labels = labels)

    results = df.groupby(["cut_base"]).agg({pred: ["count"], target: ["sum"]}).reset_index()
    results.columns= ["cut_base", 'base_total_count', 'base_bad_count']
    results["base_good_count"]= results["base_total_count"] - results["base_bad_count"] 

    results = results.sort_values(by= "cut_base", ascending = False).reset_index().drop('index', axis=1)

    results["bad_rate"] = results["base_bad_count"]/results["base_total_count"]
    bad_total = results["base_bad_count"].sum()
    results["cumulative_total"] = results["base_total_count"].cumsum()
    results["cumulative_bad"] = results["base_bad_count"].cumsum()
    results["cumulative_precision"] = results["cumulative_bad"]/results["cumulative_total"]
    results["bad_capture_rate_bin"] = results["base_bad_count"]/bad_total
    results["bad_capture_rate_cumulative_bin"] = results["cumulative_bad"]/bad_total
    results["precentile"] = results["base_total_count"].cumsum()/results["base_total_count"].sum()

    return results

def feature_red_result_analysis(path):
    """
    saving feature reduction result in a dataframe
    """
    feat_reduction_result = json.load(open(path + "/feature_reduction_result.json"))
    iter = []
    feature_count= []
    auc_train = []
    auc_test = []
    for i in feat_reduction_result.keys():
        iter.append(i)
        feature_count.append(feat_reduction_result[i]["predictor_count"])
        auc_train.append(feat_reduction_result[i]["auc_train"])
        auc_test.append(feat_reduction_result[i]["auc_test"])

    df = pd.DataFrame({"iteration": iter,
                       "features_count": feature_count,
                       "auc_train": auc_train,
                       "auc_test": auc_test})
    
    df = df.sort_values("auc_test", ascending= False)

    return df
