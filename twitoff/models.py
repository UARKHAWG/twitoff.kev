'''
SQLAlchemy User and Tweet models for out database
'''
from flask_sqlalchemy import SQLAlchemy

# creates a DB Object from SQLAlchemy class
DB = SQLAlchemy()


# Making a User table using SQLAlchemy
class User(DB.Model):
    '''Creates a User Table with SQlAlchemy'''
    # id column
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    # name column
    username = DB.Column(DB.String, nullable=False)
    # most recent tweet id
    newest_tweet_id = DB.Column(DB.BigInteger)
    # backref is as-if we had added a tweets list to the user class
    # tweets = []



    def __repr__(self):
        return f"User: {self.username}"


class Tweet(DB.Model):
    '''Keeps track of Tweets for each user'''
    # id col
    id = DB.Column(DB.BigInteger, primary_key=True, nullable=False)
    # text col
    text = DB.Column(DB.Unicode(300))
    # store word embeddings 'vectorization' - representing words with numbers
    vect = DB.Column(DB.PickleType, nullable=False)
    # user_id col (foreign / secondary key)
    user_id = DB.Column(DB.BigInteger, DB.ForeignKey('user.id'), nullable=False)
    # user col creates 2way link between a user object and a tweet object
    user = DB.relationship('User', backref=DB.backref('tweets', lazy=True))

    def __repr__(self):
        return f"Tweet: {self.text}"
