import pandas as pd

ratingsdf = pd.read_csv("data/rating.csv", sep='|')
userdf = pd.read_csv("data/user.csv", sep='|')
venuedf = pd.read_csv("data/venue.csv", sep='|')

n_ratings = len(ratingsdf)
n_venues = len(ratingsdf['venueid'].unique())
n_users = len(ratingsdf['userid'].unique())

print(f"Number of ratings: {n_ratings}")
print(f"Number of unique venue's: {n_venues}")
print(f"Number of unique users: {n_users}")
print(f"Average ratings per user: {round(n_ratings/n_users, 2)}")
print(f"Average ratings per venue: {round(n_ratings/n_venues, 2)}")

# Find Lowest and Highest rated venue:
mean_rating = ratingsdf.groupby('venueid')[['score']].mean()
# Lowest rated venue
lowest_rated = mean_rating['score'].idxmin()
venuedf.loc[venuedf['venueid'] == lowest_rated]
# Highest rated venue
highest_rated = mean_rating['score'].idxmax()
venuedf.loc[venuedf['venueid'] == highest_rated]
# show number of people who rated venue rated venue highest
ratingsdf[ratingsdf['venueid']==highest_rated]
# show number of people who rated venue rated venue lowest
ratingsdf[ratingsdf['venueid']==lowest_rated]

## the above venue has very low dataset. We will use bayesian average
venue_stats = ratingsdf.groupby('venueid')[['score']].agg(['count', 'mean'])
venue_stats.columns = venue_stats.columns.droplevel()
venue_stats = venue_stats.sort_values(by = 'count')
print(venue_stats)

user_stats = ratingsdf.groupby('userid')[['score']].agg(['count','mean'])
user_stats.columns = user_stats.columns.droplevel()
user_stats = user_stats.sort_values(by = 'count')
print(user_stats)