from flask import Flask, render_template, request
from .models import db, User, Tweet
from .twitter import add_user, add_tweets
import os
import numpy as np
from sklearn.linear_model import LogisticRegression
from dotenv import load_dotenv

load_dotenv()

import spacy
import en_core_web_sm
nlp_model = en_core_web_sm.load()
nlp_model.to_disk('my_nlp')


def create_app():
    #define database path
    # app_dir = os.path.dirname(os.path.abspath(__file__))
    # database = "sqlite:///{}".format(os.path.join(app_dir, "twitoff.sqlite3"))
    # print(database)
    nlp = spacy.load('my_nlp')

    #flask app instantiation
    app = Flask(__name__)
    #link app to database, squash warnings
    # app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI")
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
        User1 = request.form.get("User1")
        User2 = request.form.get("User2")
        p_text = request.form.get('Predict')
        response = None

        # print(User1, User2)

        # on post of name
        if User1:
            User1_name = add_user(User1)
            User2_name = add_user(User2)

            add_tweets(User1)
            add_tweets(User2)



            User1_tweets = User.query.filter_by(name=User1_name).first().tweets
            User2_tweets = User.query.filter_by(name=User2_name).first().tweets

            def vect_tweet(tweet_text):
                return nlp(tweet_text).vector

            User1_vects = np.array([vect_tweet(tweet.text) for tweet in User1_tweets])
            User2_vects = np.array([vect_tweet(tweet.text) for tweet in User2_tweets])

            vects = np.vstack([User1_vects, User2_vects])
            labels = np.concatenate([np.zeros(len(User1_tweets)),
                                     np.ones(len(User2_tweets))])
            p_text_vect = vect_tweet(p_text).reshape(1, -1)

            log_reg = LogisticRegression().fit(vects, labels)
            pred = int(log_reg.predict(p_text_vect))

            if pred == 0:
                response = "{} is likely to have tweeted '{}'.".format(User1, p_text)
            else:
                response = "{} is likely to have tweeted '{}'.".format(User2, p_text)

            # 'users' is referenced by html
        users = User.query.all()
        return render_template("home.html", users=users, response=response)
    return app

#############################################################################









