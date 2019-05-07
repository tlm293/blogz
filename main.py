from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEGUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://build-a-blog:blog@localhost:8889/build-a-blog"
app.config["SQLALCHEMY_ECHO"] = True
db = SQLAlchemy(app)

#build a class 
class Blog(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    
    
    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route("/newpost", methods=["POST", "GET"])
def new_post():
    
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


@app.route("/")
def index():
    return redirect("/blog")

if  __name__ == "__main__":
    app.run()


#<link rel="stylesheet" type="text/css" href="{{ url_for('static', filename='css/style.css') }}">
