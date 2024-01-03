from flask import Flask,render_template, request, session, redirect
from flask_mail import Mail
import datetime
import os
import math
from werkzeug.utils import secure_filename
from db import db
from models.contact import Contacts 
from models.post import Post 
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



# home page route
@app.route("/")
def home():
    posts = Post.query.filter_by().all()
    last = math.ceil(len(posts)/int(params['no_of_post']))

    page = request.args.get('page')

    if (not str(page).isnumeric()):
        page = 1
    
    page = int(page)
    posts = posts[(page-1)*int(params['no_of_post']):(page-1)*int(params['no_of_post'])+ int(params['no_of_post'])]
    if page==1:
        prev = "#"
        next = "/?page="+ str(page+1)
    elif page==last:
        prev = "/?page="+ str(page-1)
        next = "#"
    else:
        prev = "/?page="+ str(page-1)
        next = "/?page="+ str(page+1)
    
    return render_template('new_home.html', params=params, posts=posts, prev=prev, next=next)






# edit page route
@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            box_title = request.form.get('title')
            sub_title = request.form.get('sub_title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img = request.form.get('img_file')
            date = datetime.datetime.now()

            if sno == "0":
                post = Post(title=box_title, sub_title=sub_title, slug=slug, content=content, img_file=img, date=date)
                db.session.add(post)
                db.session.commit()
                return redirect('/dashboard')
            else:
                post = Post.query.filter_by(sno=sno).first()
                post.title = box_title
                post.sub_title = sub_title
                post.slug = slug
                post.content = content
                post.img_file = img
                post.date = date
                db.session.commit()

                return redirect('/dashboard')
            
            
        post = Post.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, sno=sno)

    return render_template("edit.html", params=params)


# Upload page
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == 'POST':
            f = request.files['image']
            f.save(os.path.join(params['upload_location'], secure_filename(f.filename)))
            return "Uploaded"
        

# Delete page
@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Post.query.filter_by(sno=sno).first()
        db.session.delete(posts)
        db.session.commit()
        return redirect('/dashboard')



# logout
@app.route("/logout")
def log_out():
    session.pop('user')
    return redirect('/dashboard')



# dashboard page route
@app.route("/dashboard", methods=['GET', 'POST'])
def dashbord():
    if ('user' in session and session['user'] == params['admin_user']):
        post =  Post.query.all()
        return render_template('dashboard.html', params=params, post = post)


    if request.method == 'POST':
        username = request.form.get('uname')
        userpass = request.form.get('pass')

        if (username == params['admin_user'] and userpass == params['admin_password']):
            session["user"] = username
            post =  Post.query.all()
            return render_template('dashboard.html', params=params, post = post)

    return render_template("login.html", params=params)



# contact form route
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if (request.method)=='POST':
        # Add entry to database
        name = request.form.get('name')
        phone = request.form.get('mobile')
        message = request.form.get('msg')
        email = request.form.get('email')

        entry = Contacts(
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

        
    return render_template("new_home.html", params=params)



# post page route
@app.route("/post/<string:post_slug>", methods=['GET'])
def post(post_slug):
    post = Post.query.filter_by(slug=post_slug).first()
    return render_template("post.html", params=params, post=post, p=True)

if __name__ == "__main__":
    app.run(debug=True)

