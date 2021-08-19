from .models import db, User, Tweet
import tweepy
import os


#twitter authentication
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_API_KEY_SECRET = os.getenv("TWITTER_API_KEY_SECRET")

auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_KEY_SECRET)
api = tweepy.API(auth)

def add_user(username):
    twit_user = api.get_user(username)
    user = User(name=twit_user.name)
    db.session.add(user)
    db.session.commit()
    return twit_user.name

def add_tweets(username):
    twit_user = api.get_user(username)
    db_id = User.query.filter_by(name=twit_user.name).first().id
    tweets = api.user_timeline(screen_name=twit_user.screen_name,
                    count=200,
                    exclude_replies=True,
                    include_rts=False,
                    tweet_mode="extended")

    for tweet in tweets:
        db_tweet = Tweet(text=tweet.full_text, user_id=db_id)
        db.session.add(db_tweet)

    db.session.commit()




