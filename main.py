from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz2017@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(120))
    post_body = db.Column(db.String(25000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.post_title = title
        self.post_body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

@app.route('/blog', methods = ['POST','GET'])
def index():

    posts = Blog.query.all()
    return render_template('blog.html', title="Build a Blog", posts=posts)

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    post_body = ''
    post_title = ''
    title_error = ''
    body_error = ''

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        if post_title == '':
            title_error = 'Please enter a Post Title.'
        elif post_body == '':
            body_error = 'Please enter some content.'
        else:
            new = Blog(post_title, post_body)
            db.session.add(new)
            db.session.commit()

            return redirect('/single-post?id={0}'.format(new.id))

    return render_template('new-post.html', title="New Post", title_error=title_error,
                body_error=body_error, post_title=post_title, post_body=post_body)

@app.route('/single-post', methods=['GET'])
def single_post():

    retrieved_id = request.args.get('id')
    posts = db.session.query(Blog.post_title, Blog.post_body).filter_by(id=retrieved_id)

    return render_template('single-post.html', title="Single Post", posts=posts)

if __name__ == '__main__':
    app.run()
