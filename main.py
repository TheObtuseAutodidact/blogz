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

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    # owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        # self.owner = owner


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
            
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()

        newest_post = Blog.query.order_by(desc(Blog.id)).first()
        return redirect("/blog?id={}".format(newest_post.id))
    return render_template("newpost.html")


# @app.route("/", methods=["POST", "GET"])
# def blog_post():
#     if request.method == "POST":
#         title = request.form['blog_title']
#         body = request.form['blog_post']

#         new_post = Blog(title, body)
#         db.session.add(new_post)
#         db.session.commit()

#         return redirect("/")
    # posts = Blog.query.order_by(desc(Blog.id))
    # return render_template("index.html", posts=posts)

if __name__ == '__main__':
    app.run()
