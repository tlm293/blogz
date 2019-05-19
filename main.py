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
    allowed_routes = ["login", "signup", "blog", "index"]
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
            return redirect("/newpost")
        else:
            if not user:
                flash("User does not exist.", "error")
                return redirect ("/login")
            else:
                flash("User password incorrect.", "error")
                return redirect("/login")
    return render_template("login.html")
    

@app.route("/signup", methods=["POST", "GET"])
def signup():

    title="Validation"
    title2="Welcome"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        verify_password = request.form["verify_password"]
    
        if not username:
            flash("Please enter a username.", "error")
            return redirect("/signup")
        else:
            for char in username:
                if char.isspace():
                    flash("Username cannot contain a space.", "error")
                    return redirect("/signup")
                else:
                    if (len(username)<3) or (len(username)>20):
                        flash("Username needs to be at least 3 characters but less than 20 characters.", "error")
                        return redirect("/signup")
                    
        if not password:
            flash("Please enter a password.", "error")
            return redirect("/signup")
        else:
            for char in password:
                if char.isspace():
                    flash("Password cannot contain a space.", "error")
                    return redirect("/signup")
                else:
                    if (len(password) < 3) or (len(password) > 20):
                        flash("Password needs to be at least 3 characters but less than 20 characters.", "error")
                        return redirect("/signup")

        if not verify_password:
            flash("Please re-enter password.", "error")
            return redirect("/signup")
        else:
            if password != verify_password:
                flash("Passwords do not match.", "error")
                return redirect("/signup")

        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            return redirect("/newpost")
        else:
            flash("This username already exists.", "error")
            return redirect("/signup")

    return render_template("signup.html")

@app.route("/newpost", methods=["POST", "GET"])
def new_post():
    
    owner = User.query.filter_by(username=session["username"]).first()

    if request.method == "POST":
        #access data from form in newpost.html
        blog_title = request.form["blog-title"]
        blog_body = request.form["blog-entry"]
        
        #errors
        if not blog_title:
            flash("Please enter a blog title!", "error")
        else:
            if not blog_body:
                flash("Please write your blog!", "error")

            else:
                #sets data in database(Blog) to variable and adds/commits to database
                new_entry = Blog(blog_title, blog_body, owner)     
                db.session.add(new_entry)
                db.session.commit()        
                #displays blog entries on individual URLs without having to create separate html files for each 
                return redirect("/blog?id={}".format(new_entry.id)) 
    
    return render_template("newpost.html", title="New Entry")


@app.route("/blog")
def blog():
    #returns information based on the database, query string
    blog_id = request.args.get("id")
    user_id = request.args.get("user")
    posts = Blog.query.all()
    
    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template("entry.html", post=post, title="Blog Entry")
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template("user.html", posts=posts, owner_id=user_id)
    
    return render_template("blog.html", posts=posts)

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/blog")


@app.route("/")
def index():

    users = User.query.all()
    
    return render_template("index.html", users=users, title="Home")
    
    
    
    
    
    
    # user_id = request.args.get("user")
    
    # users = User.query.all()
    # if user_id:
    #     post = Blog.query.filter_by(owner_id=user_id).all()
    #     return render_template("user.html", post=post, owner_id=user_id)

    # return render_template("index.html", users=users, title="Home")

if  __name__ == "__main__":
    app.run()


#<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
