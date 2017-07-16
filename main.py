from flask import Flask, request, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import os

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:{}@localhost:8889/blogz'.format(os.environ['RDS_PASSWORD2']) #user:password
app.config['SQLALCHEMY_ECHO'] = True # show sql generated by sqlalchemy
app.secret_key = "development"
db = SQLAlchemy(app)


def is_valid(field):
    if len(field) < 3 or len(field) > 21 or not field:
        return False
    if " " in field:
        return False
    return True

def validate(inputs, errors):
    if not is_valid(inputs['username']):
            errors['username']="That's not a valid username"
    if not is_valid(inputs['password']):
        errors["password"] = "That's not a valid password"
    if inputs['password'] != inputs['verify_pass'] or not inputs['verify_pass']:
        errors["match_password"] = "Passwords don't match"
    existing_user = User.query.filter_by(username=inputs['username']).first()
    if existing_user:
        errors["existing_user"] = "Sorry, that username is taken"
    

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password = db.Column(db.String(64))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/login", methods=["GET", "POST"])
def login():
    errors = {}
    return_name = {}
    if request.method == "POST":
        username = request.form['username']
        return_name['username'] = username # to repopulate login form incase of errors
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            errors['user'] = "User does not exist"
        if user and (not password or user.password != password):
            errors['password'] = "Password incorrect"
        if user and user.password == password:
            session['username'] = user.username
            flash("Logged in")
            return redirect("/newpost")
    return render_template("login.html", errors=errors, username=return_name)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    errors = {}
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        verify_pass = request.form['verify']
        field_inputs = {'username':username, 'password':password, 'verify_pass':verify_pass}
        validate(field_inputs, errors)
        if errors:
            return render_template("signup.html", errors=errors, field_inputs=field_inputs)

        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/newpost")
    return render_template("signup.html", errors=errors)



@app.route("/blog")
def blog():
    if request.args:
        blog_id = int(request.args.get('id'))
        post = Blog.query.filter_by(id=blog_id).first()
        print(post)
        return render_template("show.html", post=post)
    posts = Blog.query.order_by(desc(Blog.id))
    return render_template("blog.html", posts=posts)

@app.route("/newpost", methods=["POST", "GET"])
def newpost():
    if request.method == "POST":
        title = request.form['blog_title']
        body = request.form['blog_post']

        if not title or not body:
            if not title:
                flash("Title cannot be empty", category="title")

            if not body:
                flash("Body cannot be empty", category="body")
            return render_template("newpost.html")
        
        # stand in User/owner until we build the sign in
        owner = User.query.first()

        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()

        newest_post = Blog.query.order_by(desc(Blog.id)).first()
        return redirect("/blog?id={}".format(newest_post.id))
    return render_template("newpost.html")

if __name__ == '__main__':
    app.run()
