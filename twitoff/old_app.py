from flask import Flask, render_template, request
from .models import db, User, Tweet
import os
import tweepy

import spacy
import en_core_web_sm
nlp_model = en_core_web_sm.load()



def create_app():
    #define database path
    app_dir = os.path.dirname(os.path.abspath(__file__))
    database = "sqlite:///{}".format(os.path.join(app_dir, "twitoff.sqlite3"))
    #twitter authentication, tweepy api intitialization
    auth = tweepy.OAuthHandler('Tci8SikOMwWFPlnQOp3Zwb05E', '03hxbDzZJdN8j24drgA5NTjysxuBXcy4ljNsUgMWrYNNuMzfRo')
    api = tweepy.API(auth)
    #spacy model serialized then loaded
    nlp_model.to_disk('my_nlp')
    my_nlp = spacy.load('my_nlp')

    #flask app instantiation
    app = Flask(__name__)
    #link app to database, squash warnings
    app.config["SQLALCHEMY_DATABASE_URI"] = database
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    #database linking
    db.init_app(app)

    # Create tables
    with app.app_context():
        db.drop_all()
        db.create_all()

    #decorator listens for home dir, and GET/POST requests
    @app.route("/", methods=["GET", "POST"])
    def home():
        #get user input, "name"/"recency" defined in html
        name = request.form.get("name")
        recency = request.form.get("recency")
        #convert to int on post
        if recency:
            recency = int(recency)
        # on post of name
        if name:
            # create a tweepy User object
            twit_user = api.get_user(name)
            # if user not in database add to User table
            if not User.query.filter_by(name=twit_user.name).first():
                # make a User object populate User table in database
                user = User(name=twit_user.name)
                db.session.add(user)
                db.session.commit()
            #save the user id
            nu_id = User.query.filter_by(name=twit_user.name).first().id

            # make a Tweet object populate Tweet table in database
            twit_tweet = api.user_timeline(screen_name=twit_user.screen_name,
                            count=200,
                            exclude_replies=True,
                            include_rts=False,
                            tweet_mode="extended")[recency].full_text
            # make a nlp model vector from tweet text
            text_vec = my_nlp(twit_tweet).vector
            nu_tweet = Tweet(text=twit_tweet, text_vec=text_vec, user_id=nu_id)
            db.session.add(nu_tweet)
            db.session.commit()
        # 'users' is referenced by html
        users = User.query.all()
        return render_template("home.html", users=users)
    return app










