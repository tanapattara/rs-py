import pandas as pd

from util import Util



# ratingdf -> venueid|userid|score|time|comment
ratingsdf = pd.read_csv("data/rs_rating.csv", sep='|')
# venuedf -> venueid|name|location|vote_count|vote_average|score
venuedf = pd.read_csv("data/venue_metadata.csv", sep='|')
# gcategorydf -> venueid|name|gcategory
gcategorydf = pd.read_csv("data/gcategorydf.csv", sep='|')
# mcategorydf -> id|name
mcategorydf = pd.read_csv("data/mcategory.csv", sep='|')

# venuecatedf -> venueid|name|mcategory|gcategory
venuecatedf = Util.getfile("data/venue_with_category.csv")
# g2m -> gcate|mcate
g2m_category = Util.getfile("data/g2m_category.csv")

def isExist(catetxt, columntxt, df):
    if len(df) == 0:
        return False

    if catetxt in df[columntxt].values:
        return True

def getMcate(catetxt):
    data = g2m_category.loc[g2m_category.gcate == catetxt]
    return data.mcate.values.item()

# loop all venue.csv
for i, row in venuedf.iterrows():
    vid = row.venueid
    vname = row['name']

    # check if exist -> continue to new venue
    if isExist(vid, 'venueid',venuecatedf):
        continue

    # find current vid in gcate
    if vid in gcategorydf['venueid'].values:
        #get gcat
        existdata = gcategorydf.loc[(gcategorydf.venueid == vid)]
        gcat = existdata.gcategory.values.item()
        # check in exist g2m data
        if isExist(gcat, 'gcate', g2m_category):
            #get m cate from g2m
            mcat = getMcate(gcat)
            # add to new venue
            if len(venuecatedf) > 0:
                venuecatedf.loc[len(venuecatedf.index)] = [vid, vname, gcat, mcat]
            else:
                venuecatedf = pd.DataFrame([[vid, vname, gcat, mcat]], columns=['venueid', 'name', 'gcate', 'mcate'])
        else:
            # undefind link category
            while True:
                print("Undefind Category from google : " + gcat)
                print("Add gCategory to MainCategory")
                print("1|สถานที่เกี่ยวกับศาสนา\n2|แลนด์มาร์กและอนุสรณ์สถาน\n3|ศิลปะวัฒนธรรมชุมชน\n4|ตลาดแหล่งชุมชน\n5|พิพิธภัณฑ์\n6|ธรรมชาติและสถานที่สวยงาม\n7|other\n")
                value = input("Please enter a number:")
                value = int(value)

                if value > 0 and value < 8:
                    mcat = "other"
                    if value == 1:
                        mcat = "สถานที่เกี่ยวกับศาสนา"
                    elif value == 2:
                        mcat = "แลนด์มาร์กและอนุสรณ์สถาน"
                    elif value == 3:
                        mcat = "ศิลปะวัฒนธรรมชุมชน"
                    elif value == 4:
                        mcat = "ตลาดแหล่งชุมชน"
                    elif value == 5:
                        mcat = "พิพิธภัณฑ์"
                    elif value == 6:
                        mcat = "ธรรมชาติและสถานที่สวยงาม"

                    #add to g2m
                    if len(g2m_category) > 0:
                        g2m_category.loc[len(g2m_category.index)] = [gcat, mcat]
                    else:
                        g2m_category = pd.DataFrame([[gcat, mcat]], columns=['gcate','mcate'])

                    if len(venuecatedf) > 0:
                        venuecatedf.loc[len(venuecatedf.index)] = [vid, vname, gcat, mcat]
                    else:
                        venuecatedf = pd.DataFrame([[vid, vname, gcat, mcat]], columns=['venueid', 'name', 'gcate', 'mcate'])

                    
                    # Stop loop
                    break
    else:
        # undefind category from google
        while True:
                print("Undefind Category from google : " + vname)
                print("Add gCategory to MainCategory")
                print("1|สถานที่เกี่ยวกับศาสนา\n2|แลนด์มาร์กและอนุสรณ์สถาน\n3|ศิลปะวัฒนธรรมชุมชน\n4|ตลาดแหล่งชุมชน\n5|พิพิธภัณฑ์\n6|ธรรมชาติและสถานที่สวยงาม\n7|other\n")
                value = input("Please enter a number:")
                value = int(value)

                if value > 0 and value < 8:
                    mcat = "other"
                    if value == 1:
                        mcat = "สถานที่เกี่ยวกับศาสนา"
                    elif value == 2:
                        mcat = "แลนด์มาร์กและอนุสรณ์สถาน"
                    elif value == 3:
                        mcat = "ศิลปะวัฒนธรรมชุมชน"
                    elif value == 4:
                        mcat = "ตลาดแหล่งชุมชน"
                    elif value == 5:
                        mcat = "พิพิธภัณฑ์"
                    elif value == 6:
                        mcat = "ธรรมชาติและสถานที่สวยงาม"

                    gcat = "other"

                    if len(venuecatedf) > 0:
                        venuecatedf.loc[len(venuecatedf.index)] = [vid, vname, gcat, mcat]
                    else:
                        venuecatedf = pd.DataFrame([[vid, vname, gcat, mcat]], columns=['venueid', 'name', 'gcate', 'mcate'])
                    
                    # Stop loop
                    break
    
    venuecatedf.to_csv('data/venue_with_category.csv', sep='|', encoding='utf-8', index=False)
    g2m_category.to_csv('data/g2m_category.csv', sep='|', encoding='utf-8', index=False)
