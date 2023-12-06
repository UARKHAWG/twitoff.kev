'''
connection to twitter api
'''

from os import getenv
import not_tweepy as tweepy
import spacy
from .models import DB, Tweet, User


# get API Key from environment vars
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')


# Connect to the Twitter API
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):
    '''Takes username and pulls user from Twitter API'''
    try:
        twitter_user = TWITTER.get_user(screen_name=username)
        # is there a user in the db that already has this id?
        # if not, then create a User in the db with this id
        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)

        # add the user to the database
        DB.session.add(db_user)


        # get the user's tweets
        tweets = twitter_user.timeline(count=200
                                    , exclude_replies=True
                                    , include_rts=False
                                    , tweet_mode='extended'
                                    , since_id=db_user.newest_tweet_id)
        # update the newest_tweet_id if there have been new tweets
        # since the last time the user tweeted
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # check for duplicate tweets


        # add each tweet to the database
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id
                            , text=tweet.full_text[:300]
                            , vect = tweet_vector
                            , user_id=db_user.id
                            )

            db_user.tweets.append(db_tweet)

            DB.session.add(db_tweet)

    except Exception as e:
        print(f'Error processing {username}: {e}')
        raise e
    
    else:
        # save changes
        DB.session.commit()


nlp = spacy.load('my_model/')

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
