'''
test app twitoff 
'''
from flask import Flask, render_template, request
from .models import DB, User, Tweet
from .twitter import add_or_update_user
from sklearn.datasets import load_iris, load_wine
from sklearn.linear_model import LogisticRegression
from .predict import predict_user


def create_app():
    ''' Initilaize App'''
    app = Flask(__name__)


    # DB config
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


    # Register our DB with the app
    DB.init_app(app)


    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)


    @app.route("/reset")
    def reset():
        # Drop all DB tables
        DB.drop_all()
        # Recreate all DB tables according to the
        # indicated schema in models.py
        DB.create_all()
        return render_template('base.html', title='Reset')


    # @app.route('/populate_mod1')
    # def populate_mod1():
    #     john = User(id=1, username="John")
    #     DB.session.add(john)
    #     julian = User(id=2, username='Julian')
    #     DB.session.add(julian)
    #     james = User(id=3, username="James")
    #     DB.session.add(james)
    #     jeff = User(id=4, username='Jeff')
    #     DB.session.add(jeff)
    #     jennifer = User(id=5, username="Jennifer")
    #     DB.session.add(john)
    #     jack = User(id=6, username='Jack')
    #     DB.session.add(jack)


    #     tweet1 = Tweet(id=1, text='''Just witnessed the most breathtaking sunset.
    #                                 Nature's beauty never fails to amaze me! 
    #                                 🌅 #sunsetlovers #naturephotography''', user=john)
    #     DB.session.add(tweet1)
    #     tweet2 = Tweet(id=2, text='''Excited to announce the launch of our new product!
    #                                 🎉 Get ready to experience innovation like never before.
    #                                 #productlaunch #innovation''', user=julian)
    #     DB.session.add(tweet2)
    #     tweet3 = Tweet(id=3, text='''Attended an inspiring conference today.
    #                                 So many great minds coming together to shape the future.
    #                                 #inspiration #conference''', user=james)
    #     DB.session.add(tweet3)
    #     tweet4 = Tweet(id=4, text='''Feeling grateful for the incredible support from our customers.
    #                                 You are the reason we strive for excellence every day.
    #                                 Thank you! 🙏 #gratitude #customersupport''', user=jeff)
    #     DB.session.add(tweet4)
    #     tweet5 = Tweet(id=5, text='''Just finished reading an incredible book that left me spellbound.
    #                                 Highly recommended!
    #                                 📚 #booklover #mustread''', user=jennifer)
    #     DB.session.add(tweet5)
    #     tweet6 = Tweet(id=6, text='''Had an amazing workout today, pushing my limits
    #                                 and feeling stronger than ever.
    #                                 💪 #fitnessmotivation #workout''', user=jack)
    #     DB.session.add(tweet6)


    #     DB.session.commit()

    #     return render_template('base.html', title='Populate DB Mod2')


    # @app.route('/populate_mod2')
    # def populate_mod2():
    #     add_or_update_user('calebhicks')
    #     add_or_update_user('elonmusk')
    #     add_or_update_user('rrherr')
    #     add_or_update_user('SteveMartinToGo')
    #     add_or_update_user('alyankovic')
    #     add_or_update_user('NASA')
    #     add_or_update_user('jkhowland')
    #     add_or_update_user('Austen')
    #     add_or_update_user('common_squirrel')
    #     add_or_update_user('KenJennings')
    #     add_or_update_user('ConanOBrien')
    #     add_or_update_user('big_ben_clock')
    #     add_or_update_user('IAM_SHAKESPEARE')

    #     return render_template('base.html', title='Populate DB Mod2')


    @app.route('/update')
    def update():
        # get list of usersnames of all users
        users = User.query.all()
        # usernames = []
        # for user in users:
        #     usernames.append(user.username)
        # ^^^ = [user.username for user in users]
        for username in [user.username for user in users]:
            add_or_update_user(username)

        return render_template('base.html', title='Updated')


    @app.route('/iris')
    def iris():    
        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(
            random_state=0
            , solver='lbfgs'
            , multi_class='multinomial'
            ).fit(X, y)

        return str(clf.predict(X[:2, :]))


    @app.route('/wine')
    def wine():    
        X, y = load_wine(return_X_y=True)
        clf = LogisticRegression(
            random_state=0
            , solver='lbfgs'
            , multi_class='multinomial'
            ).fit(X, y)

        return str(clf.predict(X[:-1, :]))


    @app.route('/user', methods=["POST"])
    @app.route('/user/<username>', methods=["GET"])
    def user(username=None, message=''):

        # we either take name that was passed in or we pull it
        # from our request.values which would be accessed through the
        # user submission
        username = username or request.values['user_name']
        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = "User {} Successfully added!".format(username)

            tweets = User.query.filter(User.username == username).one().tweets

        except Exception as E:
            message = "Error adding {}: {}".format(username, E)

            tweets = []

        return render_template("user.html", title=username, tweets=tweets, message=message)

    @app.route('/compare', methods=["POST"])
    def compare():
        user0, user1 = sorted(
            [request.values['user0'], request.values["user1"]])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            # prediction returns a 0 or 1
            prediction = predict_user(
                user0, user1, request.values["tweet_text"])
            message = "'{}' is more likely to be said by {} than {}!".format(
                request.values["tweet_text"]
                , user1 if prediction else user0
                , user0 if prediction else user1
            )

        return render_template('prediction.html', title="Prediction", message=message)

    return app
