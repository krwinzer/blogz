from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pwd_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz2017@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True

db = SQLAlchemy(app)
app.secret_key = 'pm7yhu8#9thmkrw'

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
    username = db.Column(db.String(50), unique=True)
    pw_hash = db.Column(db.String(150))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pwd_hash(password)

@app.before_request
def require_login():
    allowed_routes = ['blogs_list', 'index', 'login', 'signup', 'single_post', 'user_posts']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods = ['POST', 'GET'])
def index():

    authors = User.query.all()
    return render_template('index.html', authors=authors)

@app.route('/new-post', methods=['POST', 'GET'])
def new_post():

    post_body = ''
    post_title = ''
    title_error = ''
    body_error = ''

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']

        if post_title == '':
            title_error = 'Please enter a Post Title.'
        elif post_body == '':
            body_error = 'Please enter some content.'
        else:
            new = Blog(post_title, post_body, owner)
            db.session.add(new)
            db.session.commit()

            return redirect('/single-post?id={0}'.format(new.id))

    return render_template('new-post.html', title="New Post", title_error=title_error,
                body_error=body_error, post_title=post_title, post_body=post_body)

@app.route('/blog', methods = ['POST','GET'])
def blogs_list():

    posts = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', posts=posts, users=users)

@app.route('/single-post', methods=['GET'])
def single_post():

    retrieved_id = request.args.get('id')
    post = Blog.query.get(retrieved_id)

    return render_template('single-post.html', title="Single Post", post=post)

@app.route('/user-posts', methods=['GET'])
def user_posts():

    user_id = request.args.get('id')
    posts = db.session.query(Blog).filter_by(owner_id=user_id).all()

    return render_template('user-posts.html', title="User Posts", posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():

        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                flash("Logged in")
                return redirect('/new-post')
            else:
                flash("User password incorrect, or user does not exist", 'error')

        return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

    # ------------Blank Fields ---------------

        if len(username) == 0:
            flash("The username field was left blank.", 'error')
        else:
            username = username
        if len(password) == 0:
            flash('The password field was left blank.', 'error')
        else:
            password = password
        if len(verify) == 0:
            flash('The verify password field was left blank.', 'error')
        else:
            verify = verify

    # --------Invalid Username, Password, username-------------

        if len(username) != 0:
            if len(username) < 4 or len(username) > 50 or ' ' in username:
                flash('username must be between 4 and 20 characters long and cannot contain spaces.', 'error')
                return render_template('/signup.html')
            else:
                username = username

        if len(password) != 0:
            if len(password) < 4 or len(password) > 150 or ' ' in password:
                flash("The password must be between 4 and 19 characters long and cannot contain spaces.", 'error')
                return render_template('/signup.html')
            else:
                password = password

    # --------Password and Verify Do Not Match----------

        if len(password) == len(verify):
            for char, letter in zip(password, verify):
                if char != letter:
                    flash('Passwords do not match.', 'error')
                    return render_template('signup.html')
                else:
                    verify = verify
                    password = password
        else:
            flash('Passwords do not match.', 'error')
            return render_template('signup.html')

        if username and password and verify:
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/new-post')
            else:
                #TODO - user better response messaging
                flash('Duplicate user.', 'error')
        else:
            return render_template('signup.html')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()
