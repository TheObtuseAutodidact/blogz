from flask import Flask, request, render_template, redirect, flash, session, url_for
from sqlalchemy import desc
from helpers import validate
from hashutils import check_pw_hash
from models import User, Blog, db
from app import app


@app.before_request
def require_login():
    allowed_routes = ["login", "signup", "index", "blog"]
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect("/login")


@app.route("/")
def index():
    bloggers = User.query.all()
    return render_template("index.html", bloggers=bloggers)


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
        if user and not check_pw_hash(password, user.pw_hash):
            errors['password'] = "Password incorrect"
        # if user and user.password == password:
        if user and check_pw_hash(password, user.pw_hash):
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
        user = User.query.filter_by(username=username).first()
        session['username'] = user.username
        return redirect("/newpost")
    return render_template("signup.html", errors=errors)


@app.route("/logout")
def logout():
    print(session)
    del session['username']
    print(session)
    
    return redirect("/blog")


@app.route("/blog")
def blog():
    page=1
    posts = []
    if request.args:
        if "id" in request.args:
            blog_id = int(request.args.get('id'))
            post = Blog.query.filter_by(id=blog_id).first()
            return render_template("show.html", post=post)
        if "user" in request.args:
            user_id = int(request.args.get('user'))
            posts = Blog.query.filter_by(owner_id=user_id).paginate(page, 5, False)
        if "page" in request.args:
            page = int(request.args.get("page"))
    posts = posts or Blog.query.order_by(desc(Blog.id)).paginate(page, 5, False)
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

        owner = User.query.filter_by(username=session['username']).first()

        new_post = Blog(title, body, owner)
        db.session.add(new_post)
        db.session.commit()

        newest_post = Blog.query.order_by(desc(Blog.id)).first()
        return redirect("/blog?id={}".format(newest_post.id))
    return render_template("newpost.html")

if __name__ == '__main__':
    app.run()
