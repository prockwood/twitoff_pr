from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Creates a 'user' table, and a row on in Users Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # id as primary key
    name = db.Column(db.String(50), nullable=False) # user name
    last_tweet_id = (db.Integer)

    def __repr__(self):
        return "<User: {}>".format(self.name)

# Create a Tweet tab
class Tweet(db.Model):
    """Tweet text data - associated with Users Table"""
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Unicode(800))
    # text_vec = db.Column(db.PickleType, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(
        "user.id"), nullable=False)
    user = db.relationship('User', backref=db.backref('tweets', lazy=True))

    def __repr__(self):
        return "<Tweet: {}>".format(self.text)