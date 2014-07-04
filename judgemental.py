from flask import Flask, session, request, render_template, flash, redirect, url_for, g
from model import session as db_session, User, Rating, Movie
import model
from flask_heroku import Heroku
import os

app = Flask(__name__)
heroku = Heroku(app)
SECRET_KEY = "fish"
app.config.from_object(__name__)

@app.teardown_request
def shutdown_session(exception = None):
    db_session.remove()

@app.before_request
def load_user_id():
    g.user_id = session.get('user_id')

@app.route("/")
def index():
    if g.user_id:
        return redirect(url_for("display_search"))
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    email = request.form['email']
    password = request.form['password']

    try:
        user = db_session.query(User).filter_by(email=email, password=password).one()
    except:
        flash("Invalid username or password", "error")
        return redirect(url_for("index"))

    session['user_id'] = user.id
    return redirect(url_for("display_search"))

@app.route("/register", methods=["POST"])
def register():
    email = request.form['email']
    password = request.form['password']
    existing = db_session.query(User).filter_by(email=email).first()
    if existing:
        flash("Email already in use", "error")
        return redirect(url_for("index"))

    u = User(email=email, password=password)
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    session['user_id'] = u.id 
    return redirect(url_for("display_search"))

@app.route("/search", methods=["GET"])
def display_search():
    return render_template("search.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.form['query']
    movies = db_session.query(Movie).\
            filter(Movie.title.ilike("%" + query + "%")).\
            limit(20).all()

    return render_template("results.html", movies=movies)

@app.route("/movie/<int:id>", methods=["GET"])
def view_movie(id):
    movie = db_session.query(Movie).get(id)
    ratings = movie.ratings
    rating_nums = []
    user_rating = None
    for r in ratings:
        if r.user_id == session['user_id']:
            user_rating = r
        rating_nums.append(r.rating)
    avg_rating = float(sum(rating_nums))/len(rating_nums)

    user = db_session.query(User).get(session['user_id'])
    prediction = None
    if not user_rating:
        # user = db_session.query(User).get(g.user_id) 
        prediction = user.predict_rating(movie)
        effective_rating = prediction
    else:
        effective_rating = user_rating.rating

    the_eye = db_session.query(User).filter_by(email="theeye@ofjudgment.com").one()
    eye_rating = db_session.query(Rating).filter_by(user_id=the_eye.id, movie_id=movie.id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(movie)
    else:
        eye_rating = eye_rating.rating

    if effective_rating:
        print effective_rating, eye_rating
        difference = abs(eye_rating - effective_rating)
        messages = ["I suppose you don't have such bad taste after all.",
                "And I was just starting to like you.",
                "I regret every decision I've ever made that has brought me to listen to your opinion.",
                "Words fail me, as your taste in movies has clearly failed you.",
                "That movie is great. For a clown to watch. Idiot."]
        beratement = messages[int(difference)]
    else: beratement = None
    
    return render_template("movie.html", movie=movie, 
            average=avg_rating, user_rating=user_rating,
            prediction = prediction, beratement=beratement)

@app.route("/rate/<int:id>", methods=["POST"])
def rate_movie(id):
    rating_number = int(request.form['rating'])
    user_id = session['user_id']
    rating = db_session.query(Rating).filter_by(user_id=user_id, movie_id=id).first()

    if not rating:
        flash("Rating added", "success")
        rating = Rating(user_id=user_id, movie_id=id)
        db_session.add(rating)
    else:
        flash("Rating updated", "success")

    rating.rating = rating_number
    db_session.commit()

    return redirect(url_for("view_movie", id=id))

@app.route("/my_ratings")
def my_ratings():
    if not g.user_id:
        flash("Please log in", "warning")
        return redirect(url_for("index"))

    ratings = db_session.query(Rating).filter_by(user_id=g.user_id).all()
    return render_template("my_ratings.html", ratings=ratings)

@app.route("/logout")
def logout():
    del session['user_id']
    return redirect(url_for("index"))

if __name__ == "__main__":
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not db_uri:
        db_uri = "sqlite:///ratings.db"
    model.connect(db_uri)
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)), host="0.0.0.0")
