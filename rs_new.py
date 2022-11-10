import pandas as pd

rating = pd.read_csv('data/_rating2.csv', sep='|')
df = rating[['venueid', 'userid', 'score', 'time']]
df.to_csv('data/_rating.csv', sep='|', encoding='utf-8', index=True)
