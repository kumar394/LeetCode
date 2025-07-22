# This will will have feture reduction code and how to run it
import xgboost as xgb
from xgboost import XGBClassifier
import numpy as np
import pandas as 
import sys


def xgb_initial (df, predictors, target, path, prefix, params, num_boost, nfold, early_stopping, nthreads,metrics
                 method=1, rp= 0.1, auc_th= None, auc_pcnt= 0.05, test_df= None, weights= None,
                 start_count= 1, verbose_eval= 20, seed= 42, mono= None, verbose= True)

    def get_feature_map(df, model, feature_file, file_save_path)
        df_dtypes = pd.DataFrame(df.dtypes)
        df_dtypes.reset_index(inplace= True)
        df_dtypes = df_dtypes.replace({"float64":"q", "int64": "i", "int32":"i"})
        files = os.path.join(file_save_path, feature_file)
        df_dtypes.to_csv(files, heador = None, index= True, sep= " ", mode= "a")
        return df_dtypes


    def get_feature_imp(xgb_model,df, model, target, var_imp_file_name, file_save_path)

        scores = xgb_model.get_score(importance_type = "total_gain")
        scores_df= pd.DataFrame(list(scores.items()).sort_values(by=1, ascending= False)).reset_index(drop= True)
        scores_df.columns= ["Feature", "Total_gain"]
        scores_df["Gain"] = scores_df["Total_gain"]/ scores_df["Total_gain"].sum()

        corr_list = []
        for var in scores_df["Feature"]:
            df_new= pd.concat([df[var], target], axis=1)
            corr = df_new.corr().iloc[0, 1]
            corr_list.append(corr)

        scores_df["corr_w_target"] = corr_list

        files = os.path.join(file_save_path, var_imp_file_name)

        scores_df.to_csv(files, index_label= "Rank", sep= ",", encoding= "utf-8")

        return scores_df


    if path == "":
        return "please provide path to save files"

    if prefix == "":
        return "please provide iteration naming structure"


    current_eligible = predictors

    cont = True
    i= start_count - 1

    if seed is not None:
        np.random.seed(seed)

    while cont == True:
        i += 1

        print("**** BEGIN ROUND '+(str(i))+' ****", file= sys.stdout)

        iter_num = "{0:0=2d}".format(i)
        file_names = {"pickled_model":prefix+ "_model" + "_iter" + iter_num+ ".pkl",
                      "var_imp": :prefix+ "_var_imp" + "_iter" + iter_num+ ".csv",
                      "xgb_eval_history":prefix+ "_xgb_eval_history" + "_iter" + iter_num+ ".csv"}


        if mono is not None:
            new_mono = mono[mono["Variable"].isin(current_eligible)]
            cat_order = CategoricalDtype(current_eligible, ordered= True)
            new_mono["Variable"]= new_mono["Variable"].astype(cat_order)
            new_mono.sort_values("Variable", inplace= True)
            feature_monotones = new_mono["mono"].tolist()
            tree_params["monotone_constraints"] = "(" + ",".join([str(m) for m in feature_monotones])

        else:
            tree_params = tree_params

        train_data = df[current_eligible]
        train_data_target = df[target]
        test_data = test_df[current_eligible]
        test_data_target= test_df[target]

        if weights is None:
            train_data_weight = None
            test_data_weight= None
        else:
            train_data_weight = list(df[weights])
            test_data_weight = list(test_data[weights])

        train_dmatrix= xgb.DMatrix(data= train_data, 
                                   label= list(train_data_target),
                                   weight= train_data_weight)
        

        test_dmatrix= xgb.DMatrix(data= test_data, 
                                   label= list(test_data_target),
                                   weight= test_data_weight)
        
        cv_results= xgb.cv(dtrain= train_dmatrix, 
                           params= tree_params,
                           nfold= nfold,
                           early_stopping_rounds= early_stopping,
                           num_boost_round= num_boost_round,
                           as_pandas = True,
                           verbose_eval= verbose_eval,
                           seed= seed)
        
        print("Fitting final model....", file= sys.stdout)
        best_iter= cv_results.shape[0]

        watchlist_final= [(train_dmatrix, "train"), (test_dmatrix, "validation")]
        xgb_progress= {}
        xgb_results= xgb.train(dtrain= train_dmatrix,
                               params= tree_params,
                               num_boost_round= best_iter,
                               evals= watchlist_final,
                               verbose_eval= verbose_eval,
                               evals_results= xgb_progress)
        
        xgb_train_auc= pd.DataFrame(xgb_progress["train"])
        xgb_train_auc.columns= ["train_auc"]
        xgb_val_auc= pd.DataFrame(xgb_progress["validation"])
        xgb_val_auc.columns= ["val_auc"]
        xgb_eval_hist= pd.concat([xgb_train_auc, xgb_val_auc], axis=1)

        file = os.path.join(path, file_names["xgb_eval_history"])
        xgb_eval_hist.to_csv(file)


        # store all the data
        storage_client = storage.Client()

        ## set up the bucket
        bucket = storage_client.bucket('prosper_group_risk')
        blob_path = save_path[len("gs://prosper_group_risk/"):]
        blob_upload = bucket.blob(blob_path + '/{}'.format(file_names['pickled_model']))

        ## this is for uploading/saving the file
        pickle_out = pickle.dumps(xgb_results)  ## change model1 to whatever object you're saving
        blob_upload.upload_from_string(pickle_out)

        # file_to_save = os.path.join(save_path, file_names['pickled_model'])
        # pickle.dump(xgb_results, open(file_to_save, 'wb'))

        # use save_model() to save the xgboost internal binary format
        # file_to_save = os.path.join(save_path, file_names['binary_model'])

        # xgb_results.save_model(file_to_save)
        #     get feature map
        #     get_feature_map(dataframe[current_eligible], save_prefix, file_names['feature_map'], file_save_path=save_path)  # use get_feature_map
        #     get feature importance table by Gain share and save to top features ranking
        #     get_feature_importance(xgb_results, dataframe, save_prefix, train_data_target, file_names['var_imp_map'], file_save_path=save_path)

        # upload all files
        print("Start uploading the final model results...", file=sys.stdout)

        # important_vars = list(xgb_results.get_fscore().keys())  # convert key to a list: but the order is different from R
        scores = xgb_results.get_score(importance_type='total_gain')
        scores_df = pd.DataFrame(list(scores.items())).sort_values(by=1, ascending=False).reset_index(drop=True)
        scores_df.columns = ['Feature', 'Total_gain']  # set column names
        scores_df['Gain'] = scores_df['Total_gain'] / scores_df['Total_gain'].sum()
        important_vars = scores_df['Feature'].tolist()
        n_var = len(important_vars)

        if (method == 1) | (method == 3):
            if n_var == len(current_eligible):
                if method == 1:
                    cont = False
                else:
                    if verbose:
                        print('***** Switching method from 1 to 2 *****', file=sys.stdout)
                    method = 2
                    print('now it is {para1}'.format(para1=method))
                current_auc = cv_results['train-auc-mean'].max()
                auc_thresh = current_auc * (1 - auc_pcnt)
                print('now it is {para1}'.format(para1=auc_thresh))
                n_to_rmv = math.ceil(n_varrked_pcnt)
                current_eligible = important_vars[:(n_var - n_to_rmv)]
            else:
                current_eligible = important_vars

            if verbose:
                print('Next Iteration Length of feature vector: {len_feature}'.format(len_feature=len(current_eligible)), file=sys.stdout)

        elif method == 2:
            current_auc = cv_results['train-auc-mean'].max()
            n_to_rmv = math.ceil(n_varrked_pcnt)
            current_eligible = important_vars[:(n_var - n_to_rmv)]
            if auc_thresh is None:
                auc_thresh = current_auc * (1 - auc_pcnt)
            if verbose:
                print('auc_thresh is set to {para1}: {para2} less than max of first model train AUC'.format(para1=auc_thresh, para2=auc_pcnt), file=sys.stdout)

            if current_auc < auc_thresh:
                cont = False
            else:
                if verbose:
                    print('Next Iteration Length of feature vector: {para1}'.format(para1=n_var - n_to_rmv), file=sys.stdout)
