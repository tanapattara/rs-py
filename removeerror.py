import pandas as pd

userdf = pd.read_csv("data/emptyuser.csv", sep='|', encoding='utf-8')
userdf = userdf.drop(userdf[userdf.msg == 'error'].index)

userdf.to_csv("data/emptyuser.csv", index=False, encoding='utf-8', sep='|')