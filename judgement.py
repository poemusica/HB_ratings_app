from flask import Flask, render_template, redirect, request, session, flash
import model

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'

@app.route('/')
def index():
    user_list = model.session.query(model.User).limit(5).all()
    print user_list
    return render_template("user_list.html", users=user_list)


@app.route("/login", methods=["GET"])
def show_login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def process_login():
    """Receive the user's login credentials located in the 'request.form'
    dictionary, look up the user, and store them in the session."""
    email = request.form["email"]
    password = request.form["password"]
    user = model.session.query(model.User).filter_by(email=email).first()

    if not user:
        flash("Sorry! Login Error.")
        return redirect("/login")
    elif (user.password != password):
        flash("Sorry! Login Error.")
        return redirect("/login")

    session['user'] = user.id
    flash("You are logged in as %s" % user.email)
    return redirect("/")












if __name__ == "__main__":
    app.run(debug=True)