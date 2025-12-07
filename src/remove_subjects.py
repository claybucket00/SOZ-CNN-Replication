import pandas as pd

# subjects_to_remove = [
#     'ccepAgeUMCU47',
#     'ccepAgeUMCU48',
#     'ccepAgeUMCU49',
#     'ccepAgeUMCU51',
#     'ccepAgeUMCU52',
#     'ccepAgeUMCU53',
#     'ccepAgeUMCU55',
#     'ccepAgeUMCU57',
#     'ccepAgeUMCU58',
#     'ccepAgeUMCU59',
#     'ccepAgeUMCU60',
#     'ccepAgeUMCU61',
#     'ccepAgeUMCU63',
#     'ccepAgeUMCU65',
#     'ccepAgeUMCU69'
# ]

subjects_to_remove = [
    'ccepAgeUMCU46',
    'ccepAgeUMCU47'
]

reponse_df_filepath = '../data/response_df.csv'
response_df = pd.read_csv(reponse_df_filepath)

response_df = response_df[~response_df['subject'].isin(subjects_to_remove)]
response_df.to_csv(reponse_df_filepath)

print(response_df["subject"].unique())

