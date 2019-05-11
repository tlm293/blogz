from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEGUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://blogz:blogz@localhost:8889/blogz"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)
app.secret_key = "y33kGcyss&zP38"

#build a class 
class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id =db.Column(db.Integer, db.ForeignKey("user.id"))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship("Blog", backref="owner")

    def __init__(self, username, password):
        self.username = username
        self.password = password
    
@app.before_request
def require_login():
    allowed_routes = ["login", "signup"]
    if request.endpoint not in allowed_routes and "username" not in session:
        return redirect("/login") 

@app.route("/login", methods=["POST", "GET"])
def login():
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["username"] = username
            flash("Logged in")
            return redirect("/")
        else:
            flash("User password incorrect or user does not exist", "error")
    return render_template("login.html")
    

@app.route("/signup", methods=["POST", "GET"])
def signup():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify_password = request.form["verify_password"]

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/")
        else:
            return "<h1>Duplicate user</h1>"

    return render_template("signup.html")

    # title="Validation"
    # title2="Welcome"

    # username=""
    # password=""
    # verify_password=""
    # username_error=""
    # verify_password_error = ""

    # if request.method == "POST":
    #     username = request.form["username"]
    #     password = request.form["password"]
    #     verify_password = request.form["verify_password"]

    # if not username:
    #     username_error = "Please enter a username."
    #     username=""
    # else:
    #     for char in username:
    #         if char.isspace():
    #             username_error = "Username cannot contain a space."
    #             username = ""
    #         else:
    #             if (len(username)<3) or (len(username)>20):
    #                 username_error = "Username needs to be at least 3 characters but less than 20 characters."
    #                 username = ""

    # if not password:
    #     password_error = "Please enter a password."
    #     password = ""
    # else:
    #     for char in password:
    #         if char.isspace():
    #             password_error = "Password cannot contain a space."
    #             password = ""
    #         else:
    #             if (len(password) < 3) or (len(password) > 20):
    #                 password_error = "Password needs to be at least 3 characters but less than 20 characters."
    #                 password = ""

    # if not verify_password:
    #     verify_password_error = "Please re-enter password."
    #     verify_password = ""
    # else:
    #     if password != verify_password:
    #         verify_password_error = "Passwords do not match."
    #         verify_password = ""

    # if not username_error and not password_error and not verify_password_error:
    #     return render_template("welcome.html", title=title2, username=username)

    # else:
    #     return render_template("setup.html", title = title, 
    #         username=username, 
    #         password=password, 
    #         verify_password=verify_password, 
    #         username_error=username_error,
    #         password_error=password_error,
    #         verify_password_error=verify_password_error)


@app.route("/newpost", methods=["POST", "GET"])
def new_post():
    
    owner = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        #access data from form in newpost.html
        blog_title = request.form["blog-title"]
        blog_body = request.form["blog-entry"]
        #sets errors to empty strings
        title_error = ""
        body_error = ""

        #errors
        if not blog_title:
            title_error = "Please enter a blog title!"
        if not blog_body:
            body_error = "Please write your blog!"

        if not body_error and not title_error:
            #sets data in database(Blog) to variable and adds/commits to database
            new_entry = Blog(blog_title, blog_body)     
            db.session.add(new_entry)
            db.session.commit()        
            #displays blog entries on individual URLs without having to create separate html files for each 
            return redirect("/blog?id={}".format(new_entry.id)) 
        else:
            #displays form with errors
            return render_template("newpost.html", title="New Entry", title_error=title_error, body_error=body_error, 
                blog_title=blog_title, blog_body=blog_body)
    
    return render_template("newpost.html", title="New Entry")


@app.route("/blog")
def blog():
    #returns information based on the database, query string
    blog_id = request.args.get("id")

    #if blog_id = None, queries all results in Blog database and calls blog.html form
    if blog_id == None:
        posts = Blog.query.all()
        return render_template("blog.html", posts=posts, title="Build a Blog")
    #queries specific blog_id and links to individual blog entries
    else:
        post = Blog.query.get(blog_id)
        return render_template("entry.html", post=post, title="Blog Entry")


@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/", methods=["POST", "GET"])
def index():
    owner = User.query.filter_by(username=session["username"]).first()

    if request.method == 'POST':
        blog_name = request.form['blog']
        new_blog = Blog(blog_name, owner)
        db.session.add(new_blog)
        db.session.commit()

    return render_template('blog.html',title="Blogz!")

if  __name__ == "__main__":
    app.run()


#<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
