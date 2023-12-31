from flask import Flask,render_template, request, session
from flask_mail import Mail
import datetime
from db import db
from models.contact import Contact 
from models.post import Posts 
import json

loacal_server = True
with open('config.json', "r") as c:
    params = json.load(c)['params']

app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '587',  
    MAIL_USE_TLS = True,
    MAIL_USERNAME = params['gmail_user'],
    MAIL_PASSWORD = params['gmail_password'],

)
mail = Mail(app)


if loacal_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db.init_app(app)

@app.route("/")
def home():
    post = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template("home.html", params=params, post=post)

@app.route("/about")
def about():
    return render_template("about.html", params=params)


@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            pass
    return render_template("edit.html", params=params)


@app.route("/dashboard", methods=['GET', 'POST'])
def dashbord():
    if ('user' in session and session['user'] == params['admin_user']):
        post =  Posts.query.all()
        return render_template('dashboard.html', params=params, post = post)


    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if (username == params['admin_user'] and userpass == params['admin_password']):
            session["user"] = username
            post =  Posts.query.all()
            return render_template('dashboard.html', params=params, post = post)

    return render_template("login.html", params=params)


@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method)=='POST':
        # Add entry to database
        name = request.form.get('name')
        phone = request.form.get('mobile')
        message = request.form.get('msg')
        email = request.form.get('email')

        entry = Contact(
            name=name, 
            phone_no=phone,
            date=datetime.datetime.now(),  
            message=message, 
            email=email
        )

        mail.send_message(
            "New message from " + name,
            sender=email,
            recipients = [params['gmail_user']],
            body= message + "\n" + phone            
            )

        db.session.add(entry)
        db.session.commit()

        
    return render_template("contact.html", params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post, p=True)

if __name__ == "__main__":
    app.run(debug=True)

