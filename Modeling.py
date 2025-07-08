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