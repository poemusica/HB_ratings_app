from flask import Flask, render_template, redirect, request, session, flash
import model

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'

@app.before_request
def setup_session():
    session['user'] = session.get('user', None)
    session['email'] = session.get('email', None)

@app.route('/')
def index():
    user_list = model.session.query(model.User).limit(20).all()
    # print user_list
    return render_template("user_list.html", users=user_list)

@app.route("/signup", methods=["GET"])
def show_signup():
    return render_template("signup.html")

@app.route("/signup", methods=["POST"])
def process_signup():
    """Receive the user's signup info located in the 'request.form'
    dictionary, look up the user, and store them in the session."""
    age = request.form["age"]
    gender = request.form["sex"]
    zipcode = request.form["zipcode"]
    email = request.form["email"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    print age, gender, zipcode, email, password1, password2
    
    user = model.session.query(model.User).filter_by(email=email).first()

    messages = ""
    
    if user:
        messages = messages + "User already exists. "
    if password1 != password2:
        messages = messages + "Passwords do not match."
    if messages:
        flash(messages)
        return redirect('/signup')
    else:
        u = model.User(age=age, gender=gender, zipcode=zipcode, email=email, password=password1)
        model.session.add(u)
        model.session.commit()

        user = model.session.query(model.User).filter_by(email=email).first()

        messages = "You are logged in as %s" % user.email
        session['user'] = user.id
        session['email'] = user.email
        flash(messages)
    return redirect("/")


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
    session['email'] = user.email
    flash("You are logged in as %s" % user.email)
    return redirect("/")

@app.route("/logout")
def logout(): 
    session.clear()

    flash("User has logged out.")
    return redirect("/login")  

@app.route("/user/<id>")
def show_user(id):
    """This page shows the details of a given user and their ratings."""
    user = model.session.query(model.User).filter_by(id=id).first()
    return render_template("user_details.html",
                  display_user = user)






if __name__ == "__main__":
    app.run(debug=True)