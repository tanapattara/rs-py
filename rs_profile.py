import pandas as pd

ratingsdf = pd.read_csv("data/rating_pop.csv", sep='|')
venuedf = pd.read_csv("data/venue_metadata.csv", sep='|')
categorydf = pd.read_csv("data/categorydf.csv", sep='|')


def getfile(filepath):
    df = pd.DataFrame()
    try:
        if os.path.exists(filepath):
            df = pd.read_csv(filepath, sep='|')
    except:
        return df
    return df


maincategory = getfile('data/main.categpry.csv')

for row in categorydf.iterrows:
    print(row.category)
    x = input()
