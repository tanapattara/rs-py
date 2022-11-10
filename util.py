import pandas as pd
import os


def getfile(filepath, isLoad=True):
    df = pd.DataFrame()
    if not isLoad:
        return df
    try:
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, sep='|')
    except:
        return df
    return df
